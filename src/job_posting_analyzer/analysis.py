"""Validate each analysis stage before advancing to the next."""

from pydantic import TypeAdapter, ValidationError

from .errors import InputError, ProviderError, ResponseError
from .evidence import validate_analysis, validate_comparison
from .models import ComparisonItem, JobAnalysis, Profile, Report


def analyze(text, profile=None, provider=None, prompt_variant="zero-shot", simulated=False):
    if not isinstance(text, str) or not text.strip() or len(text.encode("utf-8")) > 65536:
        raise InputError("Advertisement must be nonblank UTF-8 text no larger than 64 KiB.")
    if profile is not None:
        try:
            profile = Profile.model_validate(profile)
        except ValidationError:
            raise InputError("Invalid profile schema.") from None
    if provider is None:
        from .gemini import GeminiProvider

        provider = GeminiProvider()
    try:
        analysis = JobAnalysis.model_validate(provider.extract(text, prompt_variant))
        validate_analysis(analysis, text)
    except ValidationError:
        raise ResponseError("Extraction response has an invalid schema.") from None
    except ProviderError as error:
        raise ProviderError(f"Extraction failed: {error}", terminal=error.terminal) from None
    except ResponseError as error:
        raise ResponseError(f"Extraction validation failed: {error}") from None
    extraction_usage = getattr(provider, "last_usage", None)
    comparison = None
    if profile is not None:
        try:
            comparison = TypeAdapter(list[ComparisonItem]).validate_python(
                provider.compare(text, analysis, profile)
            )
            validate_comparison(comparison, analysis, profile)
        except ValidationError:
            raise ResponseError("Comparison response has an invalid schema.") from None
        except ProviderError as error:
            raise ProviderError(f"Comparison failed: {error}", terminal=error.terminal) from None
        except ResponseError as error:
            raise ResponseError(f"Comparison validation failed: {error}") from None
    usage = extraction_usage
    if comparison is not None and extraction_usage is not None:
        other = getattr(provider, "last_usage", None)
        usage = (
            None
            if other is None
            else {
                key: (None if value is None or other.get(key) is None else value + other[key])
                for key, value in extraction_usage.items()
            }
        )
    return Report(
        analysis=analysis,
        comparison=comparison,
        provider="simulated" if simulated else "gemini",
        model=getattr(provider, "model", "simulated" if simulated else "gemini-3.1-flash-lite"),
        prompt=prompt_variant,
        simulated=simulated,
        usage=usage,
        portfolio_availability=profile.portfolio if profile is not None else None,
    )
