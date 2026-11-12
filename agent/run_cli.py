"""⑥ 실행: 터미널에서 agent에게 질문한다. (Groq API를 실제로 호출한다)

    cd german-legal-agent/agent
    .venv/bin/python run_cli.py "보증금은 나눠 낼 수 있나요?"   # 질문 한 개
    .venv/bin/python run_cli.py                                  # 대화 모드 (빈 줄 입력하면 종료)

GROQ_API_KEY는 agent/.env에서 읽는다.
"""

import sys

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from legal_agent.graph import ask, build_graph

load_dotenv()  # .env 파일의 값을 환경변수로 올린다 (PHP의 vlucas/phpdotenv와 같다)


def main():
    # MemorySaver: 대화 기록을 이 프로그램의 메모리에 저장한다. 프로그램을 끄면 사라진다.
    graph = build_graph("housing", checkpointer=MemorySaver())

    if len(sys.argv) > 1:  # 질문을 인자로 받은 경우: 한 번 묻고 끝
        answer, _ = ask(graph, " ".join(sys.argv[1:]), thread_id="cli")
        print("\n" + answer)
        return

    print("질문을 입력하세요 (종료: 빈 줄)")
    while True:
        question = input("> ").strip()
        if not question:
            break
        answer, _ = ask(graph, question, thread_id="cli")  # 같은 thread_id라서 앞 대화를 기억한다
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
