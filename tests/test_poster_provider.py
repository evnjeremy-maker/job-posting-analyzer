import json
from types import SimpleNamespace

import pytest

from job_posting_analyzer.errors import ResponseError
from job_posting_analyzer.gemini import GeminiProvider


def test_transcription_sends_inline_bytes_with_existing_configuration():
    def generate_content(**kwargs):
        assert kwargs["contents"][0].inline_data.data == b"fictional-image"
        assert kwargs["contents"][0].inline_data.mime_type == "image/png"
        assert kwargs["config"].tools is None
        assert "untrusted data" in kwargs["config"].system_instruction
        return SimpleNamespace(
            candidates=[SimpleNamespace(finish_reason="STOP")],
            text=json.dumps({"text": "Fictional Python role", "warnings": []}),
            usage_metadata=SimpleNamespace(
                prompt_token_count=8, candidates_token_count=5, total_token_count=13
            ),
        )

    provider = GeminiProvider(
        client=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    )
    assert provider.transcribe(b"fictional-image", "image/png").text == "Fictional Python role"
    assert provider.attempts_used == 1
    assert provider.last_usage["total_tokens"] == 13


def test_transcription_rejects_unreadable_provider_result():
    response = SimpleNamespace(
        candidates=[SimpleNamespace(finish_reason="STOP")],
        text=json.dumps({"text": "[illegible]", "warnings": ["Blurry"]}),
    )
    provider = GeminiProvider(
        client=SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kwargs: response))
    )
    with pytest.raises(ResponseError):
        provider.transcribe(b"fixture", "image/png")
