import asyncio
import json
import threading

import httpx
import pytest

from job_posting_analyzer.demo import JOB_TEXT, PROFILE_DATA, SimulatedProvider
from job_posting_analyzer.errors import ProviderError, ResponseError

ORIGIN = "http://127.0.0.1:8000"
LOOPS = []


@pytest.fixture(scope="session", autouse=True)
def asgi_event_loops():
    # Windows creates a socket pair for loop wakeups before the per-test network ban.
    LOOPS.extend(asyncio.new_event_loop() for _ in range(2))
    yield
    for loop in LOOPS:
        loop.close()
    LOOPS.clear()


def run_async(coroutine):
    index = 0 if threading.current_thread() is threading.main_thread() else 1
    return LOOPS[index].run_until_complete(coroutine)


class FixtureProvider(SimulatedProvider):
    max_attempts = 24
    attempts_used = 0

    def extract(self, text, variant):
        self.attempts_used += 1
        return super().extract(text, variant)

    def compare(self, text, analysis, profile):
        self.attempts_used += 1
        return super().compare(text, analysis, profile)


def request(app, method, path, **kwargs):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url=ORIGIN
        ) as client:
            return await client.request(method, path, **kwargs)

    return run_async(run())


@pytest.fixture
def app(tmp_path):
    from job_posting_analyzer.web import create_app

    frontend = tmp_path / "dist"
    frontend.mkdir()
    (frontend / "index.html").write_text("<h1>Fictional workspace</h1>", encoding="utf-8")
    return create_app(provider=FixtureProvider(), frontend_dir=frontend)


def headers(app):
    session = request(app, "GET", "/api/session").json()
    return {"Origin": ORIGIN, "X-Session-Token": session["token"]}


def test_demo_needs_no_credentials_or_budget(app, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = request(app, "GET", "/api/demo")
    assert response.status_code == 200
    assert response.json()["simulated"] is True
    assert request(app, "GET", "/api/session").json()["attempts_remaining"] == 24
    assert response.headers["cache-control"] == "no-store"
    assert "access-control-allow-origin" not in response.headers


def test_analysis_uses_validated_pipeline_and_shared_attempt_budget(app):
    response = request(
        app,
        "POST",
        "/api/analyze",
        headers=headers(app),
        json={"text": JOB_TEXT, "profile": PROFILE_DATA},
    )
    assert response.status_code == 200
    report = response.json()
    assert report["schema_version"] == "1.0"
    assert [item["status"] for item in report["comparison"]] == [
        "matched",
        "partial",
        "matched",
        "missing",
    ]
    assert request(app, "GET", "/api/session").json()["attempts_remaining"] == 22


@pytest.mark.parametrize(
    "changes",
    [
        {"text": " "},
        {"text": "x" * 65537},
        {"text": "\ud800"},
        {"text": "x", "profile": {"unknown": []}},
        {"text": "x", "profile": {"skills": ["x" * 65536]}},
        {"text": "x", "prompt_variant": "unknown"},
        {"path": "C:/private.txt"},
    ],
)
def test_invalid_inputs_are_rejected_before_provider(app, changes):
    response = request(
        app, "POST", "/api/analyze", headers=headers(app), content=json.dumps(changes)
    )
    assert response.status_code == 422
    assert request(app, "GET", "/api/session").json()["attempts_remaining"] == 24


@pytest.mark.parametrize("origin", ["https://evil.example", "null", "http://localhost:8001"])
def test_cross_origin_requests_are_denied(app, origin):
    response = request(
        app,
        "POST",
        "/api/analyze",
        headers={**headers(app), "Origin": origin},
        json={"text": JOB_TEXT},
    )
    assert response.status_code == 403


@pytest.mark.parametrize("host", ["evil.example", "127.0.0.1.evil.example:8000", "localhost:8001"])
def test_nonlocal_or_wrong_port_hosts_are_denied(app, host):
    assert request(app, "GET", "/api/session", headers={"Host": host}).status_code == 403


def test_origin_and_token_both_required_for_analysis(app):
    assert request(app, "POST", "/api/analyze", json={"text": JOB_TEXT}).status_code == 403
    assert (
        request(
            app, "POST", "/api/analyze", headers={"Origin": ORIGIN}, json={"text": JOB_TEXT}
        ).status_code
        == 403
    )


def test_non_ascii_token_is_rejected_without_an_exception(app):
    response = request(
        app,
        "POST",
        "/api/analyze",
        headers=[(b"origin", ORIGIN.encode()), (b"x-session-token", b"\xff")],
        json={"text": JOB_TEXT},
    )
    assert response.status_code == 403
    assert (
        request(
            app,
            "POST",
            "/api/analyze",
            headers={"X-Session-Token": headers(app)["X-Session-Token"]},
            json={"text": JOB_TEXT},
        ).status_code
        == 403
    )


def test_oversized_and_chunked_bodies_are_bounded(app):
    assert (
        request(
            app, "POST", "/api/analyze", headers=headers(app), content=b"x" * (160 * 1024 + 1)
        ).status_code
        == 413
    )

    auth = headers(app)

    async def run():
        async def chunks():
            for _ in range(3):
                yield b"x" * 65536

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url=ORIGIN
        ) as client:
            return await client.post("/api/analyze", headers=auth, content=chunks())

    assert run_async(run()).status_code == 413


