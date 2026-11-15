"""Repeatable extraction comparison with explicitly simulated offline results."""

import json
from collections import Counter
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from .errors import InputError, ProviderError, ResponseError
from .evidence import validate_analysis
from .models import JobAnalysis

CATEGORIES = ("required", "preferred", "responsibilities", "application_materials", "ambiguities")
ROOT = Path(__file__).resolve().parents[2]
VARIANTS = ("zero-shot", "few-shot")


def _atoms(analysis):
    atoms = []
    for field, value in analysis.get("overview", {}).items():
        if value is not None:
            atoms.append((f"overview.{field}", " ".join(value["text"].split()).casefold()))
    for category in CATEGORIES:
        atoms.extend(
            (category, " ".join(item["text"].split()).casefold())
            for item in analysis.get(category, [])
        )
    return Counter(atoms)


def score_extraction(actual, expected):
    predicted = _atoms(actual)
    wanted = _atoms(expected)
    correct = predicted & wanted
    extra = predicted - wanted
    missing = wanted - predicted
    extra_texts = Counter()
    missing_texts = Counter()
    for (_, text), count in extra.items():
        extra_texts[text] += count
    for (_, text), count in missing.items():
        missing_texts[text] += count
    errors = (extra_texts & missing_texts).total()
    return {
        "expected_items": wanted.total(),
        "predicted_items": predicted.total(),
        "correct_items": correct.total(),
        "omitted_items": missing.total(),
        "unsupported_items": extra.total(),
        "classification_errors": errors,
        "omitted": [
            {"category": cat, "text": text, "count": n} for (cat, text), n in missing.items()
        ],
        "unsupported": [
            {"category": cat, "text": text, "count": n} for (cat, text), n in extra.items()
        ],
    }


def _data_file(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise InputError("Evaluation fixture path escapes the repository.")
    return path


def load_cases(split="all"):
    if split not in {"all", "validation", "holdout"}:
        raise InputError("Evaluation split must be all, validation, or holdout.")
    try:
        return _load_cases(split)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, ResponseError) as error:
        raise InputError("Evaluation fixtures are missing or invalid.") from error


def _load_cases(split):
    manifest = json.loads((ROOT / "evaluation/cases.json").read_text(encoding="utf-8"))
    cases = []
    for case in manifest["cases"]:
        if case["split"] not in ({"validation", "holdout"} if split == "all" else {split}):
            continue
        source = _data_file(case["job_path"]).read_text(encoding="utf-8")
        expected = JobAnalysis.model_validate_json(
            _data_file(case["expected_path"]).read_text(encoding="utf-8")
        )
        validate_analysis(expected, source)
        cases.append({**case, "source": source, "expected": expected})
    return cases


def _quote_counts(analysis, source):
    payload = analysis.model_dump()
    quotes = [item["quote"] for item in payload["overview"].values() if item is not None]
    for category in CATEGORIES:
        for item in payload[category]:
            quotes.extend(item["quotes"] if category == "ambiguities" else [item["quote"]])
    valid = sum(bool(quote.strip()) and quote in source for quote in quotes)
    return {"total": len(quotes), "valid": valid, "invalid": len(quotes) - valid}


def _new_provider():
    from .gemini import GeminiProvider

    return GeminiProvider(max_attempts=24)


def run_evaluation(live=False, split="all", max_requests=12):
    if type(max_requests) is not int or max_requests < 1:
        raise InputError("max_requests must be a positive integer.")
    cases = load_cases(split)
    provider = _new_provider() if live else None
    records = []
    requests = 0
    terminal_failure = False
    for case in cases:
        for variant in VARIANTS:
            record = {
                "case_id": case["id"],
                "split": case["split"],
                "variant": variant,
                "simulated": not live,
                "model": provider.model if live else "simulated-fixture-replay",
                "response_seconds": None,
                "processing_seconds": None,
                "usage": None,
                "format_valid": False,
                "quotes": None,
                "metrics": None,
                "failed": True,
                "exact_match": False,
                "error": None,
            }
            started = perf_counter()
            requested = False
            try:
                if live:
                    if terminal_failure:
                        raise ProviderError("Evaluation halted after a terminal provider failure.")
                    if requests == max_requests:
                        raise ProviderError("Evaluation logical request limit reached.")
                    requests += 1
                    requested = True
                    raw = provider.extract(case["source"], variant)
                    record["response_seconds"] = perf_counter() - started
                    record["usage"] = provider.last_usage
                else:
                    raw = case["expected"].model_dump()
                actual = JobAnalysis.model_validate(raw)
                record["format_valid"] = True
                record["quotes"] = _quote_counts(actual, case["source"])
                record["metrics"] = score_extraction(
                    actual.model_dump(), case["expected"].model_dump()
                )
                validate_analysis(actual, case["source"])
                record["failed"] = False
                record["exact_match"] = (
                    record["metrics"]["omitted_items"] == 0
                    and record["metrics"]["unsupported_items"] == 0
                )
            except (InputError, ProviderError, ResponseError, ValidationError) as error:
                record["error"] = type(error).__name__
                if getattr(error, "terminal", False) or isinstance(error, InputError):
                    terminal_failure = True
            if requested and record["response_seconds"] is None:
                record["response_seconds"] = perf_counter() - started
            record["processing_seconds"] = perf_counter() - started
            records.append(record)
    return {
        "schema_version": "1.0",
        "simulated": not live,
        "model_accuracy_measured": bool(live),
        "scoring": "Casefolded whitespace-normalized exact category/text matching; "
        "equivalent paraphrases can be counted as errors. Classification errors overlap "
        "with omission/unsupported counts; do not add those counts together. Unsupported "
        "means absent from expected labels, not proven hallucination; inspect the case details.",
        "label_provenance": "Agent-authored labels; independently agent-reviewed; no human review.",
        "case_count": len(cases),
        "planned_extractions": len(records),
        "logical_requests": requests,
        "http_attempts": getattr(provider, "attempts_used", None) if live else 0,
        "http_attempt_limit": 24 if live else 0,
        "failed_extractions": sum(record["failed"] for record in records),
        "failed_cases": [
            {"case_id": record["case_id"], "variant": record["variant"]}
            for record in records
            if record["failed"] or not record["exact_match"]
        ],
        "results": records,
    }
