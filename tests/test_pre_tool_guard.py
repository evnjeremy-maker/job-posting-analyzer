import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def invoke(payload):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/pre_tool_guard.py")],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_malformed_guard_input_is_denied_without_echoing():
    result = invoke("PRIVATE malformed input")
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "PRIVATE" not in result.stdout + result.stderr


@pytest.mark.parametrize("payload", ["[]", "{}", '"not an event"', "x" * (1024 * 1024 + 1)])
def test_invalid_guard_events_are_denied(payload):
    result = invoke(payload)
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_safe_command_keeps_normal_approval_flow():
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "cwd": str(ROOT),
        "tool_input": {"command": "git status --short"},
    }
    result = invoke(json.dumps(event))
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_unsafe_command_is_denied_without_execution_or_echo():
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "cwd": str(ROOT),
        "tool_input": {"command": "Remove-Item -Recurse PRIVATE_PATH"},
    }
    result = invoke(json.dumps(event))
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "PRIVATE_PATH" not in result.stdout + result.stderr