@pytest.mark.parametrize("content", [b"not json", b"\xff", b"[", b"[" * 10000])
def test_malformed_json_is_sanitized(app, content):
    response = request(app, "POST", "/api/analyze", headers=headers(app), content=content)
    assert response.status_code == 422
    assert set(response.json()) == {"error"}


@pytest.mark.parametrize(
    "failure,status",
    [
        (ProviderError("private payload"), 502),
        (ResponseError("private payload"), 422),
        (RuntimeError("private payload"), 500),
    ],
)
def test_provider_and_evidence_errors_are_sanitized(app, monkeypatch, failure, status):
    import job_posting_analyzer.web as web

    def fail(*args, **kwargs):
        raise failure

    monkeypatch.setattr(web, "analyze", fail)
    response = request(app, "POST", "/api/analyze", headers=headers(app), json={"text": JOB_TEXT})
    assert response.status_code == status
    assert "private payload" not in response.text


def test_budget_exhaustion_prevents_provider_request(app):
    app.state.provider.attempts_used = 24
    response = request(app, "POST", "/api/analyze", headers=headers(app), json={"text": JOB_TEXT})
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "budget_exhausted"
    assert app.state.provider.attempts_used == 24


def test_overlapping_analysis_is_rejected_without_second_request(app, monkeypatch):
    import job_posting_analyzer.web as web

    entered, release = threading.Event(), threading.Event()
    original = web.analyze

    def slow(*args, **kwargs):
        entered.set()
        assert release.wait(3)
        return original(*args, **kwargs)

    monkeypatch.setattr(web, "analyze", slow)
    auth = headers(app)
    results = []
    worker = threading.Thread(
        target=lambda: results.append(
            request(app, "POST", "/api/analyze", headers=auth, json={"text": JOB_TEXT})
        )
    )
    worker.start()
    try:
        assert entered.wait(2)
        response = request(app, "POST", "/api/analyze", headers=auth, json={"text": JOB_TEXT})
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "busy"
    finally:
        release.set()
        worker.join(3)
    assert results[0].status_code == 200


def test_static_frontend_is_served_without_exposing_repo(app):
    assert "Fictional workspace" in request(app, "GET", "/").text
    assert request(app, "GET", "/AGENTS.md").status_code == 404
    assert request(app, "GET", "/api/not-a-route").status_code == 404
    assert request(app, "GET", "/%2e%2e/AGENTS.md").status_code == 404
    assert request(app, "GET", "/bad%00path").status_code == 404


def test_real_evidence_validation_rejects_invented_source_quotes(app):
    class InvalidProvider(FixtureProvider):
        def extract(self, text, variant):
            result = super().extract(text, variant)
            result.required[0].quote = "This text was never in the advertisement."
            return result

    app.state.provider = InvalidProvider()
    response = request(app, "POST", "/api/analyze", headers=headers(app), json={"text": JOB_TEXT})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_response"


def test_session_tokens_are_unique_per_launch(tmp_path):
    from job_posting_analyzer.web import create_app

    apps = [create_app(frontend_dir=tmp_path) for _ in range(2)]
    tokens = [request(app, "GET", "/api/session").json()["token"] for app in apps]
    assert tokens[0] != tokens[1]


def test_telemetry_remains_disabled_despite_environment_opt_in(monkeypatch, tmp_path):
    from job_posting_analyzer.web import create_app

    monkeypatch.setenv("FASTAPI_OTEL_AUTO_CONFIGURE", "true")
    app = create_app(frontend_dir=tmp_path)
    for setting in ("tracing", "metrics", "logs", "operation_spans", "auto_configure"):
        assert app._telemetry[setting] is False


def test_serve_cli_binds_only_loopback(monkeypatch):
    import uvicorn

    from job_posting_analyzer import cli

    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: calls.append(kwargs))
    assert cli.main(["serve", "--port", "8123"]) == 0
    assert calls == [{"host": "127.0.0.1", "port": 8123, "access_log": False}]


@pytest.mark.parametrize("port", ["0", "65536", "bad"])
def test_serve_rejects_invalid_ports(port):
    from job_posting_analyzer.cli import main

    with pytest.raises(SystemExit) as error:
        main(["serve", "--port", port])
    assert error.value.code == 2
