from fastapi import FastAPI
from law_project.core.config import get_settings
from law_project.routers import chat

settings = get_settings() # 설정을 가져옴

app = FastAPI(
    title= "German Legal agent API",
    version= "0.1.0",
    description= "An API for a German legal agent that provides legal information and assistance.",
    docs_url= "/docs" if settings.docs_enabled else None, # docs_enabled가 True
    redoc_url= "/redoc" if settings.docs_enabled else None, # docs_enabled가 True
    openapi_url= "/openapi.json" if settings.docs_enabled else None, # docs_enabled가 True
)
@app.get("/health", tags=["system"], summary="서버 상태 확인")
def health():
    return {"status": "ok"}

app.include_router(chat.router) # chat.py에 있는 router를 FastAPI 앱에 등록
