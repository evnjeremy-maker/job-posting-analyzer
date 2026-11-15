# AI Job Posting Analyzer

Python terminal application that extracts evidence-backed job requirements and optionally compares a self-reported profile. It organizes evidence; it does not predict hiring outcomes. Extraction and profile comparison were verified against Gemini on fictional inputs; measured limitations are documented below.

## Bootstrap

Requires Python 3.12. On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe scripts/verify.py
```

On Linux, use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

Run these commands from the cloned repository. Few-shot prompts and evaluation require its fixture assets and an editable (`-e`) source checkout; a standalone wheel without those assets is not supported. Redirected CLI output uses UTF-8.

The verification command runs Ruff and offline pytest tests. It requires no API key and makes no Gemini requests. Windows and Linux GitHub CI checks passed for the live-verified implementation: [observed workflow run](https://github.com/evnjeremy-maker/job-posting-analyzer/actions/runs/43734746690).

## Current state

The application, fictional demonstration, validation, and offline evaluation are implemented. See [progress](docs/progress.md), [verification](docs/verification.md), [architecture](docs/architecture.md), and [development log](docs/development-log.md) for actual checks and outstanding work. Native hook execution was verified separately; hooks do not establish model accuracy.

## Usage

These commands use the installed module, avoiding PATH/activation requirements:

```powershell
.\.venv\Scripts\python.exe -m job_posting_analyzer --help
.\.venv\Scripts\python.exe -m job_posting_analyzer demo
.\.venv\Scripts\python.exe -m job_posting_analyzer analyze examples/jobs/ai-intern.txt
.\.venv\Scripts\python.exe -m job_posting_analyzer analyze examples/jobs/ai-intern.txt --profile examples/profiles/student.json --json reports/result.json
.\.venv\Scripts\python.exe -m job_posting_analyzer evaluate --offline
.\.venv\Scripts\python.exe -m job_posting_analyzer evaluate --live --split holdout --max-requests 6
```

The console alias `job-analyzer` is available after installation. `analyze` and `evaluate --live` contact Gemini; `demo`, help, tests, and `evaluate --offline` do not. Create the desired output parent directory beforehand. JSON output never overwrites an existing report unless `--overwrite` is supplied. Input files must never be used as output destinations.

Files must be UTF-8, nonblank advertisements of at most 64 KiB, and optional JSON profiles of at most 64 KiB. Profile fields are `education`, `skills`, `projects`, `experience`, `preferences`, `explicitly_missing` (lists of self-reported strings), and `portfolio` (string or null). See the fictional profile for a complete example. The default `python` on Jeremy's machine is an older installation; use the existing `.venv` interpreter locally. Other users should install Python 3.12 before creating the environment.

## Evidence and comparison

Required and preferred qualifications, responsibilities, materials, overview facts, and conflicts are kept separate. Every extracted fact carries an exact quote checked against the original advertisement. Profile comparisons reference qualifications as `r1`, `r2`, or `p1`, `p2`; evidence points to a profile string using a JSON pointer.

`matched` and `partial` need explicit profile support. `missing` requires a statement in `explicitly_missing`; an omitted skill is `unclear`. Portfolio availability remains self-reported and its quality is not assessed. No hiring probability or fit percentage is generated.

Schema and quote checks establish structure and source presence, not correct interpretation. Untrusted inputs are treated as data; the application does not execute commands, follow links, or give Gemini tools. Prompt injection and semantic interpretation remain evaluation concerns, not solved guarantees.

## Evaluation

Nine fictional labeled cases are split into three development examples, three validation cases, and three holdout cases. Only development examples enter the few-shot prompt. Labels were authored by one AI agent and checked against source by another; they are not human-validated.

Offline evaluation replays expected fixtures for both prompt variants and explicitly sets `model_accuracy_measured` false. It proves the scoring pipeline, not real model quality. Live evaluation uses the same model/settings/cases for each variant and includes failures in the results. Normalized exact labels are used for scoring; valid paraphrases may count as errors. Durations and token counts are recorded when available, and unavailable usage remains null. No financial costs or performance improvements are invented.

Observed live run on 2026-11-15: both prompts returned 6/6 structurally valid, quote-validated outputs. Zero-shot matched all expected normalized labels in 2/6 cases; few-shot in 3/6. Many differences were paraphrases such as `Docker knowledge` versus `Docker`, so these numbers are not semantic accuracy estimates. In the conflict case both prompts flagged contradictions but also filled a work-arrangement value; few-shot additionally extracted office attendance as a requirement. Review conflicting fields rather than treating the overview as resolved. No holdout-driven tuning followed this evaluation. See [live results](evaluation/results/live-2026-11-15.json) and [verification notes](docs/verification.md).

The saved live profile example also marks Python basics as matched where the project's conservative rule expects partial because the employer's skill level is unspecified. Its quotes and structure validate, but that interpretation is a known error. The simulated demo shows the intended partial classification. Review status labels and explanations; evidence validation cannot establish semantic correctness.

Exit codes: 0 success, 2 arguments/input/configuration, 3 provider failure, 4 invalid response/evidence, 5 output-write failure.

## AI assistance

Codex wrote implementation and tests with separate worker ownership and independent agent review. Jeremy supplied the brief, scope, approvals, and safety constraints. No human code or label review is claimed. The reusable `.agents/skills/add-extraction-field/SKILL.md` was actually used to add working-hours evidence; see the development log. A public repository without a LICENSE file was requested; none is included.

## API setup

Create a Gemini key in a Free-tier project with no billing at [Google AI Studio](https://aistudio.google.com/apikey). In Windows user environment variables, set `GEMINI_API_KEY` and restart the process that runs Codex. Never paste the key into chat or commit it. An explicit Free-tier confirmation is required before development live requests. Development spending is US$0; no paid fallback is authorized.

The selected model is `gemini-3.1-flash-lite`. One account's successful live checks do not guarantee availability or quota for another account. Free-tier content may be used to improve Google's products; development sends fictional advertisements/profiles only. See [Google's terms](https://aistudio.google.com/docs/terms).
