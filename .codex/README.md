# Local hooks

`hooks.json` is generated locally with absolute interpreter/script paths. It is ignored by Git because those paths identify this machine. This project uses SessionStart, Stop, and PreToolUse. None approves tools, runs network operations, installs dependencies, deletes files, or changes permissions.

Handler: `scripts/codex_hook.py`. Offline gate: `scripts/verify.py`.

Dangerous-action entrypoint: `scripts/pre_tool_guard.py`, with rules in `scripts/danger_policy.py`. The new PreToolUse definition requires its own review/trust. See `docs/dangerous-actions.md` for coverage and limits. Unlike Stop verification, this guard is independent of the progress status.

Review the handler and generated definitions, then open the project itself as the Codex workspace. Review/trust the new definitions using the supported hook interface (`/hooks` in Codex CLI). Never edit trust hashes or bypass hook trust. A direct synthetic handler test does not prove Codex loaded a hook.

`docs/progress.md` controls the gate using its `Status:` line. `implementation` enables verification. `bootstrap`, `awaiting-user`, `blocked`, and `complete` leave it inactive. The gate allows one correction continuation; subsequent failures must be reported. A planning session does not trigger verification.

New receipts in ignored `.codex/hook-events.jsonl` contain exactly `event` and `timestamp_utc` (UTC ISO 8601). No other metadata or payload is recorded. Existing receipts from the previous format are preserved. Resolved-path containment and logging failure handling remain unchanged; neither provides a sandbox.

Synthetic receipts use separate `.cache/hook-tests/<unique-id>/.codex/hook-events.jsonl` files. Tests never populate the real receipt file. Correlate native event names and timestamps with lifecycle actions; receipts are not authenticated proof. Do not manually invoke the handler against the actual project root while establishing native evidence.

Before unattended work, verify actual hook discovery and trust and inspect effective filesystem permissions. As of 2026-11-15, the cwd and Git root are this project; declared workspace write roots include this project and a separate visualization directory. Parent-workspace writes are no longer declared. A project-only OS boundary remains unproven. These hooks cannot narrow permissions or comprehensively prevent deletion.
