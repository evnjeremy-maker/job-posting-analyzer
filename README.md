# AI Job Posting Analyzer

Python terminal application under development. Planned behavior: extract evidence-backed job requirements and optionally compare a self-reported profile. No application commands are implemented yet.

## Bootstrap

Requires Python 3.12. On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe scripts/verify.py
```

On Linux, use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

The verification command runs Ruff and offline pytest tests. It requires no API key and makes no Gemini requests. CI configuration is prepared for Windows/Linux but has not run on GitHub.

## Current state

Project environment, safety instructions, verification handler, tests, and CI configuration exist. Native Codex hook loading, API integration, evaluation, and publication remain pending. See [progress](docs/progress.md), [hook setup](.codex/README.md), and [approved plan](docs/implementation-plan.md).

## API setup

Create a Gemini key in a Free-tier project with no billing at [Google AI Studio](https://aistudio.google.com/apikey). In Windows user environment variables, set `GEMINI_API_KEY` and restart the process that runs Codex. Never paste the key into chat or commit it. An explicit Free-tier confirmation is required before development live requests. Development spending is US$0; no paid fallback is authorized.

The selected model is `gemini-3.1-flash-lite`. Access/quota and live behavior are unverified. Free-tier content may be used to improve Google's products; development sends fictional advertisements/profiles only. See [Google's terms](https://aistudio.google.com/docs/terms).
