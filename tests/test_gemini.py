import pytest


def fake_client(response):
    from types import SimpleNamespace

    class Models:
        calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1
            assert kwargs["config"].tools is None
            if isinstance(response, Exception):
                raise response
            return response

    return SimpleNamespace(models=Models())


def test_valid_structured_response():
    import json
    from types import SimpleNamespace

    from job_posting_analyzer.gemini import GeminiProvider

    data = dict(
        overview={},
        required=[],
        preferred=[],
        responsibilities=[],
        application_materials=[],
        ambiguities=[],
    )
    response = SimpleNamespace(
        candidates=[SimpleNamespace(finish_reason="STOP")],
        text=json.dumps(data),
        usage_metadata=None,
    )
    provider = GeminiProvider(client=fake_client(response))
    assert provider.extract("Fictional role", "zero-shot").required == []
    assert provider.attempts_used == 1


@pytest.mark.parametrize(
    "reason,text", [("MAX_TOKENS", "{}"), ("SAFETY", "{}"), ("STOP", "not JSON")]
)
def test_invalid_responses_fail(reason, text):
    from types import SimpleNamespace

    from job_posting_analyzer.errors import ResponseError
    from job_posting_analyzer.gemini import GeminiProvider

    response = SimpleNamespace(candidates=[SimpleNamespace(finish_reason=reason)], text=text)
    with pytest.raises(ResponseError):
        GeminiProvider(client=fake_client(response)).extract("Fictional", "zero-shot")


def test_retry_and_attempt_budget(monkeypatch):
    from google.genai.errors import ServerError

    from job_posting_analyzer import gemini
    from job_posting_analyzer.errors import ProviderError

    monkeypatch.setattr(gemini.time, "sleep", lambda _: None)
    client = fake_client(ServerError(503, {"message": "PRIVATE error"}))
    provider = gemini.GeminiProvider(client=client, max_attempts=2)
    with pytest.raises(ProviderError):
        provider.extract("Fictional", "zero-shot")
    assert provider.attempts_used == 2
    assert client.models.calls == 2


def test_provider_missing_key_does_not_create_client(monkeypatch):
    from job_posting_analyzer.errors import InputError
    from job_posting_analyzer.gemini import GeminiProvider

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider()
    with pytest.raises(InputError, match="GEMINI_API_KEY"):
        provider.extract("fictional job", "zero-shot")


def test_auth_failure_is_not_retried_or_disclosed():
    from google.genai.errors import ClientError

    from job_posting_analyzer.errors import ProviderError
    from job_posting_analyzer.gemini import GeminiProvider

    client = fake_client(ClientError(401, {"message": "PRIVATE authentication details"}))
    with pytest.raises(ProviderError) as error:
        GeminiProvider(client=client).extract("Fictional", "zero-shot")
    assert client.models.calls == 1
    assert "PRIVATE" not in str(error.value)


def test_client_configuration_keeps_endpoint_timeout_and_single_sdk_attempt(monkeypatch):
    import json
    from types import SimpleNamespace

    from google import genai

    from job_posting_analyzer.gemini import GeminiProvider

    response = SimpleNamespace(
        candidates=[SimpleNamespace(finish_reason="STOP")],
        text=json.dumps(
            dict(
                overview={},
                required=[],
                preferred=[],
                responsibilities=[],
                application_materials=[],
                ambiguities=[],
            )
        ),
        usage_metadata=None,
    )
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return fake_client(response)

    monkeypatch.setenv("GEMINI_API_KEY", "fictional-test-credential-not-live")
    monkeypatch.setattr(genai, "Client", factory)
    GeminiProvider().extract("Fictional role", "zero-shot")
    assert captured["vertexai"] is False
    assert captured["http_options"].base_url == "https://generativelanguage.googleapis.com"
    assert captured["http_options"].timeout == 30000
    assert captured["http_options"].retry_options.attempts == 1


def test_missing_candidate_metadata_fails_cleanly():
    from types import SimpleNamespace

    from job_posting_analyzer.errors import ResponseError
    from job_posting_analyzer.gemini import GeminiProvider

    with pytest.raises(ResponseError):
        GeminiProvider(
            client=fake_client(SimpleNamespace(candidates=[SimpleNamespace()], text="{}"))
        ).extract("Fictional", "zero-shot")
