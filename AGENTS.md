# Project rules

Approved plan: `docs/implementation-plan.md`. Jeremy authorized execution with `attaboy`.

- Work only inside this repository. Never delete, move, overwrite, or modify unrelated files, sibling projects, user documents, global configuration, or credentials.
- No directory wipes, destructive Git resets, `git clean`, force pushes, unrestricted filesystem access, or automatic approval of permissions. Ask before deleting existing user work.
- Before removing a disposable file made by this run, resolve its absolute path and verify containment and ownership. Preserve other agents' edits; assign explicit file ownership.
- US$0 budget. Gemini Free tier only, fictional development inputs only. Never enable billing or select a paid fallback. Only the parent agent makes bounded live requests after Free-tier confirmation.
- Never print API keys or environment dumps. Read `GEMINI_API_KEY` only when an explicit live operation requires it. Keep credentials and personal inputs out of Git.
- Python 3.12, official Google GenAI SDK, Pydantic, argparse, pytest, Ruff. Terminal app only. No web UI, scraping, database, agent framework, or multi-provider support.
- Trace behavior before edits. Write a failing behavioral test before implementation, implement the smallest complete change, then run focused proof. Never fabricate test or evaluation results.
- Keep required/preferred/responsibility categories separate. Validate exact source quotes. Profile omission means unclear, not missing. No hiring probability or arbitrary fit scores.
- Run `.venv/Scripts/python.exe scripts/verify.py` on Windows, or `.venv/bin/python scripts/verify.py` on Linux, before commits. Independent review precedes commits and publication.
- Update `docs/progress.md` with actual evidence and blockers. Public GitHub publication occurs after completion; do not add a LICENSE file.
- Hooks provide context and verification, not a filesystem security boundary. Do not claim runtime hook loading until observed. Project trust and exact hook trust require user review.
- Existing antislop core and antislop-code apply during development. Keep comments short and useful; explain constraints rather than narrating code. Do not install skills or modify global skill files.
- New UI work would require a separate design/antislop discussion. No UI work is authorized here.
