# Local hooks

`hooks.json` is generated locally with absolute interpreter/script paths. It is ignored by Git because those paths identify this machine. This project uses SessionStart and Stop only. Neither hook approves tools, runs network operations, installs dependencies, deletes files, or changes permissions.

Handler: `scripts/codex_hook.py`. Offline gate: `scripts/verify.py`.

Review the handler and generated definitions, then open the project itself as the Codex workspace. Review/trust the new definitions using the supported hook interface (`/hooks` in Codex CLI). Never edit trust hashes or bypass hook trust. A direct synthetic handler test does not prove Codex loaded a hook.

`docs/progress.md` controls the gate using its `Status:` line. `implementation` enables verification. `bootstrap`, `awaiting-user`, `blocked`, and `complete` leave it inactive. The gate allows one correction continuation; subsequent failures must be reported. A planning session does not trigger verification.

Before unattended work, verify actual hook discovery and trust and inspect the effective filesystem permissions. This chat began in the parent workspace, which permits sibling-directory writes. These hooks cannot narrow that permission or comprehensively prevent deletion.
