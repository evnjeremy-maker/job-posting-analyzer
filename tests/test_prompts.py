import json
from pathlib import Path

from job_posting_analyzer.prompts import extraction_instructions

ROOT = Path(__file__).resolve().parents[1]


def test_few_shot_uses_development_examples_only():
    cases = json.loads((ROOT / "evaluation/cases.json").read_text(encoding="utf-8"))["cases"]
    instruction = extraction_instructions("few-shot")
    for case in cases:
        job = (ROOT / case["job_path"]).read_text(encoding="utf-8")
        assert (job in instruction) is (case["split"] == "development")
