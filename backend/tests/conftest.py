"""테스트 공통 준비. 앱을 불러오기 전에 테스트 전용 DB 로 바꾼다."""

import os
import tempfile
import time
from pathlib import Path

_TEST_DB = Path(tempfile.gettempdir()) / "meetingnote_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"

import pytest  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app import models  # noqa: E402,F401  (테이블 등록)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def gemini_pause():
    """Gemini 를 부르는 테스트는 한도에 걸리지 않게 호출 사이를 1초쯤 띄운다 (05-conventions)."""
    yield
    time.sleep(1)
