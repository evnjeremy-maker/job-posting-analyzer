"""Run bounded offline checks from the repository root."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(*, runner=subprocess.run):
    checks = [
        ([sys.executable, "-m", "ruff", "check", "."], 10),
        ([sys.executable, "-m", "ruff", "format", "--check", "."], 10),
        ([sys.executable, "-m", "pytest", "-q"], 25),
    ]
    for command, timeout in checks:
        try:
            result = runner(command, cwd=ROOT, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"Check failed: {type(error).__name__}", file=sys.stderr)
            return 1
        if result.returncode:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(verify())
