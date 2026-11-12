"""받아쓴 본문을 요약 / 결정사항 / 할 일 세 갈래로 구분한다 (02-specs 2)."""

import json
import logging
from dataclasses import dataclass

from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import MIN_CLASSIFY_LENGTH
from app.gemini import GeminiError, generate

logger = logging.getLogger(__name__)

# 02-specs 2. 세 갈래를 나누는 기준 - 문장을 그대로 넣는다
CRITERIA = """요약 - 회의 전체를 3~5줄로. 새로운 사실을 지어내지 말 것
결정사항 - 「하기로 했다 / 확정 / 승인」 처럼 합의가 끝난 것만. 논의만 하고 안 정한 것은 넣지 말 것
할 일 - 담당자와 기한이 드러난 것만. 담당자가 없으면 미정으로 적을 것
셋 중 어디에도 안 들어가는 잡담은 버릴 것"""

PROMPT_TEMPLATE = """아래 본문을 회의록으로 정리하라.

[구분 기준]
{criteria}

[출력 규칙]
- is_meeting: 본문이 회의 내용이 아니면 false, 회의 내용이면 true
- summary: 요약 문장 목록
- decisions: 결정사항 목록
- todos: 할 일 목록. what 은 내용, who 는 담당자, when 은 회의에서 말한 기한 문구 그대로
- 본문에 없는 내용은 쓰지 말 것. 한국어로 쓸 것

[본문]
{body}"""

UNASSIGNED = "미정"


class _Todo(BaseModel):
    what: str
    who: str
    when: str


class _Result(BaseModel):
    is_meeting: bool
    summary: list[str]
    decisions: list[str]
    todos: list[_Todo]


@dataclass(frozen=True)
class Classification:
    summary: str = ""
    decisions: str = ""
    todos: str = ""


EMPTY = Classification()


def _clean(text: str) -> str:
    # 한 항목이 한 줄 · 세로줄 구분을 깨지 않게 한다
    return " ".join(text.replace("|", "/").split())


def _join(lines: list[str]) -> str:
    return "\n".join(c for c in (_clean(line) for line in lines) if c)


def _format_todos(todos: list[_Todo]) -> str:
    # 한 줄에 하나씩 "내용 | 담당자 | 기한" (02-specs 1)
    rows = []
    for todo in todos:
        what = _clean(todo.what)
        if not what:
            continue
        who = _clean(todo.who) or UNASSIGNED
        rows.append(f"{what} | {who} | {_clean(todo.when)}")
    return "\n".join(rows)


def classify(body: str) -> Classification:
    """세 갈래 결과를 돌려준다. 짧거나 회의가 아니거나 실패하면 세 칸을 빈 값으로 둔다."""
    if len(body.strip()) < MIN_CLASSIFY_LENGTH:
        return EMPTY

    config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=_Result)
    prompt = PROMPT_TEMPLATE.format(criteria=CRITERIA, body=body)
    try:
        raw = generate(prompt, config)
        result = _Result.model_validate(json.loads(raw))
    except (GeminiError, json.JSONDecodeError, ValidationError):
        # 저장은 그대로 하고, 서버는 logging 으로만 남긴다 (02-specs 7)
        logger.exception("세 갈래 구분 실패")
        return EMPTY

    if not result.is_meeting:
        return EMPTY
    return Classification(
        summary=_join(result.summary),
        decisions=_join(result.decisions),
        todos=_format_todos(result.todos),
    )
