"""Loopback-only HTTP adapter; analysis remains in the validated Python pipeline."""

import json
import secrets
import threading
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from .analysis import analyze
from .demo import run_demo
from .errors import InputError, ProviderError, ResponseError
from .gemini import GeminiProvider
from .models import Profile, StrictModel

MAX_BODY_BYTES = 160 * 1024
MAX_INPUT_BYTES = 64 * 1024
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def failure(code, message, status):
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


class AnalysisRequest(StrictModel):
    text: str
    profile: Profile | None = None
    prompt_variant: Literal["zero-shot", "few-shot"] = "zero-shot"


class LocalSecurityMiddleware:
    def __init__(self, app, *, port, token):
        self.app = app
        self.hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        self.origins = {f"http://{host}" for host in self.hosts}
        self.token = token

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {}
        for key, value in scope.get("headers", []):
            headers.setdefault(key.lower(), []).append(value.decode("latin-1"))
        hosts = headers.get(b"host", [])
        origins = headers.get(b"origin", [])
        denied = (
            len(hosts) != 1
            or hosts[0].lower() not in self.hosts
            or len(origins) > 1
            or (bool(origins) and origins[0] not in self.origins)
        )
        if scope["method"] == "POST":
            tokens = headers.get(b"x-session-token", [])
            denied = denied or (
                len(origins) != 1
                or len(tokens) != 1
                or not secrets.compare_digest(
                    tokens[0].encode("latin-1"), self.token.encode("ascii")
                )
            )

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    [
                        (b"cache-control", b"no-store"),
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"no-referrer"),
                        (
                            b"content-security-policy",
                            (
                                b"default-src 'self'; script-src 'self'; "
                                b"style-src 'self' 'unsafe-inline'; "
                                b"font-src 'self'; img-src 'self' data:; connect-src 'self'; "
                                b"frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
                            ),
                        ),
                    ]
                )
            await send(message)

        if denied:
            await failure("forbidden", "This request must come from the local workspace.", 403)(
                scope, receive, secure_send
            )
            return
        if scope["method"] == "POST":
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                if len(body) + len(chunk) > MAX_BODY_BYTES:
                    await failure("body_too_large", "Request exceeds the 160 KiB limit.", 413)(
                        scope, receive, secure_send
                    )
                    return
                body.extend(chunk)
                if not message.get("more_body", False):
                    break

            async def replay():
                return {"type": "http.request", "body": bytes(body), "more_body": False}

            await self.app(scope, replay, secure_send)
        else:
            await self.app(scope, receive, secure_send)


def create_app(*, port=8000, provider=None, frontend_dir=None):
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        telemetry={
            "tracing": False,
            "metrics": False,
            "logs": False,
            "operation_spans": False,
            "auto_configure": False,
        },
    )
    app.state.provider = provider if provider is not None else GeminiProvider(max_attempts=24)
    app.state.analysis_lock = threading.Lock()
    token = secrets.token_urlsafe(32)
    frontend = Path(frontend_dir if frontend_dir is not None else FRONTEND_DIR).resolve()
    app.add_middleware(LocalSecurityMiddleware, port=port, token=token)

    @app.get("/api/session")
    def session():
        return {
            "token": token,
            "attempts_remaining": max(0, 24 - app.state.provider.attempts_used),
            "max_attempts": 24,
        }

    @app.get("/api/demo")
    def demo():
        return run_demo().model_dump(mode="json")

    @app.post("/api/analyze")
    async def analysis(request: Request):
        try:
            payload = json.loads(await request.body())
            if isinstance(payload, dict) and payload.get("profile") is not None:
                profile_size = len(
                    json.dumps(payload["profile"], ensure_ascii=False).encode("utf-8")
                )
                if profile_size > MAX_INPUT_BYTES:
                    raise ValueError
            submitted = AnalysisRequest.model_validate(payload)
            if not submitted.text.strip() or len(submitted.text.encode("utf-8")) > MAX_INPUT_BYTES:
                raise ValueError
        except (ValueError, ValidationError, UnicodeError, RecursionError):
            return failure(
                "invalid_input", "Check job text, profile fields and the 64 KiB input limits.", 422
            )
        if not app.state.analysis_lock.acquire(blocking=False):
            return failure("busy", "Another analysis is running. Wait for it to finish.", 429)
        try:
            if app.state.provider.attempts_used >= 24:
                return failure(
                    "budget_exhausted", "This server run has reached its 24-attempt limit.", 429
                )
            report = await run_in_threadpool(
                analyze,
                submitted.text,
                profile=submitted.profile,
                provider=app.state.provider,
                prompt_variant=submitted.prompt_variant,
            )
            return report.model_dump(mode="json")
        except InputError:
            return failure("configuration", "Set GEMINI_API_KEY locally before live analysis.", 422)
        except ProviderError:
            if app.state.provider.attempts_used >= 24:
                return failure(
                    "budget_exhausted", "This server run has reached its 24-attempt limit.", 429
                )
            return failure(
                "provider",
                "Gemini request failed. Check access, quota, authentication or network.",
                502,
            )
        except ResponseError:
            return failure(
                "invalid_response",
                "The model response failed validation. No report was accepted.",
                422,
            )
        except Exception:
            return failure("internal", "Analysis failed unexpectedly. No report was accepted.", 500)
        finally:
            app.state.analysis_lock.release()

    @app.get("/{path:path}")
    def static(path: str):
        if path.startswith("api/"):
            return failure("not_found", "Endpoint not found.", 404)
        try:
            target = (frontend / (path or "index.html")).resolve()
        except (ValueError, OSError):
            return failure("not_found", "File not found.", 404)
        if not target.is_relative_to(frontend) or not target.is_file():
            if not path and not (frontend / "index.html").is_file():
                return failure(
                    "frontend_missing",
                    "Build the frontend first: cd frontend; npm ci; npm run build.",
                    503,
                )
            return failure("not_found", "File not found.", 404)
        return FileResponse(target)

    return app


def serve(port=8000):
    import uvicorn

    uvicorn.run(create_app(port=port), host="127.0.0.1", port=port, access_log=False)
