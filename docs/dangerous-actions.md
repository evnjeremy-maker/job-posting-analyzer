# Dangerous-action guard

This is a bounded PreToolUse deny policy. It checks pending supported tool requests before execution; it does not implement a filesystem sandbox or prove arbitrary code safe.

## Policy

- Block recognizable shell deletion commands, including common PowerShell aliases.
- Block recognizable destructive Git operations, disk/system changes, and encoded shell commands.
- Reject shell write commands whose targets cannot be reliably resolved. Prefer path-checked file edits.
- For supported direct edit and apply_patch inputs, reject targets outside the repository, traversal escapes, resolved links outside the root, and protected policy/configuration files.
- Reject patch deletions/moves and recognized direct filesystem delete/move tools. The hook cannot determine whether an existing user file is safe to remove.
- Return no decision for accepted requests. The sandbox and normal approval process remain in effect; this hook never auto-approves a request.
- The entrypoint returns a denial on malformed input and exceptions during policy evaluation, without echoing command contents or credentials.

The separate SessionStart/Stop behavior remains unchanged. Stop verification can be inactive while the dangerous-action guard still applies.

## Coverage limits

Shell checks recognize strings, not full PowerShell, cmd, Bash, or Python semantics. Arbitrary scripts, interpreters, indirect calls, aliases, obfuscation, existing executable code, and unrecognized tools can evade this bounded detector. Harmless commands containing blocked syntax may also be denied. An allowed request means only that no implemented deny rule matched.

The agent can change unprotected source and tests, which subsequently run as code. The guard is not a defense against a malicious agent with writable code and interpreter access. Keep the sandbox enabled and do not grant broader permissions to work around a denial.

Handler-level error denial does not make the entire runtime fail-closed: disabled/untrusted hooks, missing executables, process failures, and platform-level timeouts can prevent evaluation. Supported hook coverage and error handling depend on Codex. See [official documentation](https://learn.chatgpt.com/docs/hooks#pretooluse).

## Activation

The generated local `.codex/hooks.json` contains a PreToolUse command that invokes this project's virtual-environment Python with the absolute path to `scripts/pre_tool_guard.py`. No matcher limits it to a single tool name. Review that new definition in `/hooks` and trust it. Do not edit trust hashes or bypass hook trust.

The original SessionStart/Stop entries are retained. Trust review is required because this is a new hook definition, not because the project needs another execution approval.

Policy tests pass simulated event strings to the guard; no destructive operation is executed. Native blocking must be checked separately after trust, using a harmless request whose spelling triggers a deny rule and produces no file operation if the guard is not loaded. Do not test by attempting real deletion.
