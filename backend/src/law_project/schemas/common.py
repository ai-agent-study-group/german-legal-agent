from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(description="오류 메시지", examples=["인증 토큰이 없습니다."])


UNAUTHORIZED = {401: {"model": ErrorResponse, "description": "토큰이 없거나 틀림"}}
SERVICE_UNAVAILABLE = {503: {"model": ErrorResponse, "description": "자료 저장소나 LLM에 연결할 수 없음"}}