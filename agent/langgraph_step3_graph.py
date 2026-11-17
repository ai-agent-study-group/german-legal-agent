"""3단계 연습: 모델 노드 + 도구 노드 + 조건부 간선 = agent 루프.

!! 이 파일은 Groq API를 실제로 호출한다 (모델 openai/gpt-oss-120b, 질문 1개).
   질문 1개에 모델 호출은 보통 2번(도구 요청 -> 최종 답변), 상한은 아래 recursion_limit.

빈칸(____)을 채우고 실행한다 (.env의 키를 환경변수로 읽어서 실행):
  cd german-legal-agent/agent
  set -a; . ./.env; set +a
  .venv/bin/python langgraph_step3_graph.py
"""

from typing import Annotated

import httpx
from typing_extensions import TypedDict

from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

MODEL = "openai/gpt-oss-120b"

SYSTEM = (
    "너는 독일 법률 정보 도우미다. 반드시 search_law 도구로 찾은 조문만 근거로 답하고, "
    "조문 번호를 인용해라."
)

LAWS = {
    "BGB §551": "Die Mietkaution darf höchstens drei Monatsmieten betragen (ohne Betriebskostenvorauszahlung).",
    "BGB §573c": "Die Kündigungsfrist des Mieters beträgt drei Monate.",
}


# --- 1~2단계에서 만든 것 (그대로) ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def search_law(keyword: str):
    """독일 법 조문 DB에서 키워드로 조문을 검색한다. 키워드는 조문 번호(예: BGB §551)나 독일어 단어."""
    hits = [f"{name}: {text}" for name, text in LAWS.items() if keyword in text or keyword in name]
    return "\n".join(hits) if hits else "검색 결과 없음"


# --- 3단계: 새로 하는 것 ---

# (a) 모델 준비. temperature=0: 매번 가장 가능성 높은 답을 고르게 해서 흔들림을 줄인다(완전히 없애진 못함).
#     max_retries=1, timeout=30: 실패했을 때 몰래 여러 번 재호출하지 않게, 오래 기다리지 않게.
#     http_client: 이 PC는 IPv6 연결이 막혀 있어(기본 연결이 40~120초 멈춤) IPv4로만 접속하게 강제한다.
#     네트워크 환경 문제용 임시 처방이다. 팀에 올리기 전에 빼거나 이유를 문서에 적을 것.
llm = ChatGroq(
    model=MODEL,
    temperature=0,
    max_retries=1,
    timeout=30,
    http_client=httpx.Client(transport=httpx.HTTPTransport(local_address="0.0.0.0"), timeout=30),
)

# 빈칸 1: 모델에게 "이런 도구가 있다"고 알려 주는 메서드. 인자는 도구 객체 목록.
#         (Groq 예제에서 create(..., tools=tools)로 넘기던 것에 해당)
llm_with_tools = llm.bind_tools([search_law])


# (b) 모델 노드: 대화 기록 앞에 system 지시를 붙여 모델을 부르고, 응답을 State에 추가한다.
def call_model(state: State):
    response = llm_with_tools.invoke([("system", SYSTEM)] + state["messages"])
    return {"messages": [response]}  # 빈칸 2: 모델 응답을 돌려준다 (변수 이름은 바로 위 줄에 있다)


# (c) 그래프 조립
builder = StateGraph(State)
builder.add_node("model", call_model)
# 빈칸 3: 도구 노드. 모델이 요청한 도구를 대신 실행해 주는 기성품. 인자는 도구 객체 목록.
builder.add_node("tools", ToolNode([search_law]))

builder.add_edge(START, "model")
# 빈칸 4: model 다음에 어디로 갈지 "조건"으로 정한다.
#         기성품 판단 함수 tools_condition: 도구 요청이 있으면 "tools" 노드로, 없으면 END로 보낸다.
builder.add_conditional_edges("model", tools_condition)
# 빈칸 5: tools 실행이 끝나면 다시 어느 노드로? (결과를 모델이 읽어야 한다)
builder.add_edge("tools", "model")
graph = builder.compile()

# (d) 실행. recursion_limit: 노드 실행 횟수 상한 (model 1회 + tools 1회 = 2로 센다).
#     빈칸 6: 상한 숫자. 정상이면 model -> tools -> model = 3번 실행이지만 3은 부족하다(가짜 모델로 확인).
#     여유를 두되 작게(6~8). 6이면 모델 호출은 최대 3번, 8이면 최대 4번이다.
result = graph.invoke(
    {"messages": [("user", "독일에서 월세 보증금은 최대 얼마까지 받을 수 있어?")]},
    config={"recursion_limit": 8},
)

for m in result["messages"]:
    print(type(m).__name__, "|", m.content, getattr(m, "tool_calls", None) or "")
