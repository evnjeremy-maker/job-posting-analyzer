import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def policy():
    spec = importlib.util.spec_from_file_location(
        "danger_policy", ROOT / "scripts/danger_policy.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blocks_shell_deletion():
    result = policy().evaluate(
        {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": "Remove-Item file.txt"}},
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf .",
        "DEL /s /q file.txt",
        "rmdir /s folder",
        "rd folder",
        "erase file",
        "& 'Remove`-Item' file.txt",
        "ri file.txt",
        "git reset --hard HEAD",
        "git clean -fd",
        "git push --force",
        "git push -f origin main",
        "git push --force-with-lease",
        "git branch -D feature",
        "git restore src/main.py",
        "git checkout -- src/main.py",
        "format D:",
        "diskpart",
        "shutdown /s",
        "reg delete HKCU\\Example",
        "powershell -EncodedCommand ZXhhbXBsZQ==",
        "pwsh -enc ABC",
        "Set-Content -LiteralPath C:\\outside.txt value",
        "Move-Item a b",
    ],
)
def test_blocks_recognizable_dangerous_commands(command):
    result = policy().evaluate(
        {"tool_name": "exec_command", "cwd": str(ROOT), "tool_input": {"cmd": command}},
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "path",
    [
        "../outside.txt",
        "C:relative.txt",
        "C:\\outside.txt",
        "\\\\server\\share\\file.txt",
        ".git/config",
        ".codex/hooks.json",
        "AGENTS.md",
        "scripts/danger_policy.py",
        "scripts/codex_hook.py",
    ],
)
def test_blocks_outside_or_protected_patch_paths(path):
    result = policy().evaluate(
        {
            "tool_name": "apply_patch",
            "cwd": str(ROOT),
            "tool_input": {"command": f"*** Begin Patch\n*** Add File: {path}\n+x\n*** End Patch"},
        },
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "header",
    [
        "*** Delete File: src/example.py",
        "*** Update File: src/example.py\n*** Move to: src/other.py",
    ],
)
def test_blocks_patch_deletion_and_moves(header):
    result = policy().evaluate(
        {
            "tool_name": "apply_patch",
            "cwd": str(ROOT),
            "tool_input": f"*** Begin Patch\n{header}\n*** End Patch",
        },
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content README.md",
        "rg TODO src",
        "git status",
        "git diff --cached",
        "git checkout -b feature",
        ".venv/Scripts/python.exe -m pytest -q",
        ".venv/Scripts/python.exe -m ruff check .",
    ],
)
def test_allows_normal_development_commands(command):
    assert (
        policy().evaluate(
            {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": command}}, ROOT
        )
        == {}
    )


def test_allows_regular_patch():
    assert (
        policy().evaluate(
            {
                "tool_name": "apply_patch",
                "cwd": str(ROOT),
                "tool_input": "*** Begin Patch\n*** Add File: src/example.py\n+x\n*** End Patch",
            },
            ROOT,
        )
        == {}
    )


def test_blocks_outside_shell_workdir():
    result = policy().evaluate(
        {
            "tool_name": "exec_command",
            "cwd": str(ROOT),
            "tool_input": {"cmd": "git status", "workdir": str(ROOT.parent)},
        },
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_blocks_direct_write_outside_root():
    result = policy().evaluate(
        {
            "tool_name": "Write",
            "cwd": str(ROOT),
            "tool_input": {"file_path": str(ROOT.parent / "outside.txt"), "content": "x"},
        },
        ROOT,
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "python -c \"import shutil; shutil.rmtree('folder')\"",
        "python -c \"import os; os.unlink('file')\"",
        "python -c \"import os; os.remove('file')\"",
        "python -c \"import os; os.rmdir('folder')\"",
        "python -c \"Path('file').unlink()\"",
        "python -c \"Path('folder').rmdir()\"",
        "git -C . reset --hard HEAD",
        "GIT RESET --HARD HEAD",
    ],
)
def test_blocks_obvious_inline_deletion_and_git_variants(command):
    result = policy().evaluate(
        {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": command}}, ROOT
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize("event", [{}, {"tool_name": None}, {"tool_name": 5}])
def test_blocks_malformed_tool_identity(event):
    result = policy().evaluate(event, ROOT)
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_blocks_resolved_outside_target(monkeypatch):
    original = Path.resolve
    target = ROOT / "src/example.py"

    def resolve(path, *args, **kwargs):
        if path == target:
            return ROOT.parent / "outside.py"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    result = policy().evaluate(
        {"tool_name": "Write", "cwd": str(ROOT), "tool_input": {"file_path": str(target)}}, ROOT
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        ".venv/Scripts/python.exe -m ruff format .",
        "python -c \"print('{}'.format(1))\"",
    ],
)
def test_allows_development_format_operations(command):
    assert (
        policy().evaluate(
            {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": command}}, ROOT
        )
        == {}
    )


@pytest.mark.parametrize(
    "command",
    [
        "format D:",
        "FORMAT D:",
        '"C:\\Windows\\System32\\format.com" D:',
        "& 'C:\\Windows\\System32\\format.exe' D:",
        "cmd /c format D:",
    ],
)
def test_blocks_disk_format_command_variants(command):
    result = policy().evaluate(
        {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": command}}, ROOT
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "Remove-Item('fictional.txt')",
        "rd/s/q fictional",
        "del/q fictional.txt",
        "git checkout -f HEAD",
        "git checkout --force HEAD",
        "git push origin +main",
    ],
)
def test_blocks_direct_deletion_syntax_and_force_git_variants(command):
    result = policy().evaluate(
        {"tool_name": "Bash", "cwd": str(ROOT), "tool_input": {"command": command}}, ROOT
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_allows_safe_merged_branch_deletion():
    assert (
        policy().evaluate(
            {
                "tool_name": "Bash",
                "cwd": str(ROOT),
                "tool_input": {"command": "git branch -d merged-feature"},
            },
            ROOT,
        )
        == {}
    )
