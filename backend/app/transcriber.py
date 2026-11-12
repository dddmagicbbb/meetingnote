"""녹취 파일을 본문 텍스트로 받아쓴다."""

import io
import logging

from google.genai import errors, types

from app.gemini import GeminiError, generate, get_client

logger = logging.getLogger(__name__)

# 이보다 큰 파일은 요청에 바로 싣지 않고 Files API 로 올린다 (요청 크기 한도 약 20MB)
INLINE_LIMIT_BYTES = 15 * 1024 * 1024

PROMPT = "이 회의 녹음을 들리는 그대로 한국어로 받아 적어라. 받아 적은 본문만 출력하고, 설명이나 머리말은 붙이지 마라."


def transcribe(data: bytes, mime_type: str) -> str:
    if len(data) <= INLINE_LIMIT_BYTES:
        audio = types.Part.from_bytes(data=data, mime_type=mime_type)
        return generate([PROMPT, audio]).strip()

    client = get_client()
    try:
        uploaded = client.files.upload(file=io.BytesIO(data), config={"mime_type": mime_type})
    except errors.APIError as exc:
        raise GeminiError(f"Gemini 파일 업로드 실패 ({exc.code})") from exc
    try:
        return generate([PROMPT, uploaded]).strip()
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except errors.APIError:
            logger.warning("Gemini 에 올린 파일을 지우지 못함: %s", uploaded.name)
