import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_session_start_restores_safety_context():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/codex_hook.py")],
        input=json.dumps({"hook_event_name": "SessionStart", "cwd": str(ROOT)}),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "AGENTS.md" in context
    assert "outside" in context


def load_handler():
    spec = importlib.util.spec_from_file_location("codex_hook", ROOT / "scripts/codex_hook.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stop_blocks_on_failed_verification():
    module = load_handler()
    calls = []

    def verify():
        calls.append(True)
        return False

    result = module.handle(
        {"hook_event_name": "Stop", "cwd": str(ROOT)},
        verify=verify,
        status="implementation",
    )
    assert result["decision"] == "block"
    assert calls == [True]


@pytest.mark.parametrize(
    ("fields", "status"),
    [
        ({"stop_hook_active": True}, "implementation"),
        ({"permission_mode": "plan"}, "implementation"),
        ({}, "awaiting-user"),
        ({}, "blocked"),
        ({}, "bootstrap"),
        ({"cwd": str(ROOT.parent)}, "implementation"),
    ],
)
def test_stop_never_continues_in_bypass_cases(fields, status):
    module = load_handler()
    result = module.handle(
        {"hook_event_name": "Stop", "cwd": str(ROOT), **fields},
        verify=lambda: False,
        status=status,
    )
    assert "decision" not in result


def test_stop_allows_successful_verification():
    module = load_handler()
    assert (
        module.handle(
            {"hook_event_name": "Stop", "cwd": str(ROOT)},
            verify=lambda: True,
            status="implementation",
        )
        == {}
    )


def test_verification_timeout_returns_failure(monkeypatch):
    module = load_handler()

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 50
        assert kwargs["cwd"] == ROOT
        raise subprocess.TimeoutExpired(args[0], 50)

    monkeypatch.setattr(module.subprocess, "run", timeout)
    assert module.run_verification() is False


def test_malformed_event_outputs_json_error():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/codex_hook.py")],
        input="broken JSON",
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "Hook input error" in json.loads(result.stdout)["systemMessage"]
