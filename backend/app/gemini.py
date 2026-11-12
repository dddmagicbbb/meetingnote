"""Gemini 호출. 클라이언트는 모듈에 한 번 만들어 재사용한다 (05-conventions 2. 금지)."""

import logging
import time
from functools import cache
from typing import Any

from google import genai
from google.genai import errors

from app.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# 429 · 503 이면 잠시 뒤 1번 다시 부른다 (02-specs 7. 실패 처리)
RETRY_STATUS_CODES = {429, 503}
RETRY_DELAY_SECONDS = 2.0


class GeminiError(Exception):
    """Gemini 호출이 끝내 실패했다."""


@cache
def get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY 가 .env 에 없습니다")
    return genai.Client(api_key=GEMINI_API_KEY)


def generate(contents: Any, config: Any = None) -> str:
    """모델을 불러 응답 텍스트를 돌려준다. 429 · 503 은 한 번 다시 부른다."""
    client = get_client()
    for attempt in (1, 2):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=contents, config=config)
            return response.text or ""
        except errors.APIError as exc:
            if exc.code in RETRY_STATUS_CODES and attempt == 1:
                logger.warning("Gemini %s - %s초 뒤 다시 부름", exc.code, RETRY_DELAY_SECONDS)
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise GeminiError(f"Gemini 호출 실패 ({exc.code})") from exc
    raise GeminiError("Gemini 호출 실패")  # 도달하지 않음
