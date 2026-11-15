"""Fictional, explicitly simulated responses for the offline demonstration."""

from .models import ComparisonItem, EvidenceItem, JobAnalysis, Overview, Profile, ProfileEvidence

JOB_TEXT = (
    "We are hiring an AI Engineer Intern. Applicants must be university students with Python "
    "and Git experience. SQL knowledge is preferred. You will help build applications using "
    "language models. Include a GitHub portfolio with your application."
)

PROFILE_DATA = {
    "education": ["Computer Science university student."],
    "skills": ["Python basics", "Git for personal projects"],
    "projects": ["Personal Python practice projects"],
    "experience": [],
    "preferences": [],
    "explicitly_missing": ["SQL"],
    "portfolio": "GitHub portfolio available (self-reported)",
}


class SimulatedProvider:
    model = "fictional-fixture"
    last_usage = None

    def extract(self, text, variant):
        if text != JOB_TEXT:
            raise ValueError(
                "This simulated provider accepts only the fictional demo advertisement."
            )
        required_quote = "Applicants must be university students with Python and Git experience."
        return JobAnalysis(
            overview=Overview(
                title=EvidenceItem(text="AI Engineer Intern", quote="AI Engineer Intern")
            ),
            required=[
                EvidenceItem(text=label, quote=required_quote)
                for label in ("University student status", "Python experience", "Git experience")
            ],
            preferred=[EvidenceItem(text="SQL knowledge", quote="SQL knowledge is preferred.")],
            responsibilities=[
                EvidenceItem(
                    text="Build applications using language models",
                    quote="You will help build applications using language models.",
                )
            ],
            application_materials=[
                EvidenceItem(
                    text="GitHub portfolio",
                    quote="Include a GitHub portfolio with your application.",
                )
            ],
            ambiguities=[],
        )

    def compare(self, text, analysis, profile):
        facts = [
            (
                "r1",
                "matched",
                "/education/0",
                "Computer Science university student.",
                "The profile explicitly states university student status.",
            ),
            (
                "r2",
                "partial",
                "/skills/0",
                "Python basics",
                "Only basic Python is stated; the employer's expected level remains unclear.",
            ),
            (
                "r3",
                "matched",
                "/skills/1",
                "Git for personal projects",
                "The profile explicitly reports using Git for personal projects.",
            ),
            (
                "p1",
                "missing",
                "/explicitly_missing/0",
                "SQL",
                "SQL is explicitly listed as not learned; it is preferred, not mandatory.",
            ),
        ]
        return [
            ComparisonItem(
                requirement_id=identifier,
                status=status,
                evidence=[ProfileEvidence(pointer=pointer, quote=quote)],
                explanation=explanation,
            )
            for identifier, status, pointer, quote, explanation in facts
        ]


def run_demo():
    from .analysis import analyze

    return analyze(
        JOB_TEXT,
        profile=Profile.model_validate(PROFILE_DATA),
        provider=SimulatedProvider(),
        simulated=True,
    )
