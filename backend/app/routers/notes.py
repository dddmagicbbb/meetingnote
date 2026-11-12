"""회의록 CRUD 와 검색 - /api/notes (02-specs 3. REST API)."""

from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.classifier import classify
from app.database import get_db
from app.models import Meeting
from app.schemas import NoteDetail, NoteIn, NoteSummary

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _get_or_404(db: Session, note_id: int) -> Meeting:
    meeting = db.get(Meeting, note_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="회의록이 없습니다")
    return meeting


def _apply_classification(meeting: Meeting) -> None:
    result = classify(meeting.body)
    meeting.summary = result.summary
    meeting.decisions = result.decisions
    meeting.todos = result.todos


def _local_date_to_utc(day: date, end_of_day: bool) -> datetime:
    """화면의 로컬 날짜를 UTC 경계 시각으로 바꾼다.

    앱은 사용자 PC 에서 localhost:8000 으로 돌므로 서버의 로컬 시간대를 화면의 로컬 시간대로 본다.
    """
    local_time = time(23, 59, 59) if end_of_day else time(0, 0, 0)
    local = datetime.combine(day, local_time).astimezone()  # 시간대 없는 값을 로컬로 해석
    return local.astimezone(timezone.utc).replace(tzinfo=None)


@router.post("", status_code=201, response_model=NoteDetail)
def create_note(payload: NoteIn, db: Session = Depends(get_db)) -> Meeting:
    meeting = Meeting(**payload.model_dump())
    _apply_classification(meeting)
    db.add(meeting)
    db.commit()
    return meeting


@router.get("", response_model=list[NoteSummary])
def list_notes(
    q: str | None = None,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
) -> list[Meeting]:
    stmt = select(Meeting)
    if q:
        pattern = f"%{q}%"
        # 제목과 참석자만 찾는다. 본문은 검색하지 않는다 (02-specs 4. 검색 규칙)
        stmt = stmt.where(or_(Meeting.title.like(pattern), Meeting.attendees.like(pattern)))
    if from_date:
        stmt = stmt.where(Meeting.met_at >= _local_date_to_utc(from_date, end_of_day=False))
    if to_date:
        stmt = stmt.where(Meeting.met_at <= _local_date_to_utc(to_date, end_of_day=True))
    stmt = stmt.order_by(Meeting.met_at.desc(), Meeting.id.desc())
    return list(db.scalars(stmt))


@router.get("/{note_id}", response_model=NoteDetail)
def get_note(note_id: int, db: Session = Depends(get_db)) -> Meeting:
    return _get_or_404(db, note_id)


@router.put("/{note_id}", response_model=NoteDetail)
def update_note(note_id: int, payload: NoteIn, db: Session = Depends(get_db)) -> Meeting:
    meeting = _get_or_404(db, note_id)
    body_changed = meeting.body != payload.body
    for field, value in payload.model_dump().items():
        setattr(meeting, field, value)
    # 본문이 바뀌면 세 갈래 결과가 본문과 어긋나므로 다시 구분한다
    if body_changed:
        _apply_classification(meeting)
    db.commit()
    return meeting


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    meeting = _get_or_404(db, note_id)
    db.delete(meeting)
    db.commit()
    return Response(status_code=204)
