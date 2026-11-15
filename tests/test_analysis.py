import pytest


def test_invalid_extraction_never_reaches_comparison():
    from job_posting_analyzer.analysis import analyze
    from job_posting_analyzer.errors import ResponseError
    from job_posting_analyzer.models import Profile

    class Provider:
        def extract(self, text, variant):
            return dict(
                overview={},
                required=[dict(text="Python", quote="absent")],
                preferred=[],
                responsibilities=[],
                application_materials=[],
                ambiguities=[],
            )

        def compare(self, *args):
            pytest.fail("Comparison must not run on invalid extraction")

    with pytest.raises(ResponseError):
        analyze("Fictional job", profile=Profile(), provider=Provider(), simulated=True)


def test_comparison_provider_failure_identifies_stage():
    from job_posting_analyzer.analysis import analyze
    from job_posting_analyzer.errors import ProviderError
    from job_posting_analyzer.models import Profile

    class Provider:
        def extract(self, text, variant):
            return dict(
                overview={},
                required=[],
                preferred=[],
                responsibilities=[],
                application_materials=[],
                ambiguities=[],
            )

        def compare(self, *args):
            raise ProviderError("Provider request failed.")

    with pytest.raises(ProviderError, match="Comparison failed"):
        analyze("Fictional job", profile=Profile(), provider=Provider(), simulated=True)
