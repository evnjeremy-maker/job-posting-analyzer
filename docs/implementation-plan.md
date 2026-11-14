# AI Job Posting Analyzer Implementation Plan

> **For Codex:** Implement task by task only after Jeremy says **attaboy**. Use bounded subagents with explicit file ownership and separate specification and code reviews. The user selected Codex; Hermes-specific commands in the planning skill do not apply to execution.

**Goal:** Build a documented Python terminal application that extracts evidence-backed job requirements and optionally compares a self-reported profile, with validated JSON, offline tests, and an honest live evaluation.

**Architecture:** Read and validate local files, extract job facts through one Gemini API integration, validate source evidence, and optionally run a separate profile comparison. Keep presentation, API access, and evaluation separate. Offline demonstrations use explicitly simulated responses through the same validation and reporting path.

**Tech stack:** Python 3.12, standard-library argparse/pathlib/json, Google official `google-genai` SDK, Pydantic 2, pytest, and Ruff for development checks. No website, database, scraping, agent framework, or multi-provider abstraction.

---

## 1. Approval and current evidence

Status: **planning only; execution keyword not received**.

Confirmed decisions:

- Run in this Codex chat. Subagents are permitted when useful.
- API and service spending: **US$0**. No paid fallback, upgrades, billing enrollment, subscriptions, or paid CI runners.
- Proposed provider accepted: Google Gemini Free tier, model `gemini-3.1-flash-lite`.
- Jeremy reports eligibility and needs API key setup instructions.
- Work locally with documentation and Git history throughout development.
- Publish the finished project to a **public** GitHub repository.
- Latest license instruction supersedes the earlier MIT selection: **do not add a LICENSE file or an MIT declaration**.
- Wait for the exact approval signal **attaboy** before implementing, installing, initializing Git, configuring hooks, committing, or publishing.

Read-only evidence gathered on 2026-11-14:

- Workspace `C:\jeremy\sekolah\projects\automated projects` is empty and is not a Git repository.
- Default `python` resolves to an old Python 3.7 installation. Do not use it.
- Existing bundled interpreter `C:\Users\Asus TuF Gaming F15\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` reports `Python 3.12.14`.
- Installed CLI reports `codex-cli 0.154.0`. Actual hook loading in the desktop session remains unverified.
- Some old hook hashes reference a nonexistent project directory. They do not prove that new hooks are trusted or running; do not alter those global entries.
- No application, tests, dependency installation, hook configuration, or repository has been created. This plan is the only project-related file created during planning.

Original brief: `C:\Users\Asus TuF Gaming F15\.codex\attachments\602137c8-67fb-4954-ac6c-569ec5ac9c64\Pasted text.txt`.

## 2. Execution scope proposed for approval

Project root: `C:\jeremy\sekolah\projects\automated projects\job-posting-analyzer`.

Approval authorizes creating this project, its `.venv`, local Git history, project-local hooks, fictional fixtures, documentation, tests, and free dependency downloads. It authorizes small free-tier API checks using fictional inputs and publishing the completed repository under Jeremy's connected personal GitHub account, if exactly one intended account is identifiable. Ask only if the publishing account is ambiguous or `job-posting-analyzer` already exists; do not overwrite another repository.

Use the existing bundled Python for the local environment, but document ordinary Python 3.12 setup for other users. Pin actual installed dependency versions after compatibility is verified; do not invent version pins now. Do not modify global Python, global Codex configuration, other projects, or existing user work.

API key setup, hook trust, and sandbox/network approval may require user action. Approval in chat cannot bypass platform permission controls. Bootstrap and verify hooks before treating the run as unattended. If a free API quota runs out, finish independent offline work and report the live check as pending; do not silently select a paid tier or another provider.

## 3. API key setup and privacy

### Filesystem and destructive-action boundary

