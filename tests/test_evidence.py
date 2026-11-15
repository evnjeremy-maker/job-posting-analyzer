import pytest

from job_posting_analyzer.errors import ResponseError
from job_posting_analyzer.evidence import requirement_map, validate_analysis
from job_posting_analyzer.models import (
    ComparisonItem,
    EvidenceItem,
    JobAnalysis,
    Overview,
    Profile,
    ProfileEvidence,
)


def job():
    return JobAnalysis(
        overview=Overview(),
        required=[EvidenceItem(text="Python", quote="Python required.")],
        preferred=[EvidenceItem(text="SQL", quote="SQL preferred.")],
        responsibilities=[],
        application_materials=[],
        ambiguities=[],
    )


def test_analysis_checks_every_quote_against_original_source():
    analysis = job()
    validate_analysis(analysis, "Python required. SQL preferred.")
    with pytest.raises(ResponseError, match="quote"):
        validate_analysis(analysis, "python required. SQL preferred.")


def test_requirement_ids_are_assigned_in_python_and_keep_preference():
    mapping = requirement_map(job())
    assert list(mapping) == ["r1", "p1"]
    assert mapping["p1"].text == "SQL"


def comparison():
    return [
        ComparisonItem(
            requirement_id="r1",
            status="partial",
            evidence=[ProfileEvidence(pointer="/skills/0", quote="Python basics")],
            explanation="Basic only",
        ),
        ComparisonItem(
            requirement_id="p1",
            status="missing",
            evidence=[ProfileEvidence(pointer="/explicitly_missing/0", quote="SQL")],
            explanation="Explicitly absent and preferred",
        ),
    ]


def test_comparison_requires_complete_ids_and_explicit_profile_evidence():
    from job_posting_analyzer.evidence import validate_comparison

    profile = Profile(skills=["Python basics"], explicitly_missing=["SQL"])
    validate_comparison(comparison(), job(), profile)
    with pytest.raises(ResponseError):
        validate_comparison(comparison()[:1], job(), profile)
    with pytest.raises(ResponseError):
        validate_comparison([comparison()[0], comparison()[0]], job(), profile)
    with pytest.raises(ResponseError):
        validate_comparison(comparison(), job(), Profile())


@pytest.mark.parametrize(
    "pointer", ["skills/0", "/skills/-1", "/skills/01", "/skills/9", "/skills"]
)
def test_invalid_profile_pointers_are_rejected(pointer):
    from job_posting_analyzer.evidence import validate_comparison

    items = comparison()
    items[0].evidence[0].pointer = pointer
    with pytest.raises(ResponseError):
        validate_comparison(
            items, job(), Profile(skills=["Python basics"], explicitly_missing=["SQL"])
        )


@pytest.mark.parametrize(
    "status,pointer,quote",
    [
        ("missing", "/skills/0", "Python basics"),
        ("matched", "/explicitly_missing/0", "SQL"),
        ("partial", "/explicitly_missing/0", "SQL"),
        ("matched", "/skills/0", "Invented project experience"),
    ],
)
def test_rejects_unsupported_status_evidence(status, pointer, quote):
    from job_posting_analyzer.evidence import validate_comparison

    items = comparison()
    items[0] = ComparisonItem(
        requirement_id="r1",
        status=status,
        evidence=[ProfileEvidence(pointer=pointer, quote=quote)],
        explanation="Simulated claim",
    )
    with pytest.raises(ResponseError):
        validate_comparison(
            items, job(), Profile(skills=["Python basics"], explicitly_missing=["SQL"])
        )


def test_omitted_skill_is_unclear_without_evidence():
    from job_posting_analyzer.evidence import validate_comparison

    items = [
        ComparisonItem(
            requirement_id=key,
            status="unclear",
            evidence=[],
            explanation="Profile provides no evidence",
        )
        for key in ("r1", "p1")
    ]
    validate_comparison(items, job(), Profile())
