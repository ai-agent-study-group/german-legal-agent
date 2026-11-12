"""2단계 연습: 도구(tool) 정의. 모델 호출 없음 -> API 비용 없음.

빈칸(____)을 채우고 실행한다:  .venv/bin/python langgraph_step2_tool.py
"""

from langchain_core.tools import tool

# 설명용 가짜 데이터 (실제 법률 근거 아님). legal_agent_groq_example.py와 같다.
LAWS = {
    "BGB §551": "Die Mietkaution darf höchstens drei Monatsmieten betragen (ohne Betriebskostenvorauszahlung).",
    "BGB §573c": "Die Kündigungsfrist des Mieters beträgt drei Monate.",
}


# 1) 도구 = 평범한 파이썬 함수 + 위에 붙이는 @tool 한 줄.
#    @tool을 붙이면 함수가 "모델에게 설명서를 줄 수 있는 도구 객체"로 바뀐다.
#    Groq 예제에서 손으로 쓴 JSON 스키마(tools = [...])를 이 한 줄이 대신 만든다.
@tool  # 빈칸 1: 위에서 import한 이름
def search_law(keyword: str):  # 빈칸 2: keyword의 타입 (문자열)
    """description"""  # 빈칸 3: 모델이 읽을 설명 한 줄 (Groq 예제의 "description"에 해당)
    hits = [f"{name}: {text}" for name, text in LAWS.items() if keyword in text or keyword in name]
    return "\n".join(hits) if hits else "검색 결과 없음"


# 2) 모델이 보게 될 설명서를 눈으로 확인
print("이름       :", search_law.name)
print("설명       :", search_law.description)
print("입력 스키마:", search_law.args)

# 3) 도구를 직접 실행해 보기 (모델 없이). 인자는 dict로 넘긴다.
print("실행 결과  :", search_law.invoke({"keyword": "BGB §551"}))  # 빈칸 4: 도구를 실행하는 메서드 (invoke)
