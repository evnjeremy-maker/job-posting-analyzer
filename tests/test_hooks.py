import importlib.util
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def hook_project(monkeypatch):
    # Keep synthetic events inside an ignored, unique project-owned directory.
    root = ROOT / ".cache/hook-tests" / uuid4().hex
    (root / ".codex").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "docs/progress.md").write_text("Status: awaiting-user\n", encoding="utf-8")
    module = load_handler()
    monkeypatch.setattr(module, "ROOT", root)
    return module, root


def invoke_main(module, event, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(event)))
    module.main()
    captured = capsys.readouterr()
    return json.loads(captured.out), captured.err


def test_session_start_restores_safety_context(hook_project, monkeypatch, capsys):
    module, root = hook_project
    output, stderr = invoke_main(
        module, {"hook_event_name": "SessionStart", "cwd": str(root)}, monkeypatch, capsys
    )
    assert stderr == ""
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "AGENTS.md" in context
    assert "outside" in context


def test_hook_receipts_contain_only_event_and_timestamp(hook_project, monkeypatch, capsys):
    module, root = hook_project
    for name in ("SessionStart", "Stop"):
        invoke_main(
            module,
            {
                "hook_event_name": name,
                "cwd": str(root),
                "session_id": "fictional-session",
                "stop_hook_active": False,
                "prompt": "PRIVATE INPUT MUST NOT BE LOGGED",
                "last_assistant_message": "PRIVATE RESPONSE MUST NOT BE LOGGED",
                "transcript_path": "PRIVATE PATH MUST NOT BE LOGGED",
            },
            monkeypatch,
            capsys,
        )
    raw = (root / ".codex/hook-events.jsonl").read_text(encoding="utf-8")
    records = [json.loads(line) for line in raw.splitlines()]
    assert [record["event"] for record in records] == ["SessionStart", "Stop"]
    assert "PRIVATE" not in raw
    assert "fictional-session" not in raw
    for record in records:
        assert set(record) == {"timestamp_utc", "event"}
        assert datetime.fromisoformat(record["timestamp_utc"]).utcoffset().total_seconds() == 0


@pytest.mark.parametrize("passed", [True, False])
def test_stop_receipt_preserves_verification_behavior(hook_project, monkeypatch, capsys, passed):
    module, root = hook_project
    (root / "docs/progress.md").write_text("Status: implementation\n", encoding="utf-8")
    monkeypatch.setattr(module, "run_verification", lambda: passed)
    output, stderr = invoke_main(
        module, {"hook_event_name": "Stop", "cwd": str(root)}, monkeypatch, capsys
    )
    assert stderr == ""
    assert (output.get("decision") == "block") is (not passed)
    record = json.loads((root / ".codex/hook-events.jsonl").read_text(encoding="utf-8"))
    assert set(record) == {"timestamp_utc", "event"}
    assert record["event"] == "Stop"


def test_log_failure_preserves_stop_decision(hook_project, monkeypatch, capsys):
    module, root = hook_project
    (root / "docs/progress.md").write_text("Status: implementation\n", encoding="utf-8")
    monkeypatch.setattr(module, "run_verification", lambda: False)

    def denied(*args, **kwargs):
        raise PermissionError("PRIVATE ERROR DETAILS")

    monkeypatch.setattr(module, "record_event", denied)
    output, stderr = invoke_main(
        module, {"hook_event_name": "Stop", "cwd": str(root)}, monkeypatch, capsys
    )
    assert output["decision"] == "block"
    assert "Hook event log unavailable: PermissionError" in stderr
    assert "PRIVATE" not in stderr


def test_outside_event_is_not_logged(hook_project, monkeypatch, capsys):
    module, root = hook_project
    output, _ = invoke_main(
        module, {"hook_event_name": "SessionStart", "cwd": str(root.parent)}, monkeypatch, capsys
    )
    assert "outside" in output["systemMessage"]
    assert not (root / ".codex/hook-events.jsonl").exists()


def test_redirected_log_path_is_rejected(hook_project, monkeypatch, capsys):
    module, root = hook_project
    log_path = root / ".codex/hook-events.jsonl"
    resolve = Path.resolve

    def redirected(path, *args, **kwargs):
        if path == log_path:
            return root.parent / "outside-log.jsonl"
        return resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", redirected)
    output, stderr = invoke_main(
        module, {"hook_event_name": "SessionStart", "cwd": str(root)}, monkeypatch, capsys
    )
    assert "hookSpecificOutput" in output
    assert "Hook event log unavailable: ValueError" in stderr
    assert not log_path.exists()
    assert not (root.parent / "outside-log.jsonl").exists()


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
