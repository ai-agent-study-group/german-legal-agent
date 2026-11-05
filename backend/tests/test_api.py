import pytest
from fastapi.testclient import TestClient #서버를 안켜고도 앱에 요청을 보내는 도구. (swagger Execute임.)
from pydantic import SecretStr, ValidationError # 토큰담는 비밀문자열, pydantic 검사 실패에러. prod토큰테스트에서 씀.

from law_project.core.config import Settings, get_settings
from law_project.main import create_app # from main.py

TOKEN = "test-token" # 테스트용 토큰. 
VALID_BODY = {"domain": "housing", "messages": [{"role": "user", "content": "보증금 질문"}]}
# 올바른 요청 body. swagger입력칸에 있던 jason이랑 같은모양.

"""
테스트 하나하나 다 이런 모양일것임.
def test_name():
    res = 요청보내기
    assert 결과가 이래야함.

def test_name test_로 시작하면 pytest가 알아서 테스트로 인식.
"""

#원하는 환경, 원하는 토큰으로 앱만들어서 요청을 보낼 준비해줘 하는 함수. 
def make_client(app_env: str = "local", token: str | None = TOKEN) -> TestClient:
    settings = Settings(app_env=app_env, api_token=SecretStr(token) if token else None)
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)

"""
make_client() - local 환경에서, test-token 토큰으로.
make_client("prod") - prod 환경에서, test-token 토큰으로.

.env 를 읽는대신 값을 직접 넣어서  설정을 만듬. 
SecretStr(token) if token else None은 "토큰이 있으면 SecretStr로 감싸고, 없으면 None"

app=create_app(settings) - FastAPI 앱을 만듬.

app.dependency_overrides[get_settings] = lambda: settings
    security.py의 require_token은 설정을 스스로가져옴.
    근데 get_settings은 .env를 읽음. 그대로두면  mytoken으로 알고있게됨.
    test에서는 test-token으로 보내니 계속 401 나옴.
    dependency_overrides는 FastAPI 기능으로, **”이 앱에서는 get_settings 대신 이걸 써"
    lambda: settings는 "부르면 위에서 만든 settings를 돌려주는 작은 함수

create_app(settings)은 문서 켜고 끄기.
dependency_overrides는 토큰 검사에 같은 설정을 쓰게 맞춰 주는 것.
"""


def auth(token: str = TOKEN) -> dict:
    return {"Authorization": f"Bearer {token}"}

# ----

def test_health_needs_no_token():
    res = make_client().get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ----

def test_chat_without_token_is_401():
    res = make_client().post("/v1/chat", json=VALID_BODY)
    assert res.status_code == 401
    assert res.json()["detail"] == "인증 토큰이 없습니다."

def test_chat_with_wrong_token_is_401():
    res = make_client().post("/v1/chat", json=VALID_BODY, headers=auth("wrong"))
# 틀린 토큰 → 401, "올바르지 않습니다"

def test_chat_with_correct_token_is_200():
    res = make_client().post("/v1/chat", json=VALID_BODY, headers=auth())
    assert res.status_code == 200
    body = res.json()
    assert "보증금 질문" in body["answer"] # 보낸 질문이 stub답변안에 들어있는지 
    assert body["citations"] == [] # 빈리스트

# ----

def test_wrong_domain_is_422():
    body = {**VALID_BODY, "domain": "house"}
    res = make_client().post("/v1/chat", json=body, headers=auth())
    assert res.status_code == 422


def test_empty_content_is_422():
    body = {"domain": "visa", "messages": [{"role": "user", "content": ""}]}
    res = make_client().post("/v1/chat", json=body, headers=auth())
    assert res.status_code == 422

# ----

def test_docs_visible_in_local():
    client = make_client("local")
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_docs_hidden_in_prod():
    client = make_client("prod")
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404


def test_prod_without_token_fails_to_start():
    with pytest.raises(ValidationError):
        Settings(app_env="prod", api_token=None)


# ---- 
def test_openapi_documents_errors_and_tags():
    spec = make_client().get("/openapi.json").json()
    chat_op = spec["paths"]["/v1/chat"]["post"]
    assert {"200", "401", "422", "503"} <= set(chat_op["responses"])
    assert chat_op["tags"] == ["chat"]
    assert chat_op["summary"] == "법률 정보 질문하기"
    assert "HTTPBearer" in spec["components"]["securitySchemes"]