import pytest
from pydantic import ValidationError


def test_explicit_working_hours_has_verified_evidence():
    from job_posting_analyzer.evidence import validate_analysis
    from job_posting_analyzer.models import JobAnalysis

    data = dict(
        overview={"working_hours": {"text": "20 hours weekly", "quote": "20 hours weekly"}},
        required=[],
        preferred=[],
        responsibilities=[],
        application_materials=[],
        ambiguities=[],
    )
    try:
        analysis = JobAnalysis.model_validate(data)
    except ValidationError as error:
        pytest.fail(f"Working-hours schema missing: {error.error_count()} validation errors")
    validate_analysis(analysis, "Work 20 hours weekly.")
    assert analysis.overview.working_hours.text == "20 hours weekly"
