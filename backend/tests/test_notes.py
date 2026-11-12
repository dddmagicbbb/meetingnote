"""2.4 검증 · 2.5 CRUD · 2.6 검색 (05-conventions 테스트 매트릭스 1~6, 8~11)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 20자 미만이라 세 갈래 구분(Gemini)을 부르지 않는 본문
SHORT_BODY = "짧은 메모"


def make_note(**overrides) -> dict:
    payload = {
        "title": "주간 기획 회의",
        "met_at": "2026-11-10T01:00:00Z",
        "attendees": "김대리, 이주임",
        "body": SHORT_BODY,
    }
    payload.update(overrides)
    return payload


def create(**overrides) -> dict:
    res = client.post("/api/notes", json=make_note(**overrides))
    assert res.status_code == 201, res.text
    return res.json()


# --- 매트릭스 1~5 : CRUD ---

def test_create_returns_201():
    res = client.post("/api/notes", json=make_note())
    assert res.status_code == 201
    data = res.json()
    assert data["id"] > 0
    assert data["met_at"] == "2026-11-10T01:00:00Z"
    assert data["summary"] == data["decisions"] == data["todos"] == ""


def test_list_returns_200_without_body():
    create()
    res = client.get("/api/notes")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert "body" not in res.json()[0]


def test_get_one_returns_200_with_body():
    note = create()
    res = client.get(f"/api/notes/{note['id']}")
    assert res.status_code == 200
    assert res.json()["body"] == SHORT_BODY


def test_update_all_fields_returns_200():
    note = create()
    new = make_note(title="바뀐 제목", met_at="2026-11-11T02:30:00Z", attendees="박과장", body="바뀐 메모")
    res = client.put(f"/api/notes/{note['id']}", json=new)
    assert res.status_code == 200
    data = client.get(f"/api/notes/{note['id']}").json()
    assert (data["title"], data["met_at"], data["attendees"], data["body"]) == (
        "바뀐 제목", "2026-11-11T02:30:00Z", "박과장", "바뀐 메모")


def test_delete_returns_204():
    note = create()
    res = client.delete(f"/api/notes/{note['id']}")
    assert res.status_code == 204
    assert client.get(f"/api/notes/{note['id']}").status_code == 404


# --- 매트릭스 8~11 : 검증 ---

def test_missing_title_returns_400():
    payload = make_note()
    del payload["title"]
    assert client.post("/api/notes", json=payload).status_code == 400


@pytest.mark.parametrize("field", ["met_at", "body"])
def test_missing_required_returns_400(field):
    payload = make_note()
    del payload[field]
    assert client.post("/api/notes", json=payload).status_code == 400


def test_bad_met_at_returns_400():
    assert client.post("/api/notes", json=make_note(met_at="어제 오후")).status_code == 400


def test_title_over_200_returns_400():
    assert client.post("/api/notes", json=make_note(title="가" * 201)).status_code == 400


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_unknown_id_returns_404(method):
    kwargs = {"json": make_note()} if method == "put" else {}
    assert getattr(client, method)("/api/notes/99999", **kwargs).status_code == 404


def test_extra_field_returns_422():
    assert client.post("/api/notes", json=make_note(color="red")).status_code == 422


def test_extra_field_on_put_returns_422():
    note = create()
    assert client.put(f"/api/notes/{note['id']}", json=make_note(color="red")).status_code == 422


def test_local_offset_met_at_saved_as_utc():
    note = create(met_at="2026-11-10T10:00:00+09:00")
    assert note["met_at"] == "2026-11-10T01:00:00Z"


# --- 2.6 검색 (매트릭스 6) ---

def _utc_iso_of_local(text: str) -> str:
    """로컬 시각 문자열을 UTC ISO 로 바꾼다. 테스트가 PC 시간대에 매이지 않게 한다."""
    from datetime import datetime, timezone
    local = datetime.fromisoformat(text).astimezone()
    return local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def test_search_q_matches_title_and_attendees_only():
    create(title="신제품 기획 회의", attendees="김대리")
    create(title="주간 회의", attendees="기획팀 박과장")
    create(title="예산 회의", attendees="이주임", body="기획 이야기가 본문에만 나온 회의")
    res = client.get("/api/notes", params={"q": "기획"})
    assert res.status_code == 200
    titles = sorted(n["title"] for n in res.json())
    assert titles == ["신제품 기획 회의", "주간 회의"]


def test_search_date_range_includes_both_ends_in_local_date():
    create(title="시작일 자정", met_at=_utc_iso_of_local("2026-11-10T00:00:00"))
    create(title="끝날 마지막 초", met_at=_utc_iso_of_local("2026-11-12T23:59:59"))
    create(title="하루 전", met_at=_utc_iso_of_local("2026-11-09T23:59:59"))
    create(title="하루 뒤", met_at=_utc_iso_of_local("2026-11-13T00:00:00"))
    res = client.get("/api/notes", params={"from": "2026-11-10", "to": "2026-11-12"})
    assert res.status_code == 200
    assert sorted(n["title"] for n in res.json()) == ["끝날 마지막 초", "시작일 자정"]


def test_search_only_from_or_only_to():
    create(title="이전", met_at=_utc_iso_of_local("2026-11-01T12:00:00"))
    create(title="이후", met_at=_utc_iso_of_local("2026-11-20T12:00:00"))
    assert [n["title"] for n in client.get("/api/notes", params={"from": "2026-11-10"}).json()] == ["이후"]
    assert [n["title"] for n in client.get("/api/notes", params={"to": "2026-11-10"}).json()] == ["이전"]


def test_search_bad_date_returns_400():
    assert client.get("/api/notes", params={"from": "11/10"}).status_code == 400
