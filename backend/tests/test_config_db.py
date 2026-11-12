"""2.2 설정 읽기 · 2.3 DB 모델."""

from datetime import datetime

from sqlalchemy import text

from app import config
from app.database import SessionLocal, engine
from app.models import Meeting


def test_settings_loaded_from_env():
    assert config.GEMINI_API_KEY, ".env 의 GEMINI_API_KEY 를 읽지 못함"
    assert config.GEMINI_MODEL == "gemini-3.1-flash-lite"


def test_meeting_table_has_autoincrement():
    with engine.connect() as conn:
        ddl = conn.execute(text("SELECT sql FROM sqlite_master WHERE name = 'meetings'")).scalar_one()
    assert "AUTOINCREMENT" in ddl


def test_deleted_id_is_not_reused():
    with SessionLocal() as db:
        first = Meeting(title="a", met_at=datetime(2026, 1, 1), body="b")
        db.add(first)
        db.commit()
        deleted_id = first.id
        db.delete(first)
        db.commit()

        second = Meeting(title="c", met_at=datetime(2026, 1, 1), body="d")
        db.add(second)
        db.commit()
        assert second.id > deleted_id


def test_meeting_field_order():
    names = [c.name for c in Meeting.__table__.columns]
    assert names == ["id", "title", "met_at", "attendees", "body", "summary", "decisions", "todos"]
