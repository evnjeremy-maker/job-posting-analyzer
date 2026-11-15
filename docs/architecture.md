# Architecture

The CLI parses arguments and validates files/output destinations before invoking a provider. `analysis.py` orchestrates two stages: extraction, then optional comparison. Pydantic checks both structures; `evidence.py` checks exact source quotes, JSON pointers, and complete qualification-ID coverage before a report is returned. Responsibilities are not profile qualifications.

`gemini.py` is the only hosted integration. Its client is lazy, explicitly uses `GEMINI_API_KEY`, and disables SDK retries in favor of at most three attempts per operation and an instance-wide cap. Requests have 30-second timeouts, 8192 output tokens, no tools, and generated schemas from the same Pydantic models used locally. Refusal/truncation and invalid responses fail rather than becoming successful reports.

`report.py` renders terminal-safe text and writes complete validated JSON. Existing reports are protected by default; explicit overwrite uses atomic replacement. The demo injects a fictional provider into the production orchestration. Offline tests reject socket connections. Evaluation keeps fixture replay separate from live model measurement and retains failed cases.

Hooks provide project context, bounded offline verification, and recognized dangerous-action denial. They run outside the application pipeline and do not establish application correctness or replace the sandbox.
