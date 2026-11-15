"""Readable terminal reports and validated JSON output."""

import os
import tempfile
import unicodedata
from pathlib import Path

from pydantic import ValidationError

from .errors import OutputError, ResponseError
from .inputs import preflight_output
from .models import Report


def terminal_text(value: str) -> str:
    return "".join(
        character.encode("unicode_escape").decode("ascii")
        if unicodedata.category(character) in {"Cc", "Cf"}
        else character
        for character in value
    )


def render_report(report: Report) -> str:
    lines = [
        "SIMULATED DEMONSTRATION — no live API results" if report.simulated else "Job analysis",
        f"Provider: {terminal_text(report.provider)} | Model: {terminal_text(report.model)}",
        f"Prompt: {terminal_text(report.prompt)}",
        "",
        "Job overview",
    ]
    for name in type(report.analysis.overview).model_fields:
        item = getattr(report.analysis.overview, name)
        label = name.replace("_", " ").capitalize()
        lines.append(f"{label}: {terminal_text(item.text) if item else 'Not provided'}")
        if item:
            lines.append(f"  Source: {terminal_text(item.quote)}")
    for name, label in (
        ("required", "Required qualifications"),
        ("preferred", "Preferred qualifications"),
        ("responsibilities", "Responsibilities"),
        ("application_materials", "Application materials"),
    ):
        lines.extend(["", label])
        items = getattr(report.analysis, name)
        if not items:
            lines.append("Not provided")
        for item in items:
            lines.extend(
                [f"- {terminal_text(item.text)}", f"  Source: {terminal_text(item.quote)}"]
            )
    lines.extend(["", "Ambiguous or conflicting information"])
    if not report.analysis.ambiguities:
        lines.append("None identified; this does not guarantee that the advertisement is complete.")
    for item in report.analysis.ambiguities:
        lines.append(f"- {terminal_text(item.text)}")
        lines.extend(f"  Source: {terminal_text(quote)}" for quote in item.quotes)
    if report.comparison is not None:
        from .evidence import requirement_map

        requirements = requirement_map(report.analysis)
        lines.extend(["", "Profile comparison — self-reported, not independently verified"])
        for item in report.comparison:
            requirement = requirements[item.requirement_id]
            category = "required" if item.requirement_id.startswith("r") else "preferred"
            lines.append(
                f"- {terminal_text(requirement.text)} ({category}): {item.status.capitalize()}"
            )
            lines.append(f"  {terminal_text(item.explanation)}")
            lines.extend(
                f"  Profile {terminal_text(evidence.pointer)}: {terminal_text(evidence.quote)}"
                for evidence in item.evidence
            )
        portfolio = getattr(report, "portfolio_availability", None)
        lines.append(
            "Portfolio availability: "
            + (terminal_text(portfolio) if portfolio else "Not provided")
            + "; quality has not been assessed."
        )
    lines.extend(
        ["", "Exact quotes verify text presence, not the correctness of its interpretation."]
    )
    return "\n".join(lines)


def write_report(report: Report, path: str | Path, overwrite: bool = False) -> None:
    try:
        validated = Report.model_validate(report.model_dump())
        payload = validated.model_dump_json(indent=2) + "\n"
    except (ValidationError, TypeError, ValueError):
        raise ResponseError("Report does not match the expected output schema.") from None
    preflight_output(path, overwrite=overwrite)
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent, prefix=".job-report-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        preflight_output(target, overwrite=overwrite)
        if overwrite:
            os.replace(temporary, target)
        elif os.name == "nt":
            os.rename(temporary, target)
        else:
            # A hard link creates the destination atomically without replacing a raced-in file.
            os.link(temporary, target)
    except (OSError, ValueError):
        raise OutputError(
            "Validated report could not be written; existing output was preserved."
        ) from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
