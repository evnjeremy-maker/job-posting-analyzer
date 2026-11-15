"""Project-local Codex lifecycle handler; reads one JSON event from stdin."""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def record_event(event):
    if event.get("hook_event_name") not in {"SessionStart", "Stop"}:
        return
    cwd = Path(event.get("cwd", "")).resolve()
    if not cwd.is_relative_to(ROOT):
        return
    log_path = ROOT / ".codex/hook-events.jsonl"
    if not log_path.resolve().is_relative_to(ROOT):
        raise ValueError("Hook event log resolves outside the project root")
    record = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "event": event["hook_event_name"],
    }
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")


def run_verification():
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/verify.py")],
            cwd=ROOT,
            stdout=sys.stderr,
            stderr=sys.stderr,
            timeout=50,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Verification failed: {type(error).__name__}", file=sys.stderr)
        return False


def handle(event, *, verify=None, status="bootstrap"):
    cwd = Path(event.get("cwd", "")).resolve()
    if not cwd.is_relative_to(ROOT):
        return {"systemMessage": "Hook skipped: session cwd is outside the project root."}
    if event.get("hook_event_name") == "SessionStart":
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "Read AGENTS.md and docs/progress.md. Work only inside this project; "
                    "never modify or delete outside it. No destructive Git commands. "
                    "US$0 budget; fictional API inputs only. Hooks are not a sandbox."
                ),
            }
        }
    if event.get("hook_event_name") == "Stop" and status == "implementation":
        if event.get("permission_mode") == "plan":
            return {}
        if event.get("stop_hook_active"):
            return {"systemMessage": "Continuation limit reached. Report remaining failures."}
        if verify is not None and not verify():
            return {"decision": "block", "reason": "Offline verification failed. Fix and rerun."}
    return {}


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("Expected object")
        progress = (ROOT / "docs/progress.md").read_text(encoding="utf-8")
        status = next(
            (
                line.removeprefix("Status: ")
                for line in progress.splitlines()
                if line.startswith("Status: ")
            ),
            "bootstrap",
        )
        output = handle(event, verify=run_verification, status=status)
        try:
            record_event(event)
        except (OSError, ValueError) as error:
            print(f"Hook event log unavailable: {type(error).__name__}", file=sys.stderr)
    except (ValueError, TypeError, OSError) as error:
        output = {"systemMessage": f"Hook input error: {type(error).__name__}. Check setup."}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
