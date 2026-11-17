"""⑤ 그래프: 모델 노드 + 도구 노드 + 조건부 간선. 1~3단계에서 배운 구조를 한 파일에 모은 것.

    START -> model --(도구 요청 있음)--> tools -> model ...
                  \\--(도구 요청 없음)--> END
"""

import groq
import httpx
from typing import Annotated

from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from legal_agent.prompts import SYSTEM_PROMPT
from legal_agent.tools import make_tools

MODEL = "openai/gpt-oss-120b"
RECURSION_LIMIT = 10  # 노드 실행 횟수 상한. 질문 1개당 모델 호출은 최대 5번이다 (비용 상한)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def _make_llm() -> ChatGroq:
    # temperature=0: 흔들림을 줄인다 (완전히 없애진 못한다). max_retries=1, timeout=30: 몰래 재호출하거나 오래 기다리지 않게.
    # http_client: 이 PC는 IPv6가 막혀 있어 기본 연결이 40~120초 멈춘다. IPv4로만 접속하게 강제한다.
    #              환경 문제용 임시 처방이다. 다른 환경에서는 이 줄을 지워도 된다.
    return ChatGroq(
        model=MODEL,
        temperature=0,
        max_retries=1,
        timeout=30,
        http_client=httpx.Client(transport=httpx.HTTPTransport(local_address="0.0.0.0"), timeout=30),
    )


def build_graph(domain: str = "housing", checkpointer=None):
    """분야(domain)를 정해서 agent 그래프를 만든다.

    checkpointer를 넘기면 대화 기록이 thread_id별로 저장되어 연속 대화가 된다 (6단계).
    """
    tools = make_tools(domain)
    llm_with_tools = _make_llm().bind_tools(tools)

    def call_model(state: State):
        response = llm_with_tools.invoke([("system", SYSTEM_PROMPT)] + state["messages"])
        return {"messages": [response]}

    builder = StateGraph(State)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile(checkpointer=checkpointer)


def ask(graph, question: str, thread_id: str = "default", verbose: bool = True):
    """질문 하나를 실행해서 (답변, 도구 요청 목록)을 돌려준다.

    같은 thread_id로 부르면 앞선 대화를 이어서 본다 (graph를 checkpointer와 함께 만들었을 때).
    """
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}
    answer = ""
    tool_requests = []
    try:
        # stream_mode="updates": 노드가 하나 끝날 때마다 그 노드가 돌려준 값을 받는다.
        for update in graph.stream({"messages": [("user", question)]}, config, stream_mode="updates"):
            for node, data in update.items():
                for m in data["messages"]:
                    if node == "model" and m.tool_calls:
                        for call in m.tool_calls:
                            tool_requests.append((call["name"], call["args"]))
                            if verbose:
                                print(f"[도구 요청] {call['name']} {call['args']}")
                    elif node == "model":
                        answer = m.content
                    elif verbose:  # node == "tools"
                        print(f"[도구 결과] {m.content[:70]!r}")
    except GraphRecursionError:
        answer = "(검색을 여러 번 했지만 답을 만들지 못했습니다. 질문을 바꿔 보세요.)"
    except groq.RateLimitError:  # Groq의 분당 토큰 한도(TPM)를 넘은 경우
        answer = "(요청 한도를 넘었습니다. 잠시 뒤에 다시 시도해 주세요.)"
    return answer, tool_requests
