"""2.9 POST /api/upload (05-conventions 테스트 매트릭스 12 · 13)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FIXTURE_WAV = Path(__file__).parent / "fixtures" / "meeting_ko.wav"


def test_mp4_returns_415():
    res = client.post("/api/upload", files={"file": ("meeting.mp4", b"\x00" * 100, "video/mp4")})
    assert res.status_code == 415


def test_30mb_returns_413():
    big = b"\x00" * (30 * 1024 * 1024)
    res = client.post("/api/upload", files={"file": ("meeting.wav", big, "audio/wav")})
    assert res.status_code == 413


def test_missing_file_returns_400():
    assert client.post("/api/upload").status_code == 400


@pytest.mark.usefixtures("gemini_pause")
def test_wav_is_transcribed():
    with FIXTURE_WAV.open("rb") as f:
        res = client.post("/api/upload", files={"file": ("meeting_ko.wav", f, "audio/wav")})
    assert res.status_code == 200, res.text
    body = res.json()["body"]
    assert "보도자료" in body
    assert "금요일" in body


def _padded_wav(target_bytes: int) -> bytes:
    """픽스처 음성 뒤에 무음을 붙여 target_bytes 크기의 WAV 를 만든다."""
    import io
    import wave
    with wave.open(str(FIXTURE_WAV), "rb") as src:
        params = src.getparams()
        frames = src.readframes(src.getnframes())
    out = io.BytesIO()
    with wave.open(out, "wb") as dst:
        dst.setparams(params)
        dst.writeframes(frames)
        dst.writeframes(b"\x00" * (target_bytes - len(frames) - 44))
    return out.getvalue()


@pytest.mark.usefixtures("gemini_pause")
def test_large_wav_goes_through_files_api():
    from app.transcriber import INLINE_LIMIT_BYTES
    data = _padded_wav(INLINE_LIMIT_BYTES + 1024 * 1024)
    assert INLINE_LIMIT_BYTES < len(data) <= 25 * 1024 * 1024
    res = client.post("/api/upload", files={"file": ("long.wav", data, "audio/wav")})
    assert res.status_code == 200, res.text
    assert "보도자료" in res.json()["body"]
