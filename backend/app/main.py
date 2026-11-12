"""MeetingNote 백엔드 진입점. 포트 8000 고정 (04-tasks Phase 2)."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_DIR
from app.database import Base, engine
from app.routers import notes, todos, upload

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

Base.metadata.create_all(engine)

app = FastAPI(title="MeetingNote")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """FastAPI 기본 422 를 400 으로 바꾼다. 스펙 외 필드만 422 로 남긴다 (02-specs 5. 검증)."""
    errors = exc.errors()
    has_extra = any(error.get("type") == "extra_forbidden" for error in errors)
    status_code = 422 if has_extra else 400
    return JSONResponse(status_code=status_code, content={"detail": jsonable_errors(errors)})


def jsonable_errors(errors: list[dict]) -> list[dict]:
    # ctx 안의 예외 객체는 JSON 으로 바꿀 수 없어 메시지 위주로 돌려준다
    return [{"loc": list(e.get("loc", ())), "msg": e.get("msg", ""), "type": e.get("type", "")} for e in errors]


app.include_router(notes.router)
app.include_router(todos.router)
app.include_router(upload.router)

# 프론트는 같은 오리진에서 제공한다 (03-design 2). API 경로를 먼저 등록한 뒤 마지막에 붙인다
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
