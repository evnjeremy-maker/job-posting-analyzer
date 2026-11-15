from pathlib import Path
from uuid import uuid4

import pytest

from job_posting_analyzer.errors import InputError, OutputError
from job_posting_analyzer.inputs import preflight_output, read_job, read_profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def work():
    path = ROOT / ".cache/input-tests" / uuid4().hex
    path.mkdir(parents=True)
    return path


def test_reads_unicode_job_and_profile(work):
    job = work / "job.txt"
    profile = work / "profile.json"
    job.write_text("Développer Python", encoding="utf-8")
    profile.write_text('{"skills": ["Python basics"]}', encoding="utf-8")
    assert read_job(job) == "Développer Python"
    assert read_profile(profile).skills == ["Python basics"]


def test_preflight_does_not_create_or_overwrite(work):
    output = work / "report.json"
    preflight_output(output)
    assert not output.exists()
    output.write_text("existing", encoding="utf-8")
    with pytest.raises(OutputError):
        preflight_output(output)
    preflight_output(output, overwrite=True)
    assert output.read_text(encoding="utf-8") == "existing"


@pytest.mark.parametrize("content", [b"", b" \n\t", b"\xff", b"x" * 65537])
def test_rejects_invalid_job_input(work, content):
    path = work / "job.txt"
    path.write_bytes(content)
    with pytest.raises(InputError):
        read_job(path)


def test_accepts_exact_byte_limit_and_rejects_missing_file_and_directory(work):
    path = work / "job.txt"
    path.write_bytes(b"x" * 65536)
    assert len(read_job(path)) == 65536
    with pytest.raises(InputError):
        read_job(work / "not-present.txt")
    with pytest.raises(InputError):
        read_job(work)


@pytest.mark.parametrize("content", ['{"skills": "PRIVATE"}', '["PRIVATE"]', "PRIVATE", "[" * 1500])
def test_profile_errors_do_not_echo_input(work, content):
    path = work / "profile.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(InputError) as error:
        read_profile(path)
    assert "PRIVATE" not in str(error.value)


def test_preflight_rejects_directory_and_missing_parent(work):
    with pytest.raises(OutputError):
        preflight_output(work, overwrite=True)
    with pytest.raises(OutputError):
        preflight_output(work / "absent" / "report.json")


@pytest.mark.parametrize("prefix,suffix", [("", ""), ('{"skills":', "}")])
def test_deeply_nested_profile_is_a_sanitized_input_error(work, prefix, suffix):
    path = work / "deep-profile.json"
    path.write_text(prefix + "[" * 20000 + "]" * 20000 + suffix, encoding="utf-8")
    with pytest.raises(InputError) as error:
        read_profile(path)
    assert str(error.value) == "Profile JSON does not match the expected schema."


def test_profile_validation_recursion_is_a_sanitized_input_error(work, monkeypatch):
    from job_posting_analyzer.models import Profile

    path = work / "profile.json"
    path.write_text('{"skills": ["PRIVATE"]}', encoding="utf-8")

    def recursive_failure(*args, **kwargs):
        raise RecursionError("PRIVATE validation detail")

    monkeypatch.setattr(Profile, "model_validate", recursive_failure)
    with pytest.raises(InputError) as error:
        read_profile(path)
    assert str(error.value) == "Profile JSON does not match the expected schema."
