"""2.7 세 갈래 구분 - 실제 Gemini 를 부른다 (05-conventions 4. 테스트)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MEETING_BODY = """김대리: 다음 분기 신제품 출시 일정을 정해야 합니다.
박과장: 출시는 3월 2일로 확정하겠습니다. 다들 동의하시죠?
이주임: 네, 동의합니다.
박과장: 그럼 출시일은 3월 2일로 하기로 했습니다. 광고 예산은 다음 회의에서 다시 논의하죠.
김대리: 보도자료 초안은 제가 다음 주 금요일까지 쓰겠습니다.
이주임: 저는 이번 주 안에 랜딩 페이지 시안을 올리겠습니다.
박과장: 아, 점심은 다들 뭐 드셨어요?"""

NOT_MEETING_BODY = """오늘 저녁 장보기 목록: 우유 2팩, 계란 한 판, 양파 3개, 두부, 대파 한 단, 그리고 세탁 세제."""


def post(body: str) -> dict:
    res = client.post("/api/notes", json={"title": "테스트", "met_at": "2026-11-10T01:00:00Z", "body": body})
    assert res.status_code == 201, res.text
    return res.json()


@pytest.mark.usefixtures("gemini_pause")
def test_meeting_body_is_split_into_three():
    note = post(MEETING_BODY)

    summary_lines = note["summary"].splitlines()
    assert 1 <= len(summary_lines) <= 5

    assert "3월 2일" in note["decisions"]
    assert "광고 예산" not in note["decisions"], "논의만 한 것이 결정사항에 들어감"

    todo_lines = note["todos"].splitlines()
    assert len(todo_lines) >= 2
    for line in todo_lines:
        assert len(line.split(" | ")) == 3, f"내용 | 담당자 | 기한 형식이 아님: {line}"
    assert any("김대리" in line and "다음 주 금요일" in line for line in todo_lines)

    assert "점심" not in note["summary"] + note["decisions"] + note["todos"], "잡담이 남음"


@pytest.mark.usefixtures("gemini_pause")
def test_not_meeting_body_leaves_three_empty():
    note = post(NOT_MEETING_BODY)
    assert note["summary"] == note["decisions"] == note["todos"] == ""


def test_short_body_skips_classification():
    note = post("19자짜리 아주 짧은 메모입니다")
    assert note["summary"] == note["decisions"] == note["todos"] == ""
