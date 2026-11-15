"""One lazily initialized Gemini integration with a bounded request budget."""

import json
import os
import time

from pydantic import ValidationError

from .errors import InputError, ProviderError, ResponseError
from .models import ComparisonItem, JobAnalysis, StrictModel
from .prompts import COMPARISON_RULES, extraction_data, extraction_instructions

MODEL = "gemini-3.1-flash-lite"


class ComparisonResponse(StrictModel):
    items: list[ComparisonItem]


class GeminiProvider:
    model = MODEL

    def __init__(self, *, max_attempts=24, client=None):
        self._client = client
        self.max_attempts = max_attempts
        self.attempts_used = 0
        self.last_usage = None

    def extract(self, text, variant="zero-shot"):
        return self._generate(extraction_data(text), extraction_instructions(variant), JobAnalysis)

    def compare(self, text, analysis, profile):
        from .evidence import requirement_map

        data = json.dumps(
            {
                "advertisement_data": text,
                "qualifications": {
                    key: value.model_dump() for key, value in requirement_map(analysis).items()
                },
                "profile_data": profile.model_dump(),
            },
            ensure_ascii=False,
        )
        return self._generate(data, COMPARISON_RULES, ComparisonResponse).items

    def _generate(self, data, instruction, schema):
        from google import genai
        from google.genai import types

        if not os.environ.get("GEMINI_API_KEY") and self._client is None:
            raise InputError("Set GEMINI_API_KEY locally before live analysis.")
        if self._client is None:
            self._client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"],
                vertexai=False,
                http_options=types.HttpOptions(
                    base_url="https://generativelanguage.googleapis.com",
                    timeout=30000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        self.last_usage = None
        for attempt in range(3):
            if self.attempts_used >= self.max_attempts:
                raise ProviderError("Development request attempt budget exhausted.", terminal=True)
            self.attempts_used += 1
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=data,
                    config=types.GenerateContentConfig(
                        system_instruction=instruction,
                        response_mime_type="application/json",
                        response_schema=schema,
                        max_output_tokens=8192,
                    ),
                )
                break
            except Exception as error:
                code = getattr(error, "code", None)
                quota = "perday" in str(error).lower() or "daily" in str(error).lower()
                transient = (
                    code in {408, 429, 500, 502, 503, 504}
                    or isinstance(error, (TimeoutError, ConnectionError, OSError))
                    or type(error).__name__ in {"ConnectError", "ReadTimeout", "ConnectTimeout"}
                )
                if not transient or quota or attempt == 2:
                    raise ProviderError(
                        "Gemini request failed; check authentication, access, quota, or network.",
                        terminal=quota or code in {400, 401, 403, 404},
                    ) from None
                time.sleep(attempt + 1)
        candidates = getattr(response, "candidates", None)
        if (
            not candidates
            or str(getattr(candidates[0], "finish_reason", None)).split(".")[-1] != "STOP"
        ):
            raise ResponseError("Gemini response was blocked, incomplete, or empty.")
        try:
            result = schema.model_validate_json(response.text)
        except (ValidationError, ValueError, TypeError):
            raise ResponseError("Gemini returned an invalid response schema.") from None
        usage = getattr(response, "usage_metadata", None)
        if usage is not None:
            self.last_usage = {
                "input_tokens": getattr(usage, "prompt_token_count", None),
                "output_tokens": getattr(usage, "candidates_token_count", None),
                "total_tokens": getattr(usage, "total_token_count", None),
            }
        return result
