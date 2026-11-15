import socket

import pytest

import job_posting_analyzer.evaluation as evaluation
from job_posting_analyzer.errors import InputError, ProviderError
from job_posting_analyzer.evaluation import run_evaluation, score_extraction


def test_classification_error_is_not_counted_as_correct():
    expected = {"required": [{"text": "Python", "quote": "Python is required."}]}
    actual = {"preferred": [{"text": "Python", "quote": "Python is required."}]}
    result = score_extraction(actual, expected)
    assert result["correct_items"] == 0
    assert result["classification_errors"] == 1
    assert result["omitted_items"] == 1
    assert result["unsupported_items"] == 1


def test_offline_evaluation_is_simulated_and_excludes_development(monkeypatch):
    def deny_network(*args, **kwargs):
        raise AssertionError("Offline evaluation attempted network access")

    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(evaluation, "_new_provider", deny_network)
    result = run_evaluation()
    assert result["simulated"] is True
    assert result["model_accuracy_measured"] is False
    assert result["case_count"] == 6
    assert result["planned_extractions"] == 12
    assert result["failed_extractions"] == 0
    assert {item["variant"] for item in result["results"]} == {"zero-shot", "few-shot"}
    assert {item["split"] for item in result["results"]} == {"validation", "holdout"}
    assert all(item["usage"] is None for item in result["results"])
    assert all(item["response_seconds"] is None for item in result["results"])


def test_classification_errors_do_not_reuse_one_expected_item():
    expected = {"required": [{"text": "Python"}]}
    actual = {"preferred": [{"text": "Python"}], "responsibilities": [{"text": "Python"}]}
    assert score_extraction(actual, expected)["classification_errors"] == 1


def test_wrong_interpretation_remains_visible_as_failed_case(monkeypatch):
    original = evaluation.JobAnalysis.model_validate

    def incorrect(raw):
        analysis = original(raw)
        wrong = analysis.model_copy(deep=True)
        wrong.preferred.extend(wrong.required)
        wrong.required.clear()
        return wrong

    monkeypatch.setattr(evaluation.JobAnalysis, "model_validate", incorrect)
    result = run_evaluation(split="holdout")
    assert result["failed_extractions"] == 0
    assert len(result["failed_cases"]) == 6
    assert all(record["exact_match"] is False for record in result["results"])


def test_failed_calls_and_request_budget_stay_in_denominator(monkeypatch):
    class FailingProvider:
        model = "fictional-test-provider"
        attempts_used = 0
        last_usage = None

        def extract(self, text, variant):
            self.attempts_used += 1
            raise ProviderError("PRIVATE API KEY VALUE")

    provider = FailingProvider()
    monkeypatch.setattr(evaluation, "_new_provider", lambda: provider)
    result = run_evaluation(live=True, max_requests=1)
    assert provider.attempts_used == 1
    assert result["planned_extractions"] == 12
    assert result["failed_extractions"] == 12
    assert "PRIVATE" not in str(result)
    assert isinstance(result["results"][0]["response_seconds"], float)
    assert result["results"][1]["response_seconds"] is None


def test_terminal_quota_stops_subsequent_requests(monkeypatch):
    class QuotaProvider:
        model = "fictional-test-provider"
        attempts_used = 0
        last_usage = None

        def extract(self, text, variant):
            self.attempts_used += 1
            raise ProviderError("Quota exhausted", terminal=True)

    provider = QuotaProvider()
    monkeypatch.setattr(evaluation, "_new_provider", lambda: provider)
    result = run_evaluation(live=True)
    assert provider.attempts_used == 1
    assert result["failed_extractions"] == 12
    assert result["logical_requests"] == 1


def test_missing_fixtures_fail_before_provider_creation(monkeypatch):
    monkeypatch.setattr(evaluation, "ROOT", evaluation.ROOT / "examples")
    with pytest.raises(InputError, match="Evaluation fixtures"):
        run_evaluation()


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_invalid_request_limit_is_rejected(limit):
    with pytest.raises(InputError, match="positive integer"):
        run_evaluation(max_requests=limit)


def test_invalid_split_is_rejected():
    with pytest.raises(InputError, match="split"):
        run_evaluation(split="development")


@pytest.mark.parametrize("invalid", ["format", "quote"])
def test_invalid_responses_are_failed_and_retained(monkeypatch, invalid):
    expected = evaluation.load_cases("holdout")[0]["expected"].model_dump()

    class InvalidProvider:
        model = "fictional-test-provider"
        attempts_used = 0
        last_usage = None

        def extract(self, text, variant):
            self.attempts_used += 1
            if invalid == "format":
                return {"unexpected": "PRIVATE RESPONSE"}
            expected["required"][0]["quote"] = "QUOTE NOT IN SOURCE"
            return expected

    monkeypatch.setattr(evaluation, "_new_provider", InvalidProvider)
    result = run_evaluation(live=True, split="holdout", max_requests=1)
    first = result["results"][0]
    assert first["failed"] is True
    assert first["format_valid"] is (invalid == "quote")
    if invalid == "quote":
        assert first["quotes"]["invalid"] == 1
    assert result["planned_extractions"] == 6
    assert result["failed_extractions"] == 6
    assert len(result["failed_cases"]) == 6
    assert "PRIVATE RESPONSE" not in str(result)
