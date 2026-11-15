import pytest
from pydantic import ValidationError

from job_posting_analyzer.models import EvidenceItem, JobAnalysis, Overview, Profile, Report


def test_evidence_rejects_blank_quote_and_unexpected_fields():
    with pytest.raises(ValidationError):
        EvidenceItem(text="Python", quote=" ")
    with pytest.raises(ValidationError):
        EvidenceItem(text="Python", quote="Python", confidence=0.8)


def test_profile_is_optional_self_reported_information():
    profile = Profile(skills=["Python basics"], explicitly_missing=["SQL"], portfolio="GitHub")
    assert profile.education == []
    assert profile.skills == ["Python basics"]
    assert profile.explicitly_missing == ["SQL"]


def test_analysis_preserves_nullable_overview_and_distinct_categories():
    analysis = JobAnalysis(
        overview=Overview(),
        required=[],
        preferred=[],
        responsibilities=[],
        application_materials=[],
        ambiguities=[],
    )
    assert analysis.overview.salary is None
    assert analysis.required == []


def test_report_accepts_explicit_self_reported_portfolio_availability():
    report = Report(
        analysis=JobAnalysis(
            overview=Overview(),
            required=[],
            preferred=[],
            responsibilities=[],
            application_materials=[],
            ambiguities=[],
        ),
        provider="simulated",
        model="fixture",
        prompt="zero-shot",
        simulated=True,
        portfolio_availability="GitHub portfolio available",
    )
    assert report.portfolio_availability == "GitHub portfolio available"


@pytest.mark.parametrize("data", [{"skills": [12]}, {"unknown": []}, {"skills": [" "]}])
def test_profile_rejects_coercion_and_unrecognized_data(data):
    with pytest.raises(ValidationError):
        Profile.model_validate(data)


def test_missing_analysis_categories_are_invalid():
    with pytest.raises(ValidationError):
        JobAnalysis.model_validate({"overview": {}})
