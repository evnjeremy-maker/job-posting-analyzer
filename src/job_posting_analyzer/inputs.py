"""Bounded local reads and output preflight without touching destinations."""

import json
import os
from pathlib import Path

from pydantic import ValidationError

from .errors import InputError, OutputError
from .models import Profile

MAX_INPUT_BYTES = 64 * 1024


def _read_text(path: str | Path) -> str:
    try:
        with Path(path).open("rb") as stream:
            content = stream.read(MAX_INPUT_BYTES + 1)
    except (OSError, ValueError, TypeError):
        raise InputError("Input file could not be read.") from None
    if len(content) > MAX_INPUT_BYTES:
        raise InputError("Input file exceeds the 64 KiB limit.")
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("Input file must contain valid UTF-8 text.") from None


def read_job(path: str | Path) -> str:
    text = _read_text(path)
    if not text.strip():
        raise InputError("Job advertisement must not be empty.")
    return text


def read_profile(path: str | Path) -> Profile:
    text = _read_text(path)
    try:
        return Profile.model_validate(json.loads(text))
    except (ValueError, ValidationError, RecursionError):
        raise InputError("Profile JSON does not match the expected schema.") from None


def preflight_output(path: str | Path, overwrite: bool = False) -> None:
    try:
        target = Path(path)
        if target.is_symlink():
            raise OutputError("Output destination must not be a symbolic link.")
        if target.exists():
            if not target.is_file():
                raise OutputError("Output destination must be a regular file.")
            if not overwrite:
                raise OutputError("Output file exists; use --overwrite to replace it.")
        if not target.parent.is_dir() or not os.access(target.parent, os.W_OK):
            raise OutputError("Output parent directory is missing or not writable.")
    except (OSError, ValueError, TypeError):
        raise OutputError("Output destination could not be checked.") from None
