"""할 일 모아 보기 - GET /api/todos (02-specs 3)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting
from app.schemas import TodoOut

router = APIRouter(prefix="/api", tags=["todos"])

TODO_SEPARATOR = "|"
TODO_FIELD_COUNT = 3


def parse_todo_line(line: str) -> tuple[str, str, str] | None:
    """`내용 | 담당자 | 기한` 한 줄을 나눈다. 칸이 모자라면 빈 값으로 채운다."""
    parts = [part.strip() for part in line.split(TODO_SEPARATOR, TODO_FIELD_COUNT - 1)]
    if not parts or not parts[0]:
        return None
    parts += [""] * (TODO_FIELD_COUNT - len(parts))
    return parts[0], parts[1], parts[2]


@router.get("/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)) -> list[TodoOut]:
    # 회의 날짜 오래된 순. 기한으로는 정렬하지 않는다 (02-specs 2)
    meetings = db.scalars(select(Meeting).order_by(Meeting.met_at.asc(), Meeting.id.asc()))
    result: list[TodoOut] = []
    for meeting in meetings:
        for line in meeting.todos.splitlines():
            parsed = parse_todo_line(line)
            if parsed is None:
                continue
            what, who, when = parsed
            result.append(TodoOut(what=what, who=who, when=when, note_id=meeting.id, note_title=meeting.title))
    return result
