"""Deny recognized dangerous tool requests before execution."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT = 1024 * 1024


def main():
    try:
        raw = sys.stdin.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise ValueError("Oversized event")
        event = json.loads(raw)
        if not isinstance(event, dict) or event.get("hook_event_name") != "PreToolUse":
            raise ValueError("Invalid event")
        from danger_policy import evaluate

        output = evaluate(event, ROOT)
    except Exception:
        # A policy evaluation error must not silently permit a pending tool call.
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Safety policy could not validate this request.",
            }
        }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
