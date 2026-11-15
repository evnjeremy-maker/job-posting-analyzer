"""Check evidence existence; semantic interpretation is evaluated separately."""

from .errors import ResponseError
from .models import ComparisonItem, EvidenceItem, JobAnalysis, Profile


def require_quote(source: str, quote: str) -> None:
    if not quote.strip() or quote not in source:
        raise ResponseError("Supporting quote is absent from source.")


def validate_analysis(analysis: JobAnalysis, source: str) -> None:
    for field in type(analysis.overview).model_fields:
        item = getattr(analysis.overview, field)
        if item is not None:
            require_quote(source, item.quote)
    for name in ("required", "preferred", "responsibilities", "application_materials"):
        for item in getattr(analysis, name):
            require_quote(source, item.quote)
    for ambiguity in analysis.ambiguities:
        for quote in ambiguity.quotes:
            require_quote(source, quote)


def requirement_map(analysis: JobAnalysis) -> dict[str, EvidenceItem]:
    return {
        **{f"r{index}": item for index, item in enumerate(analysis.required, 1)},
        **{f"p{index}": item for index, item in enumerate(analysis.preferred, 1)},
    }


def _profile_string(profile: Profile, pointer: str) -> str:
    if not pointer.startswith("/"):
        raise ResponseError("Profile evidence pointer is invalid.")
    current = profile.model_dump()
    try:
        for token in pointer[1:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict):
                current = current[token]
            elif isinstance(current, list):
                if (
                    not token.isascii()
                    or not token.isdecimal()
                    or (len(token) != 1 and token.startswith("0"))
                ):
                    raise ValueError("Invalid array index")
                current = current[int(token)]
            else:
                raise ValueError("Not a container")
    except (KeyError, IndexError, ValueError):
        raise ResponseError("Profile evidence pointer does not identify a string.") from None
    if not isinstance(current, str):
        raise ResponseError("Profile evidence pointer does not identify a string.")
    return current


def validate_comparison(
    items: list[ComparisonItem], analysis: JobAnalysis, profile: Profile
) -> None:
    identifiers = [item.requirement_id for item in items]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(
        requirement_map(analysis)
    ):
        raise ResponseError("Comparison must cover every qualification exactly once.")
    for item in items:
        if item.status != "unclear" and not item.evidence:
            raise ResponseError("Comparison status requires explicit profile evidence.")
        for evidence in item.evidence:
            require_quote(_profile_string(profile, evidence.pointer), evidence.quote)
            negative = evidence.pointer.startswith("/explicitly_missing/")
            if item.status == "missing" and not negative:
                raise ResponseError("Missing status requires an explicit lack in the profile.")
            if item.status in {"matched", "partial"} and negative:
                raise ResponseError("Positive matches cannot use explicit lack as evidence.")
