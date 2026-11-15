import importlib
import subprocess
import sys
from pathlib import Path

import pytest


def test_help_works_without_provider_configuration(capsys):
    cli = importlib.import_module("job_posting_analyzer.cli")
    with pytest.raises(SystemExit) as error:
        cli.main(["--help"])
    assert error.value.code == 0
    assert "analyze" in capsys.readouterr().out


def test_offline_demo_has_validated_simulated_output(capsys):
    cli = importlib.import_module("job_posting_analyzer.cli")
    assert cli.main(["demo"]) == 0
    output = capsys.readouterr().out
    assert "SIMULATED" in output
    assert "SQL" in output
    assert "Partial" in output
    assert "quality has not been assessed" in output


def test_missing_input_is_an_error_before_analysis(monkeypatch, capsys, tmp_path):
    from job_posting_analyzer import analysis

    def forbidden(*args, **kwargs):
        pytest.fail("Analysis must not run for an unreadable input.")

    monkeypatch.setattr(analysis, "analyze", forbidden)
    cli = importlib.import_module("job_posting_analyzer.cli")
    assert cli.main(["analyze", str(tmp_path / "missing.txt")]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Input file could not be read" in captured.err


def test_demo_writes_validated_json_and_refuses_overwrite(capsys, tmp_path):
    from job_posting_analyzer.models import Report

    cli = importlib.import_module("job_posting_analyzer.cli")
    path = tmp_path / "demo report.json"
    assert cli.main(["demo", "--json", str(path)]) == 0
    parsed = Report.model_validate_json(path.read_text(encoding="utf-8"))
    assert parsed.simulated is True
    original = path.read_bytes()
    assert cli.main(["demo", "--json", str(path)]) == 5
    assert path.read_bytes() == original
    assert "--overwrite" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("error_name", "expected_code"),
    [("InputError", 2), ("ProviderError", 3), ("ResponseError", 4)],
)
def test_analysis_failures_have_correct_exit_codes(
    monkeypatch, capsys, tmp_path, error_name, expected_code
):
    from job_posting_analyzer import analysis, errors

    def failure(*args, **kwargs):
        raise getattr(errors, error_name)("Controlled failure\x1b[31m")

    monkeypatch.setattr(analysis, "analyze", failure)
    job = tmp_path / "job with spaces.txt"
    job.write_text("Fictional advertisement", encoding="utf-8")
    cli = importlib.import_module("job_posting_analyzer.cli")
    assert cli.main(["analyze", str(job)]) == expected_code
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "\\x1b" in captured.err
    assert "\x1b" not in captured.err


def test_evaluation_dispatch_is_explicit_and_prints_results(monkeypatch, capsys):
    import sys
    from types import SimpleNamespace

    calls = []

    def evaluate(**kwargs):
        calls.append(kwargs)
        return {"simulated": True, "cases": 3}

    monkeypatch.setitem(
        sys.modules, "job_posting_analyzer.evaluation", SimpleNamespace(run_evaluation=evaluate)
    )
    cli = importlib.import_module("job_posting_analyzer.cli")
    assert cli.main(["evaluate", "--offline", "--split", "holdout", "--max-requests", "6"]) == 0
    assert calls == [{"live": False, "split": "holdout", "max_requests": 6}]
    assert '"simulated": true' in capsys.readouterr().out


@pytest.mark.parametrize("target_name", ["job.txt", "profile.json"])
def test_analysis_cannot_overwrite_its_inputs(monkeypatch, capsys, tmp_path, target_name):
    from job_posting_analyzer import analysis

    job = tmp_path / "job.txt"
    profile = tmp_path / "profile.json"
    job.write_text("Fictional advertisement", encoding="utf-8")
    profile.write_text("{}", encoding="utf-8")
    before = {path: path.read_bytes() for path in (job, profile)}

    def forbidden(*args, **kwargs):
        pytest.fail("Provider must not run when output aliases an input.")

    monkeypatch.setattr(analysis, "analyze", forbidden)
    cli = importlib.import_module("job_posting_analyzer.cli")
    assert (
        cli.main(
            [
                "analyze",
                str(job),
                "--profile",
                str(profile),
                "--json",
                str(tmp_path / target_name),
                "--overwrite",
            ]
        )
        == 5
    )
    assert {path: path.read_bytes() for path in (job, profile)} == before
    assert "input file" in capsys.readouterr().err


@pytest.mark.parametrize("alias_kind", ["resolved-parent", "same-file-identity"])
def test_input_aliases_are_protected(monkeypatch, tmp_path, alias_kind):
    from job_posting_analyzer.cli import protect_input_paths
    from job_posting_analyzer.errors import OutputError

    source = tmp_path / "source.txt"
    target = tmp_path / "alias.json"
    source.write_text("Source remains intact", encoding="utf-8")
    target.write_text("Other fictional file", encoding="utf-8")
    if alias_kind == "resolved-parent":
        resolve = Path.resolve

        def resolved(path, *args, **kwargs):
            return resolve(source) if path == target else resolve(path, *args, **kwargs)

        monkeypatch.setattr(Path, "resolve", resolved)
    else:
        monkeypatch.setattr(Path, "samefile", lambda first, second: True)
    with pytest.raises(OutputError):
        protect_input_paths(target, [source])
    assert source.read_text(encoding="utf-8") == "Source remains intact"


def test_module_entrypoint_displays_help():
    result = subprocess.run(
        [sys.executable, "-m", "job_posting_analyzer", "--help"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    assert "analyze" in result.stdout


def test_redirected_demo_uses_utf8_even_with_ascii_environment():
    import os
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "job_posting_analyzer", "demo"],
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
        capture_output=True,
        check=False,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "SIMULATED DEMONSTRATION" in result.stdout.decode("utf-8")
