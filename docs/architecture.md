# Architecture

The CLI parses arguments and validates files/output destinations before invoking a provider. `analysis.py` orchestrates two stages: extraction, then optional comparison. Pydantic checks both structures; `evidence.py` checks exact source quotes, JSON pointers, and complete qualification-ID coverage before a report is returned. Responsibilities are not profile qualifications.

`gemini.py` is the only hosted integration. Its client is lazy, explicitly uses `GEMINI_API_KEY`, and disables SDK retries in favor of at most three attempts per operation and an instance-wide cap. Requests have 30-second timeouts, 8192 output tokens, no tools, and generated schemas from the same Pydantic models used locally. Refusal/truncation and invalid responses fail rather than becoming successful reports.

`report.py` renders terminal-safe text and writes complete validated JSON. Existing reports are protected by default; explicit overwrite uses atomic replacement. The demo injects a fictional provider into the production orchestration. Offline tests reject socket connections. Evaluation keeps fixture replay separate from live model measurement and retains failed cases.

Hooks provide project context, bounded offline verification, and recognized dangerous-action denial. They run outside the application pipeline and do not establish application correctness or replace the sandbox.

## Localhost browser adapter

The React/TypeScript frontend is built by Vite and served by FastAPI alongside the JSON API. `job-analyzer serve` binds only to IPv4 loopback. A server-run token, Host/origin validation, request-body bounds and one-analysis-at-a-time lock protect the local adapter; there is no cross-origin access. This is a single-user local tool, not a public authentication system.

`GET /api/session` supplies the run token and attempt budget, `POST /api/analyze` accepts text, optional Profile and prompt variant, and `GET /api/demo` returns the existing simulated Report. No route accepts a filesystem path or API credential. The server reuses the production analysis/evidence pipeline and one bounded Gemini provider per run. Errors return sanitized codes/messages. The browser keeps editable inputs and the last validated report in memory, marks stale results after edits, and exports only by explicit download.

The browser's categories and comparison IDs mirror the existing models. Required/preferred status counts are separate and are not fit scores. Font files are bundled locally. No database, telemetry, history persistence or deployment is included. Automated API tests inject fictional providers rather than contacting Gemini.
