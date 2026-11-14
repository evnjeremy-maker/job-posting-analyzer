import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_verify():
    spec = importlib.util.spec_from_file_location("verify", ROOT / "scripts/verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verification_stops_on_first_failure():
    module = load_verify()
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        assert kwargs["cwd"] == ROOT
        return subprocess.CompletedProcess(command, 1)

    assert module.verify(runner=runner) == 1
    assert len(calls) == 1
