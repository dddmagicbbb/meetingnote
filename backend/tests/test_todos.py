"""2.8 GET /api/todos (05-conventions 테스트 매트릭스 7)."""

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Meeting
from datetime import datetime

client = TestClient(app)


def add_meeting(title: str, met_at: datetime, todos: str) -> int:
    # 세 갈래 결과를 직접 넣어 Gemini 없이 todos 파싱 · 정렬만 본다
    with SessionLocal() as db:
        meeting = Meeting(title=title, met_at=met_at, body="본문", todos=todos)
        db.add(meeting)
        db.commit()
        return meeting.id


def test_todos_returns_200_with_fields():
    note_id = add_meeting("2차 스프린트", datetime(2026, 11, 10), "목록 화면과 검색 기능 구현 | 김대리 | 다음 주 금요일")
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.json() == [{
        "what": "목록 화면과 검색 기능 구현",
        "who": "김대리",
        "when": "다음 주 금요일",
        "note_id": note_id,
        "note_title": "2차 스프린트",
    }]


def test_todos_sorted_by_meeting_date_oldest_first():
    add_meeting("나중 회의", datetime(2026, 11, 20), "나중 일 | 박과장 | 다음 달 10일")
    add_meeting("먼저 회의", datetime(2026, 11, 1), "먼저 일 1 | 이주임 | 이번 주 안\n먼저 일 2 | 미정 | ")
    whats = [t["what"] for t in client.get("/api/todos").json()]
    assert whats == ["먼저 일 1", "먼저 일 2", "나중 일"]


def test_todos_skips_empty_and_fills_missing_fields():
    add_meeting("회의", datetime(2026, 11, 1), "\n담당자 없는 일\n")
    assert client.get("/api/todos").json() == [{
        "what": "담당자 없는 일", "who": "", "when": "", "note_id": 1, "note_title": "회의",
    }]


def test_todos_empty_when_no_meetings():
    assert client.get("/api/todos").json() == []
