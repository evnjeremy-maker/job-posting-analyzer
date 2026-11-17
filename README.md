# AI Job Posting Analyzer

Python application with a terminal interface and a localhost browser workspace that extracts evidence-backed job requirements and optionally compares a self-reported profile. It organizes evidence; it does not predict hiring outcomes. Extraction and profile comparison were verified against Gemini on fictional inputs; measured limitations are documented below.

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

## Localhost browser workspace

The browser interface follows Jeremy's portfolio typography and editorial layout. It supports job text/import, an optional profile form or JSON import, evidence disclosures, required/preferred comparison counts, and JSON download. The existing CLI remains available.

After the Python bootstrap above, use Node.js 22.22.2+ in the 22 release line, 24.15.0+ in the 24 release line, or 26+, and run from the repository root:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
.\.venv\Scripts\job-analyzer.exe serve
```

Open http://127.0.0.1:8000. On Linux/macOS use `npm` and `.venv/bin/job-analyzer`. An occupied port can be changed with `serve --port 8001`; use the matching URL. The server binds only to `127.0.0.1`, not the local network. Keep its terminal open while using the app; Ctrl+C stops it.

**Load fictional demo** works without a Gemini key or API call. **Analyze job** sends submitted job text and optional profile to Google using the server's `GEMINI_API_KEY`. Never enter a key in the browser. Use an unbilled Free-tier project; development inputs must be fictional. Free-tier quota is controlled by Google, and the app does not verify billing settings.

### Read a job poster

1. In the default **Picture** tab, choose one JPEG or PNG (up to 8 MiB and 20 megapixels). Selection and preview stay local.
2. Click **Read text with Gemini** to send the image to Google. The server validates and re-encodes it in memory, applying orientation and removing metadata; normalized images larger than 12 MiB are rejected. No Google Files API or permanent image upload is used.
3. Compare the editable transcription against the poster. Correct mistakes, review warnings and `[illegible]` passages, then select **I reviewed this text against the poster**. Editing the text resets this confirmation.
4. Click **Analyze job**. The optional profile comparison and zero-shot/few-shot choice apply to this reviewed text, not to image recognition. Transcription token usage is shown separately from analysis usage.

The **Text** tab keeps the original pasted/imported text workflow, with a separate draft. Source quotes are validated against text, not image pixels; recognition and interpretation can both be wrong. Download the transcript as `.txt` separately from report JSON. Replacing/removing a poster clears its transcription and review state and marks earlier results stale. PDFs, multiple posters, animated images, camera input, translation and local OCR are not supported.

For a fictional test poster, use `examples/posters/fictional-ai-intern.png`; the neighboring `.txt` contains its reference text. Images and transcription are kept in memory and discarded on page refresh. Both image reading and analysis consume the same server-run SDK attempt budget. The offline demo remains API-free.

Inputs and results stay in memory until you explicitly download JSON. Refreshing discards them. The server permits one live analysis at a time and shares a 24-SDK-attempt budget per run, including provider retries. A new server run resets this local budget; it does not reset Google's quota. There is no automatic frontend retry or paid fallback. Source/profile quote validation does not prove that a model's interpretation is correct.

Frontend checks, run independently of the Python verification gate:

```powershell
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Built assets and fonts are served locally; no font CDN or analytics runs in the browser. Font license notices are retained in `frontend/public/fonts/` and listed in `frontend/THIRD_PARTY_NOTICES.md`. During frontend development, run `npm.cmd --prefix frontend run watch` alongside the Python server, then reload the browser after changes. This addition is intended for local review; public hosting needs a separate security/deployment design.

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
