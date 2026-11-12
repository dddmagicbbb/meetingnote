"""설정 값. 비밀값은 프로젝트 루트의 .env 에서만 읽는다."""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

load_dotenv(PROJECT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'meetingnote.db').as_posix()}")

# 업로드 제한 (02-specs 5. 검증)
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {".mp3": "audio/mp3", ".wav": "audio/wav"}

# 이 길이 미만의 본문은 세 갈래 구분을 부르지 않는다 (02-specs 7. 실패 처리)
MIN_CLASSIFY_LENGTH = 20
