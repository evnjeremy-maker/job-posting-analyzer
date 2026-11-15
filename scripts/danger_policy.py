"""Bounded detection of recognizable dangerous operations, not a shell sandbox."""

import re
from pathlib import Path, PureWindowsPath

PROTECTED = {
    "agents.md",
    "scripts/danger_policy.py",
    "scripts/codex_hook.py",
    "scripts/pre_tool_guard.py",
}
SHELL_TOOLS = {"bash", "exec_command", "shell_command", "shell"}
WRITE_TOOLS = {"write", "edit", "write_file", "edit_file", "create_file"}
DELETE_TOOLS = {"delete_file", "delete_directory", "remove_file", "move_file", "move_directory"}


def safe_target(value, root, cwd):
    if not isinstance(value, str) or not value.strip():
        return False
    if value.startswith(("\\\\", "//")):
        return False
    windows = PureWindowsPath(value)
    if windows.drive and not windows.is_absolute():
        return False
    target = Path(value)
    if not target.is_absolute():
        target = cwd / target
    target = target.resolve()
    if not target.is_relative_to(root):
        return False
    relative = target.relative_to(root).as_posix().lower()
    return not (
        relative in PROTECTED or relative == "." or relative.split("/", 1)[0] in {".git", ".codex"}
    )


def shell_reason(command):
    normalized = command.replace("`", "").replace("'", "").replace('"', "")
    if re.search(
        r"(?<![\w-])(remove-item|ri|rm|del|erase|rmdir|rd)(?:\.exe)?(?=\s|\(|/|$)",
        normalized,
        re.I,
    ):
        return "Deletion commands are blocked by project policy."
    if re.search(
        r"\bshutil\s*\.\s*rmtree\s*\(|\bos\s*\.\s*(remove|unlink|rmdir)\s*\("
        r"|\.\s*(unlink|rmdir)\s*\(",
        normalized,
        re.I,
    ):
        return "Inline deletion code is blocked by project policy."
    if re.search(
        r"\bgit(?:\.exe)?\s+[^;|\n]*?\b(reset\b[^;|\n]*--hard|clean\b|restore\b|"
        r"checkout\b[^;|\n]*\s(?:--|--force|-f)(?:\s|$)|branch\b[^;|\n]*\s(?-i:-D)(?:\s|$)|"
        r"push\b[^;|\n]*\s(?:--force[^\s]*|-f)(?:\s|$)|push\b[^;|\n]*\s\+\S+)",
        normalized,
        re.I,
    ):
        return "Destructive Git operation is blocked by project policy."
    if re.search(
        r"\bformat(?:\.exe|\.com)?\s+(?:/\S+\s+)*[a-z]:|"
        r"(?:^|[;&|])\s*format(?:\.exe|\.com)?\s*$|"
        r"\b(diskpart|shutdown|stop-computer|restart-computer|stop-service|"
        r"set-service|sc|bcdedit|takeown|icacls)(?:\.exe)?(?=\s|$)|"
        r"\breg(?:\.exe)?\s+delete\b|-(?:enc|encodedcommand)\b",
        normalized,
        re.I,
    ):
        return "System changes or encoded shell commands are blocked by project policy."
    # Shell write targets cannot be resolved reliably without executing shell expressions.
    if re.search(
        r"\b(set-content|add-content|out-file|copy-item|move-item|new-item|"
        r"set-item|rename-item|clear-content|clear-item|tee-object)\b|(?<![<>])[>]+",
        normalized,
        re.I,
    ):
        return "Use a path-checked file edit tool instead of a shell write command."
    return None


def patch_reason(patch, root, cwd):
    if not isinstance(patch, str):
        return "Unrecognized patch input; no edit was authorized."
    paths = []
    for line in patch.splitlines():
        if line.startswith(("*** Delete File:", "*** Move to:")):
            return "Patch deletion and moves are blocked by project policy."
        for prefix in ("*** Add File: ", "*** Update File: "):
            if line.startswith(prefix):
                paths.append(line[len(prefix) :])
    if not paths or any(not safe_target(path, root, cwd) for path in paths):
        return "Patch targets must stay inside the project and avoid protected policy files."
    return None


def deny(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def evaluate(event, root):
    root = root.resolve()
    name = event.get("tool_name")
    if not isinstance(name, str) or not name.strip():
        return deny("Unrecognized tool identity; no operation was authorized.")
    tool = re.split(r"__|[.]", name)[-1].lower()
    raw_input = event.get("tool_input")
    data = raw_input if isinstance(raw_input, dict) else {}
    if tool not in SHELL_TOOLS | WRITE_TOOLS | DELETE_TOOLS | {"apply_patch"}:
        return {}
    cwd_value = event.get("cwd")
    if not isinstance(cwd_value, str) or not cwd_value or cwd_value.startswith(("\\\\", "//")):
        return deny("Unrecognized session working directory; no operation was authorized.")
    cwd = Path(cwd_value).resolve()
    workdir = data.get("workdir", cwd)
    if not isinstance(workdir, (str, Path)) or str(workdir).startswith(("\\\\", "//")):
        return deny("Tool working directory must remain inside the project.")
    workdir_path = Path(workdir)
    if not workdir_path.is_absolute():
        workdir_path = cwd / workdir_path
    if not workdir_path.resolve().is_relative_to(root):
        return deny("Tool working directory must remain inside the project.")
    if not cwd.is_relative_to(root):
        return deny("Session working directory must remain inside the project.")
    if tool in DELETE_TOOLS:
        return deny("Filesystem deletion and moves are blocked by project policy.")
    if tool in SHELL_TOOLS:
        command = data.get("command", data.get("cmd"))
        if not isinstance(command, str) or not command.strip():
            return deny("Unrecognized shell input; no command was authorized.")
        reason = shell_reason(command)
    elif tool == "apply_patch":
        patch = raw_input if isinstance(raw_input, str) else data.get("command", data.get("patch"))
        reason = patch_reason(patch, root, cwd)
    else:
        target = data.get("file_path", data.get("path"))
        reason = (
            None
            if safe_target(target, root, cwd)
            else ("File edits must stay inside the project and avoid protected policy files.")
        )
    if reason:
        return deny(reason)
    return {}
