"""
요청에 올바른 토큰이 있는지 검사함. 
핵심 개념 : Depends
    FastAPI에서 depends(함수)는 이 API를 실행하기전에 이 함수를 먼저 실행해줘라는 의미.

    요청 도착
        Depends로 걸린 함수들 먼저 실행 (문지기)
            통과하면 → 진짜 API 함수 실행 (chat)
            에러 내면 → 거기서 끝, 바로 에러 응답
routers/chat.py에서 dependencies=[Depends(require_token)]  라고 쓴게 chat 라우터의 모든 API앞에 require_token 문지기를 세워라.라는의미.       

"""
import secrets
from typing import Annotated # 타입에 추가정보 (여기선 depends) 를 붙이는 문법

from fastapi import Depends, HTTPException, status # 위에서 설명한 "먼저실행해줘", 에러응답을 만드는 도구 (raise하면 그자리에서 멈추고 에러로 응답), 401같은 숫자를 이름으로 쓰게해주는 모음
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer # 헤더에서 Bearer토큰을 꺼내주는 도구, 꺼낸 토큰이 담기는 상자

from law_project.core.config import Settings, get_settings # .env 설정 클래스, 설정을 꺼내는 함수

bearer_scheme = HTTPBearer(auto_error=False)
# HTTPBearer는 요청 헤더에서 Authorization: Bearer xxx를 찾아서 xxx를 꺼냄.
# 그리고 이게 Authorize 버튼을 만드는 장본인이에요. 
# FastAPI가 "어? 이 API는 HTTPBearer를 쓰네" 하고 Swagger에 자물쇠와 Authorize 버튼을 자동으로 그려 줘요.
# auto_error=False가 중요해요.
    # True(기본값)면 토큰이 없을 때 HTTPBearer가 알아서 403 에러를 내요
    # False로 두면 토큰이 없을 때 에러 대신 None을 돌려줘요. 그럼 우리가 직접 처리할 수 있어요
        # 401 Unauthorized: "너 누군지 모르겠어" (인증 안 됨)
        # 403 Forbidden: "너 누군지 알지만 권한 없어"


def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if credentials is None: # 토큰이있나?
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "인증 토큰이 없습니다.")

    expected = settings.api_token #토큰이 맞나?
    if expected is not None and not secrets.compare_digest(
        credentials.credentials, expected.get_secret_value()
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "인증 토큰이 올바르지 않습니다.")