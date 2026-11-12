# 질문 API가 주고받는 JSON이 어떻게 생겨야하는지 정의하는 곳.
from typing import Literal
from pydantic import BaseModel, Field

# Literal is used to specify that a  value must be one of a specific set of string literals.
# BaseModel is a class from the pydantic library that allows you to define data models with type validation and serialization.
# Field is a function from the pydantic library that allows you to specify additional metadata for model fields, such as descriptions, examples, and validation constraints.


# Turn : 메시지 한개 / Basemodel를 상속해서 메시지 하나 의 모양을 정의. Turn은 대화의 한 차례라는 의미.
class Turn(BaseModel):
    role: Literal["user", "assistant"] = Field(description="발화자")
    # role은 칸 이름. json에서도 role이라는 이름으로 들어가야함.
    # : Literal["user", "assistant"] : 타입. user 아니면 assistant만 들어올 수 있음. 다른 값이 들어오면 에러.
    # = Field(description="발화자") : Swagger에 발화자라고 설명표시.

    content: str = Field(
        min_length=1,
        max_length=2000,
        description="메시지 본문 (2,000자 이내)", # Swagger에 메시지 본문이라고 설명표시.
        examples=["집주인이 보증금을 3개월 넘게 돌려주지 않아요."], # Swagger에 예시값. 리스트로 줘야함.
    )

# front > server
class ChatRequest(BaseModel):
    domain: Literal["housing", "visa"] = Field(description="질문 분야", examples=["housing"])
    # 질문 분야. 주거(housing)인지 비자(visa)인지. 지금 프론트 데모에 있는 페이지 두 개랑 같아요.

    messages: list[Turn] = Field(
        min_length=1,
        max_length=12,
        description="지금까지의 대화. 마지막은 user 메시지", # 지금 이코드에서는 검사하지않음 추후에 추가.

        # list[Turn]: Turn 여러 개가 담긴 리스트. 위에서 만든 Turn을 부품으로 쓰는 거예요. 리스트 안의 각 항목도 Turn 규칙(role, content 검사)을 다 거쳐요
        # min_length=1, max_length=12: 여기선 글자 수가 아니라 리스트 길이예요. 최소 1개, 최대 12개 메시지

    )

# server > front
class ChatResponse(BaseModel):
    answer: str = Field(description="최종 답변 (Markdown)")
    citations: list[str] = Field(description="답변에 사용한 출처 ID 목록", examples=[["housing-deposit"]])

    # list[str]: 문자열 리스트. 예: ["housing-deposit", "bgb-551"]
    # 법률 정보라서 "어디서 나온 말인지" 출처가 중요. 그 출처 ID를 담는 칸
    #


"""
BaseModel과 Field
BaseModel: Pydantic의 기본 클래스. 이걸 상속하면 들어온 데이터가 이 모양에 맞는지 자동으로 검사. 
            config.py의 BaseSettings랑 친척.
Field(...): 칸 하나에 규칙과 설명을 다는 도구. 이슈에서 말한 Field(description, examples)가 이거.

"""