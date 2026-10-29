from fastapi import APIRouter, Depends

from law_project.core.security import require_token
from law_project.schemas.chat import ChatRequest, ChatResponse
from law_project.schemas.common import SERVICE_UNAVAILABLE, UNAUTHORIZED


# APIRouter는 FastAPI에서 API를 묶어서 관리할 수 있는 도구.
# ChatRequest, ChatResponse는 schemas.chat 모듈에서 정의한 요청과 응답의 모양을 정의.

# API 묶음 (router) 생성.
router = APIRouter(
    prefix="/v1",
    tags=["chat"],
    dependencies=[Depends(require_token)],
    responses=UNAUTHORIZED,
)

# API 하나 등록
@router.post(
    "/chat",
    summary="법률 정보 질문하기",
    response_model=ChatResponse,
    responses=SERVICE_UNAVAILABLE,
)

def chat(request: ChatRequest) -> ChatResponse:
    """분야와 대화 기록을 받아 답변과 출처를 돌려준다. 현재는 stub."""
    question = request.messages[-1].content
    return ChatResponse(
        answer=f"(stub) '{question}'에 대한 답변은 agent 연결 후 제공됩니다.",
        citations=[],
    )

# router.post, app.get 같은역할, 앱 본체대신 router에 붙이고, get대신 post.