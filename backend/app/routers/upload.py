"""녹취 파일 받아쓰기 - POST /api/upload (02-specs 3)."""

import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_AUDIO_TYPES, MAX_UPLOAD_BYTES
from app.schemas import UploadOut
from app.transcriber import transcribe
from app.gemini import GeminiError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadOut)
async def upload_audio(file: UploadFile = File(...)) -> UploadOut:
    suffix = Path(file.filename or "").suffix.lower()
    mime_type = ALLOWED_AUDIO_TYPES.get(suffix)
    if mime_type is None:
        raise HTTPException(status_code=415, detail="mp3, wav 파일만 받습니다")

    # 제한보다 1바이트 더 읽어 넘는지만 본다
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="25MB 이하 파일만 받습니다")

    try:
        text = transcribe(data, mime_type)
    except GeminiError:
        logger.exception("받아쓰기 실패")
        raise HTTPException(status_code=502, detail="받아쓰기 서비스 호출에 실패했습니다")
    return UploadOut(body=text)
