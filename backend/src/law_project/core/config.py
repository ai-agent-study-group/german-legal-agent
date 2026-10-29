
'''
.env 에 적힌 설정을 읽어서 파이썬 객체로 만들어주는 곳.
'''

from functools import lru_cache # 함수결과를 저장해 두고 재사용
from typing import Literal # 이 값들 중 하나만 허용

from pydantic import SecretStr, model_validator # 출력할때 가려지는 문자열
from pydantic_settings import BaseSettings, SettingsConfigDict 
# 환경변수를 자동으로 읽는 클래스, 그 읽는 방법을 정하는 옵션.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") # .env 파일을 읽고, 정의되지 않은 env는 무시
# 설정을 담을 상자를 만드는 것. 괄호안에 BaseSettings를 넣으면 이 상자는 만들어지는 순간 환경변수와 .env파일을 확인해서 자기 칸을 스스로채움
# env_file=".env": 환경 변수뿐 아니라 .env 파일도 읽어
# extra="ignore": .env에 이 상자에 없는 항목이 있어도 그냥 무시

    app_env: Literal["local", "dev", "prod"] = "local" # 앱 환경
    # app_env라는 칸이 있고, 들어갈 수 있는 값은 local, dev, prod 셋뿐이고, 아무것도 없으면 local.
    api_token: SecretStr | None = None # API 키
    # api_token이라는 칸이 있고, 비밀 문자열이거나 비어 있을 수 있고, 아무것도 없으면 비어 있음(None).
    # 비밀 문자열 또는 없음.

    @property
    def docs_enabled(self) -> bool:
        return self.app_env != "prod" # prod 환경에서는 docs를 비활성화

    @model_validator(mode="after")                      
    def _require_token_in_prod(self) -> "Settings":
        if self.app_env == "prod" and self.api_token is None:
            raise ValueError("APP_ENV=prod 에서는 API_TOKEN 을 설정해야 합니다.")
        return self

@lru_cache
def get_settings() -> "Settings":
    return Settings() # Settings 객체를 생성하고 반환   

    