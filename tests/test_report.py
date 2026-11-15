import importlib
from pathlib import Path
from uuid import uuid4

import pytest

from job_posting_analyzer.models import EvidenceItem, JobAnalysis, Overview, Report


@pytest.fixture
def work_path():
    root = Path(__file__).resolve().parents[1] / ".cache/report-tests" / uuid4().hex
    root.mkdir(parents=True)
    return root


def sample_report():
    return Report(
        analysis=JobAnalysis(
            overview=Overview(title=EvidenceItem(text="AI Intern", quote="AI Intern")),
            required=[EvidenceItem(text="Python", quote="Python experience required.")],
            preferred=[],
            responsibilities=[],
            application_materials=[],
            ambiguities=[],
        ),
        provider="simulated",
        model="fictional-response",
        prompt="zero-shot",
        simulated=True,
    )


def test_terminal_text_escapes_controls_but_preserves_unicode():
    report = importlib.import_module("job_posting_analyzer.report")
    assert report.terminal_text("Résumé\x1b[31m\nnext") == "Résumé\\x1b[31m\\nnext"


def test_render_shows_missing_information_evidence_and_simulation():
    report = importlib.import_module("job_posting_analyzer.report")
    rendered = report.render_report(sample_report())
    assert "SIMULATED" in rendered
    assert "Salary: Not provided" in rendered
    assert "Python experience required." in rendered
    assert "Required qualifications" in rendered


def test_json_write_round_trips_and_never_overwrites_by_default(work_path):
    from job_posting_analyzer.errors import OutputError

    report = importlib.import_module("job_posting_analyzer.report")
    path = work_path / "report.json"
    expected = sample_report()
    report.write_report(expected, path)
    assert Report.model_validate_json(path.read_text(encoding="utf-8")) == expected
    with pytest.raises(OutputError):
        report.write_report(expected, path)
    assert Report.model_validate_json(path.read_text(encoding="utf-8")) == expected


def test_failed_overwrite_preserves_existing_file(monkeypatch, tmp_path):
    from job_posting_analyzer import report
    from job_posting_analyzer.errors import OutputError

    target = tmp_path / "existing.json"
    target.write_text("Original fictional content", encoding="utf-8")

    def denied(*args):
        raise PermissionError("Controlled replacement failure")

    monkeypatch.setattr(report.os, "replace", denied)
    with pytest.raises(OutputError):
        report.write_report(sample_report(), target, overwrite=True)
    assert target.read_text(encoding="utf-8") == "Original fictional content"
    assert list(tmp_path.glob(".job-report-*")) == []


def test_report_with_mutated_invalid_data_is_not_saved(tmp_path):
    from job_posting_analyzer import report
    from job_posting_analyzer.errors import ResponseError

    value = sample_report()
    value.analysis.required[0].quote = ""
    target = tmp_path / "invalid.json"
    with pytest.raises(ResponseError):
        report.write_report(value, target)
    assert not target.exists()


def test_render_displays_working_hours_and_escapes_claim_controls():
    from job_posting_analyzer import report

    value = sample_report()
    value.analysis.overview.working_hours = EvidenceItem(
        text="20 hours/week", quote="20 hours/week"
    )
    value.analysis.required[0].text = "Python\x1b[31m"
    rendered = report.render_report(value)
    assert "Working hours: 20 hours/week" in rendered
    assert "\\x1b" in rendered
    assert "\x1b" not in rendered
