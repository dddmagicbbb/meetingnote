"""요청 · 응답 스키마. 스펙 외 필드는 extra=forbid 로 막는다 (02-specs 5. 검증)."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class NoteIn(BaseModel):
    """POST · PUT /api/notes 요청 본문."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    met_at: datetime
    attendees: str = ""
    body: str = Field(min_length=1)

    @field_validator("title", "body")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("빈 값은 허용하지 않음")
        return value

    @field_validator("met_at")
    @classmethod
    def to_utc(cls, value: datetime) -> datetime:
        # 시간대가 없으면 UTC 로 본다. 저장은 tzinfo 없는 UTC 값으로 한다
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc)
        return value.replace(tzinfo=None)


class _NoteOutBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    met_at: datetime
    attendees: str
    summary: str
    decisions: str
    todos: str

    @field_serializer("met_at")
    def serialize_met_at(self, value: datetime) -> str:
        # 화면이 로컬 시각으로 되돌릴 수 있게 UTC 임을 Z 로 밝힌다
        return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class NoteSummary(_NoteOutBase):
    """목록 응답. body 를 넣지 않는다."""


class NoteDetail(_NoteOutBase):
    """단건 응답. body 를 넣는다."""

    body: str


class TodoOut(BaseModel):
    what: str
    who: str
    when: str
    note_id: int
    note_title: str


class UploadOut(BaseModel):
    body: str