Jeremy explicitly requires protection against deleting or modifying unrelated work. Execution and subagents must stay inside the project root in section 2. Do not delete, move, overwrite, or modify files outside that root, including sibling projects, global settings, credentials, and user documents. Read external documentation and use the existing interpreter only as needed; this does not authorize external writes.

Do not use recursive directory wipes, `git reset --hard`, `git clean`, force pushes, or broad cleanup commands. Routine edits to project-owned source and removal of disposable files created by this run inside the project are allowed. Before removing any such file, resolve its absolute path and verify ownership and containment. Ask before deleting existing user work or taking any other destructive action. The later execution keyword does not waive this boundary.

Use a project-root sandbox when supported and retain platform approvals. The current chat's writable workspace includes the parent directory; instructions and hooks alone do not narrow that operating-system permission. Verify the actual sandbox boundary during bootstrap, report its limits before unattended execution, and never request unrestricted filesystem access as a convenience. Verification hooks are not a comprehensive deletion-prevention mechanism.

Jeremy's setup before unattended live verification:

1. Open [Google AI Studio API Keys](https://aistudio.google.com/apikey), sign in, and create a key in a project that remains on the Free tier. Do not link billing or select a paid project. Complete any provider-required verification through Google's UI.
2. In Windows, search for **Edit environment variables for your account**. Create user variable `GEMINI_API_KEY` with the key as its value. Do not send the key in chat, put it in a command argument, or save it in the repository.
3. Restart Codex if needed so its processes inherit the variable, then reopen this chat. A fresh terminal inherits new user variables; an already-running process may not.
4. Confirm only that the key is configured. The agent may check variable presence without printing its value. Do not dump all environment variables or credential files.

The application passes this key explicitly from its configuration to the Gemini SDK, so an unrelated `GOOGLE_API_KEY` cannot silently select another project. No `.env` loader is needed. Documentation includes the same setup instructions.

Google lists free input/output for the selected model, subject to access and quota. Free-tier content may be used to improve Google's products. Development and live evaluation therefore send **fictional advertisements and fictional profiles only**. Real users receive a clear privacy explanation before usage; the CLI does not transmit anything during help, validation failures, demos, or offline evaluation.

Sources: [API key setup](https://aistudio.google.com/docs/api-key), [pricing](https://aistudio.google.com/docs/pricing#gemini-3.1-flash-lite), [model capabilities](https://aistudio.google.com/docs/models/gemini-3.1-flash-lite), [structured output](https://aistudio.google.com/docs/structured-output), [data terms](https://aistudio.google.com/docs/terms), [available regions](https://aistudio.google.com/docs/available-regions). Account access, actual quota, and SDK compatibility still require verification.

## 4. Fixed product decisions

- English CLI and documentation; initial evaluation uses English advertisements. Preserve Unicode and UTF-8 input. Other-language accuracy remains unverified.
- Input is local UTF-8 text and optional JSON profile. No PDFs, URLs, uploads, scraping, or remote file retrieval.
- Reject blank advertisements, invalid UTF-8, and inputs over 64 KiB per file. Read at most limit plus one byte. Do not contact Gemini when local validation fails.
- Extract overview fields as nullable evidence-backed values: title, employer, location, work arrangement, employment type, salary text, deadline text, and working-hours text. Preserve salary/deadline wording rather than inventing currency, timezone, or dates.
- Separate required qualifications, preferred qualifications, responsibilities, application materials, and ambiguous/conflicting statements. Missing values display as `Not provided`.
- Every extracted nonempty claim has a nonempty exact substring quote. Overview evidence is included to make unsupported claims inspectable. Conflicts carry both relevant quotes; do not select a resolution without source support.
- Assign qualification IDs in Python after validation. Comparison references only those IDs, exactly once each. Responsibilities never become prior-experience requirements automatically.
- Profile fields cover education, skills and experience descriptions, projects, work/internship experience, portfolio availability, and preferences/constraints. Include an explicit list of qualifications the person states they lack. An omitted field never means the person lacks it.
- Comparison outcomes are exactly `matched`, `partial`, `missing`, and `unclear`. Default to `unclear` when support is absent. `missing` requires an explicit negative profile statement; `matched` and `partial` require profile evidence.
- Profile evidence uses JSON pointers to scalar strings and exact quotes within those strings. Validate pointer resolution and quote presence. This checks evidence existence, not semantic correctness.
- Portfolio availability is reported separately from qualification matching. Never claim portfolio quality or inspected work.
- No hiring probabilities, arbitrary fit scores, guarantees, or inferred personal characteristics.
- Extraction and comparison are separate API calls, with separate failure labels. If comparison fails, the requested combined operation fails; do not save partial output as a completed report.
- Use SDK schema support with Pydantic, then independently validate parsed content, references, and evidence. Handle refusals, safety blocks, truncated responses, and missing parsed data as failures.
- Treat advertisements and profiles only as untrusted data. Gemini receives no tools. Never execute embedded commands or follow embedded URLs. Document that prompts and quote checks do not prove semantic immunity to prompt injection.
- Use plain terminal output with user-supplied control characters escaped; preserve original strings for evidence validation and JSON. Print diagnostics to stderr.
- JSON output contains a schema version, provider/model and prompt identifiers, validated analysis, optional comparison, and explicit simulation/live provenance. Avoid full input copies and credential logging.
- Output defaults to no overwrite. Require `--overwrite` for replacement; validate requested destination before API calls and recheck at write time. Use safe replacement after complete serialization when overwriting, preserving an existing file if the write fails.
- Exit codes: `0` success/help; `2` CLI/input/configuration errors; `3` provider errors; `4` response/evidence validation errors; `5` output-write errors. Reports with invalid content never exit successfully.
- Start with 30-second per-attempt API timeouts. Retry transport failures, transient server errors, and retryable rate limits at most twice, with short bounded waits. Do not retry authentication, exhausted daily quota, invalid schemas, or invalid model evidence. Inspect actual SDK retry defaults to prevent nested retries.

Planned CLI contracts:

```powershell
job-analyzer --help
job-analyzer analyze examples/jobs/ai-intern.txt
job-analyzer analyze examples/jobs/ai-intern.txt --profile examples/profiles/student.json --json report.json
job-analyzer demo
job-analyzer evaluate --offline
job-analyzer evaluate --live --split holdout --max-requests 12
```

`demo` always labels responses as simulated. `evaluate --offline` checks the evaluation machinery with simulated responses; its results are not model accuracy measurements. Live evaluation requires its explicit flag and an API key. No live calls happen in ordinary tests or CI.

## 5. Files and ownership

All paths below are relative to the absolute project root in section 2.

```text
AGENTS.md
README.md
pyproject.toml
requirements-dev.lock
.gitignore
.codex/hooks.json
.agents/skills/add-extraction-field/SKILL.md
.github/workflows/ci.yml
scripts/verify.py
scripts/codex_hook.py
src/job_posting_analyzer/__init__.py
src/job_posting_analyzer/__main__.py
src/job_posting_analyzer/cli.py
src/job_posting_analyzer/models.py
src/job_posting_analyzer/inputs.py
src/job_posting_analyzer/evidence.py
src/job_posting_analyzer/prompts.py
src/job_posting_analyzer/gemini.py
src/job_posting_analyzer/analysis.py
src/job_posting_analyzer/report.py
src/job_posting_analyzer/evaluation.py
tests/conftest.py
tests/test_models.py
tests/test_inputs.py
tests/test_evidence.py
tests/test_analysis.py
tests/test_gemini.py
tests/test_report.py
tests/test_cli.py
tests/test_evaluation.py
tests/test_hooks.py
tests/fixtures/simulated/
examples/jobs/
examples/profiles/
evaluation/cases.json
evaluation/expected/
evaluation/results/
docs/architecture.md
docs/decisions.md
docs/development-log.md
docs/verification.md
docs/progress.md
```

No `LICENSE` file. No generated keys, personal profiles, local reports, `.venv`, or hook session state in Git.

Parent agent owns integration, dependencies, hooks, docs/progress, Git commits, live requests, and publishing. Delegate independent work after shared schemas are stable. Possible ownership: worker A models/input/evidence and their tests; worker B reporting/CLI and their tests; worker C evaluation data/runner and their tests. Each worker must know other agents are editing the repository, preserve their changes, and remain within assigned files. One agent owns all writes to any one file at a time. Reviewers report findings without editing another worker's files.

## 6. Hooks and unattended work

Use two project-local Codex events: `SessionStart` to restore the recorded objective/current task, and `Stop` to run verification when an implementation task is active. Do not build an automatic permission-approval hook or a broad shell-command filter.

Codex discovers project hooks in `.codex/hooks.json`; project trust and review of exact non-managed hook definitions are required. A changed definition needs review again. `Stop` can request a continuation using a blocking decision, and receives `stop_hook_active`. These behaviors come from [official hook documentation](https://learn.chatgpt.com/docs/hooks); installed desktop behavior must be probed before relying on it.

Implementation policy:

- Operate with the actual project root as the Codex workspace. A child `.codex` directory under the current parent workspace is not sufficient proof of discovery.
- Keep hook commands Windows-compatible, with absolute resolved interpreter/script paths and correct quoting. Machine-specific launch paths are documented and generated locally rather than presented as portable configuration.
- Hook output must follow the event's documented JSON contract; send test output to stderr or a local log, never mix it into protocol JSON.
- Hooks never run paid operations, network requests, dependency installation, or commits.
- `Stop` invokes `scripts/verify.py`, the same offline check used locally and in CI. Set an explicit timeout and terminate a timed-out child process.
- Permit one correction continuation only. If `stop_hook_active` is true and verification still fails, report failure without creating another continuation. No unbounded self-restart loop.
- Do not block planning-only work, intentional user interruptions, required approvals, or a clearly recorded external blocker. The parent must record remaining work honestly before stopping.
- Do not treat hook success as proof of API accuracy or completion of all requirements.
- Validate both handler behavior using synthetic event input and actual Codex loading with a harmless event probe. Record whether each was verified.
- If the desktop cannot load the hooks from this workspace/session, report that before unattended work; use explicit verification and CI as documented checks, without claiming hook enforcement.

`docs/progress.md` is the durable task checklist. Update after each completed task with exact checks and blockers. Existing platform interruptions, resource limits, and credential/trust prompts can still stop execution. Hooks do not restart a closed application.

## 7. Implementation tasks

For each behavioral task: write a focused test, run it and observe the intended failure, implement the smallest behavior, rerun that test, review the diff, and commit the task's owned files. Do not write implementation-mirroring tests for simple metadata or prose. Expand tests only for changed behavior, failures, or unresolved risks.

Commands below assume PowerShell at the project root. Use `.\.venv\Scripts\python.exe` explicitly; environment activation is optional. CLI examples use the installed name `job-analyzer`; without activation, invoke that name as `.\.venv\Scripts\job-analyzer.exe`.

### Task 1: Bootstrap the repository and environment

Create `pyproject.toml`, `.gitignore`, package entry files, and `AGENTS.md`. Use setuptools with a `src` layout and console entry point `job-analyzer`. Carry forward Jeremy's engineering rules and approved scope. Do not install extra skills or modify global skill files.

Create `.venv` with the verified Python 3.12 interpreter. Install the project editable with its dev dependencies. Record actual resolved versions in `requirements-dev.lock` and verify `pip check`. Initialize Git only inside the new project. Check configured Git identity; do not invent Jeremy's identity or rewrite global Git settings.

Proof: `.\.venv\Scripts\python.exe --version`, `.\.venv\Scripts\python.exe -m pip check`, and `job-analyzer --help` succeeds with no API key and no network request. Do not claim live integration here.

### Task 2: Add one verification command

Create `scripts/verify.py` and `.github/workflows/ci.yml`. Run Ruff lint/format checks and `pytest` offline through the same interpreter. Test on Python 3.12 in Windows and Linux CI using standard free runners; no credentials, live jobs, or scheduled paid work.

Proof: `.\.venv\Scripts\python.exe scripts/verify.py` exits nonzero on a deliberately failing disposable test, and succeeds after removing that test. Do not leave a fabricated passing report. The script must work from any current directory by resolving the repository root.

### Task 3: Bootstrap and verify hooks

Create `.codex/hooks.json`, `scripts/codex_hook.py`, `tests/test_hooks.py`, and `docs/progress.md`. Test event parsing, valid JSON output, timeout, failure feedback, planning bypass, user-input bypass, and one-continuation limit.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_hooks.py -q`, followed by an actual harmless runtime probe after Jeremy reviews/trusts the concrete definitions. Do not edit trust hashes or bypass hook trust. Finish this step before relying on unattended enforcement.

### Task 4: Define validated schemas and examples

Create `models.py`, `tests/test_models.py`, one fictional job, one fictional profile, and simulated provider responses. Use explicit fields, enums, nonblank evidence, and rejection of unexpected fields. Keep provider response schemas compatible with the supported JSON Schema subset. Generate JSON schemas from the Pydantic models rather than maintaining duplicate schema files by hand. Leave the approved working-hours field for task 14 so the reusable skill has a real, scoped use before the final schema is complete.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_models.py -q`. Reject unknown comparison statuses, missing evidence fields, invalid profile shapes, and unrelated fields. Accept the example from the brief, including explicitly absent SQL and an available self-reported portfolio.

### Task 5: Validate local files before provider access

Create `inputs.py` and `tests/test_inputs.py`. Implement bounded reads, UTF-8 decoding, JSON parsing, and path errors. Preflight output arguments without touching the destination. Accept valid Unicode. File errors must not echo full personal input.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_inputs.py -q`. Cover missing/unreadable files, directories, blank text, invalid UTF-8, invalid JSON, size boundary and boundary plus one byte. Assert provider code is not called on failures.

### Task 6: Validate source evidence and qualification references

Create `evidence.py` and `tests/test_evidence.py`. Check exact quotes against the original decoded advertisement, profile pointers against parsed JSON, and comparison coverage against Python-assigned qualification IDs. Require explicit support for every claimed match or absence. No fuzzy quote correction.

Complete example of the intended quote check contract:

```python
def require_quote(source: str, quote: str) -> None:
    if not quote.strip() or quote not in source:
        raise ValueError("Supporting quote is absent from source.")
```

Complete focused test example:

```python
import pytest
from job_posting_analyzer.evidence import require_quote


def test_rejects_quote_absent_from_source():
    with pytest.raises(ValueError, match="Supporting quote is absent from source"):
        require_quote("SQL is preferred.", "SQL is required.")
```

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_evidence.py -q`. Also test blank quotes, altered punctuation/case, unresolved JSON pointers, unknown/duplicated/omitted requirement IDs, and unsupported comparison evidence. Record that valid quotes do not prove correct interpretation.

### Task 7: Write extraction and comparison prompts

Create `prompts.py` and frozen development examples. Include separate zero-shot and few-shot extraction prompts with a shared output contract. The comparison prompt explicitly distinguishes absent information from explicit lack. Delimit untrusted input and prohibit obeying embedded instructions.

Review expected outputs against the source, including the ambiguous Python-basics example. Avoid interpreting responsibilities as required past experience. Do not create a model-based self-grader as the source of truth.

Proof: review prompts and example labels separately for specification compliance. Any tests here should target contract integration or attack cases, not exact wording snapshots.

### Task 8: Implement the single Gemini integration

Create `gemini.py` and `tests/test_gemini.py`. Recheck the installed official SDK API before writing calls. Instantiate its client lazily. Configure the fixed approved model, supported structured response settings, timeout, output limit, and bounded retries. Disable tools, search, URL context, and unnecessary request logging.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_gemini.py -q` with simulated SDK responses. Cover authentication, quota/rate limits, transport failures, server errors, malformed data, refusals, truncation, missing parsed response, and bounded attempts. Confirm SDK defaults do not multiply retries. These tests do not prove a live connection.

### Task 9: Connect extraction and optional comparison

Create `analysis.py` and `tests/test_analysis.py`. Validate extraction before invoking comparison. Add comparison only when a profile exists. Preserve stage-specific failures and return only fully validated completed reports.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_analysis.py -q`. Assert one logical API operation without a profile and two with a profile. Reject invalid extraction before comparison; reject invalid comparison without returning combined success. Cover matched, partial, explicitly missing, and unclear cases.

### Task 10: Add terminal and JSON reports

Create `report.py` and `tests/test_report.py`. Use headings and readable text; escape terminal control sequences from source material. Show source quotes, missing job information, comparison uncertainty, and provenance. Write JSON only after complete validation. Preserve existing files without `--overwrite` and on write failure.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_report.py -q`. Verify output-file protection, invalid destinations, replacement failure, readable Unicode, terminal escape handling, JSON schema round-trip, and explicit simulation labels.

### Task 11: Add CLI and offline demonstration

Complete `cli.py`, `__main__.py`, `tests/test_cli.py`, and the fictional examples. Use argparse rather than a new CLI framework. Implement the command contracts and exit codes in section 4. Wire the simulated demo through the production validation/report path.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_cli.py -q`, `job-analyzer --help`, and `job-analyzer demo`. Patch outbound network access to fail in offline tests so accidental provider requests cause test failures. Test console and `python -m job_posting_analyzer` entry points, input paths with spaces, stderr errors, and overwrite opt-in.

### Task 12: Build evaluation data with separate holdout cases

Create `evaluation/cases.json`, `evaluation/expected/`, and the additional fictional advertisements. Start with nine short advertisements: three few-shot development examples, three validation cases, and three frozen holdout cases. Cover missing fields, required/preferred distinctions, responsibilities, conflicts, application materials, and embedded instructions.

One agent authors expected answers; a different agent checks every label and quote against the source. Record that these are **agent-authored and agent-reviewed**, with human review absent unless Jeremy actually reviews them. Do not claim human-validated labels. This is a disclosed limitation against the brief's manually checked-answer objective.

Freeze holdout data before prompt tuning. Do not use holdout failures to tune prompts and then continue calling the same cases an untouched holdout. If revision is necessary, report it and create new holdout cases.

### Task 13: Implement repeatable evaluation

Create `evaluation.py` and `tests/test_evaluation.py`. Compare both extraction prompts using the same model/settings on the same cases. Keep simulated and live artifacts separate. Use deterministic scoring of labeled atomic fields/categories/quotes; do not treat string similarity alone as semantic equivalence. Report unmatched items and all failed cases for inspection.

Report classification/extraction errors, unsupported claims, exact-quote validity, format validity, response duration, token usage if returned, failed requests, prompt/model identifiers, split, and simulation status. Record unavailable usage as unavailable, never zero. Make no invented monetary cost claims or unsupported accuracy-improvement claims.

Proof: `.\.venv\Scripts\python.exe -m pytest tests/test_evaluation.py -q` with deliberately wrong simulated cases, then `job-analyzer evaluate --offline`. Verify failures stay in denominators and both prompts use the identical fixture split. The offline run proves scoring machinery, not real model quality.

### Task 14: Create and use the development skill

Create `.agents/skills/add-extraction-field/SKILL.md`. Scope it to tracing a new field across model, provider schema, prompts, evidence checks, reporting, fixtures, and tests.

Document one actual use: add the already-required working-hours field through this skill after the initial schema pipeline exists. Record before/after behavior, changed files, exact focused tests and results. Do not invent earlier use or add an unrelated feature solely to demonstrate the skill.

### Task 15: Run bounded live verification on the Free tier

Only the parent agent performs live API calls; workers and CI remain offline. Check key presence without displaying it and obtain Jeremy's confirmation that its project is unbilled/Free tier. If that cannot be established, do not send requests.

Run one extraction-only smoke case and one case with a profile, then compare both prompts across the three validation and three holdout cases. Planned total: 15 logical requests before retries. Cap the initial development session at 24 HTTP attempts including retries. Keep executions sequential to respect free quotas. Stop when quota is exhausted; no repeated rapid polling or paid fallback.

Record actual counts, model identifier, settings, response handling, duration, and failures in `docs/verification.md` and separate live evaluation artifacts. If blocked by access, key, quota, or network, finish all independent offline work and mark live verification **unverified/pending**. Do not claim the full live-dependent definition of done is met.

### Task 16: Complete documentation and independent review

Write `README.md`, `docs/architecture.md`, `docs/decisions.md`, `docs/development-log.md`, and final verification/progress records. Cover setup for a clean Python 3.12 environment, examples, key setup, privacy, US$0 development policy, provider quotas, exact commands, evidence limitations, honest AI contributions, and missing human review. Keep prose normal English; caveman compression applies to chat only.

Review code comments with `antislop-code`: retain concise reasons, contracts, traps, and security constraints; remove narration and decorative comments. This comment review does not alter executable code. No visual/UI skill installation is needed for this terminal project.

Run `scripts/verify.py`, clean-environment installation checks, the documented demo, and documented evaluation commands. Review specification compliance first, then code quality/security. Fix actionable findings with focused regression tests. Do not claim tests passed unless actual command results are recorded.

### Task 17: Publish the completed repository

After local review and verification, inspect the staged files and history for credentials, personal inputs, generated local paths, and unrelated files. Do not stage everything blindly. Use existing connected GitHub tooling if sufficient; otherwise use authenticated `gh` after reading the applicable GitHub workflow skill. Never expose authentication tokens.

Create public `job-posting-analyzer` under Jeremy's confirmed personal account, without a LICENSE file, and push the complete local history. The user's publication choice and execution keyword authorize this final action; do not ask redundant permission. Ask only on an account/name conflict or a material change to the approved scope.

Run and observe CI to completion after pushing. Fix failures, rerun the affected checks, and report the actual repository URL and CI status. If live integration remains blocked, do not label the project fully finished or publish a misleading completion claim; report the blocker and finish the remaining work when the external requirement is supplied.

## 8. Completion evidence

- Another person can install with Python 3.12 from the README.
- Help, demos, and tests work without credentials or API access.
- A real advertisement extraction and optional fictional profile comparison pass live schema/evidence handling.
- Required/preferred/responsibility distinctions and unclear/missing semantics have focused tests and reviewed evaluation cases.
- Invalid provider results and write failures cannot appear as successful analysis.
- JSON output is validated and existing files are protected.
- Both prompts have honest comparable live results, including failures; simulated results are separate.
- Reusable skill has a documented actual use.
- Hook handler tests and actual hook-loading status are separately recorded.
- Public GitHub repository contains documentation and development history, no LICENSE file, no credentials or personal profiles, and observed CI results.
- Final handoff states exact checks, real results, unresolved risks, and material omissions. Never attribute agent-written work or agent-reviewed labels to Jeremy without evidence.

## 9. Remaining readiness items

No additional product design choice is required unless Jeremy changes the proposed defaults. Before execution, Jeremy can approve this complete scope with **attaboy**. API key configuration and provider Free-tier confirmation are needed before the live phase; exact hook definitions can only be reviewed/trusted after bootstrap. Platform permission prompts and GitHub authentication may still require interaction.

Outstanding limitations: the API key, account quota, live model behavior, hook discovery/trust, GitHub write access, clean installation, tests, and CI have **not** been verified. The plan does not represent completed implementation.
