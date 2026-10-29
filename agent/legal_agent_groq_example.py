import json

from groq import Groq

client = Groq()  # 환경변수 GROQ_API_KEY 를 자동으로 읽음

MODEL = "openai/gpt-oss-20b"  # Groq 호스팅 모델. 도구 호출 지원. 바꾸려면 이 문자열만 수정
MAX_STEPS = 3  # 루프 상한. 모델이 도구만 계속 부르는 경우에 비용이 무한히 늘지 않게 한다

# 1) "법 데이터베이스" 대신 쓰는 가짜 데이터 (설명용 요약본, 실제 법률 조언용 아님)
#    찾을 대상이 독일어 법문이므로 본문도 독일어로 쓴다.
LAWS = {
    "BGB §551": "Die Mietkaution darf höchstens drei Monatsmieten betragen (ohne Betriebskostenvorauszahlung).",
    "BGB §573c": "Die Kündigungsfrist des Mieters beträgt drei Monate.",
}


# 2) 도구(tool): 키워드로 조문을 찾는 파이썬 함수 (Claude 예제와 동일)
def search_law(keyword):
    hits = [f"{name}: {text}" for name, text in LAWS.items() if keyword in text or keyword in name]
    return "\n".join(hits) if hits else "검색 결과 없음"


# 3) 모델에게 "이런 도구가 있다"고 알려주는 설명서
#    Groq는 OpenAI 호환 형식이라 {"type": "function", "function": {...}}로 감싸고,
#    스키마 키 이름이 input_schema가 아니라 parameters다.
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_law",
            "description": "독일 법 조문 DB에서 키워드로 조문을 검색한다.",
            "parameters": {
                "type": "object",
                "properties": {"keyword": {"type": "string", "description": "검색할 키워드"}},
                "required": ["keyword"],
            },
        },
    }
]

# 4) 에이전트 루프
messages = [
    # Groq(OpenAI 형식)는 system을 messages 안의 첫 항목으로 넣는다. (Claude는 별도 system= 인자)
    {
        "role": "system",
        "content": "너는 독일 법률 정보 도우미다. 반드시 search_law 도구로 찾은 조문만 근거로 답하고, 조문 번호를 인용해라.",
    },
    {"role": "user", "content": "독일에서 월세 보증금은 최대 얼마까지 받을 수 있어?"},
]

for step in range(MAX_STEPS):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # 도구를 쓸지 말지는 모델이 정한다
        max_completion_tokens=2000,
    )
    message = response.choices[0].message
    messages.append(message)  # 모델의 응답(도구 호출 요청 포함)을 대화 기록에 남긴다

    if not message.tool_calls:  # 도구를 더 부르지 않으면 끝
        print(message.content)
        break

    for call in message.tool_calls:
        args = json.loads(call.function.arguments)  # 인자는 dict가 아니라 JSON 문자열로 온다
        result = search_law(**args)
        print(f"[도구 호출] {call.function.name}({args}) -> {result}")
        messages.append(
            {
                "role": "tool",  # Claude는 user 메시지 안의 tool_result 블록, Groq는 role="tool" 메시지
                "tool_call_id": call.id,  # 어떤 요청에 대한 결과인지 연결
                "content": result,
            }
        )
else:
    print(f"[중단] {MAX_STEPS}번 안에 최종 답변이 나오지 않았다.")
