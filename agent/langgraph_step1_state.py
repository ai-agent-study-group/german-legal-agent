"""1단계 연습: State(상태)와 노드/간선. 모델 호출 없음 -> API 비용 없음.

빈칸(____)을 채우고 실행한다:  .venv/bin/python langgraph_step1_state.py
"""

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


# 1) State: 그래프의 모든 노드가 공유하는 데이터 모양.
#    Annotated[타입, 규칙]: "messages는 list인데, 노드가 값을 돌려주면 이 규칙으로 합쳐라"는 뜻.
#    힌트: 위에서 import한 add_messages가 "기존 목록 뒤에 추가"하는 규칙이다.
class State(TypedDict):
    messages: Annotated[list, add_messages]  # 빈칸 1


# 2) 노드: state를 받아서, "바꿀 부분만" dict로 돌려주는 함수.
#    모델 대신 가짜 응답을 돌려준다.
def fake_model(state: State):
    last = state["messages"][-1].content  # 마지막 메시지의 내용
    return {"messages": [("ai", f"(가짜 모델) '{last}'라고 하셨네요")]}


# 3) 그래프 조립
builder = StateGraph(State)
builder.add_node("model", fake_model)  # 노드 이름 "model" <-> 함수 fake_model
builder.add_edge(START, "model")  # 빈칸 2: 시작점에서 model로
builder.add_edge("model", END)  # 빈칸 3: model에서 끝으로
graph = builder.compile()  # 빈칸 4: 조립을 마치고 실행 가능한 객체로 만든다

# 4) 실행
result = graph.invoke({"messages": [("user", "보증금은 얼마까지 가능해?")]})
for m in result["messages"]:
    print(type(m).__name__, "|", m.content)
