---
제목: "LLM / Agent 작업장"
유형: "위키"
설명: "GitHub Wiki 에서 자동 동기화된 문서입니다."
---

# LLM / Agent 작업장

## 시작하기
현재는 cli, 커맨드 환경에서 작동하는 사용법입니다.

### python 설치하기

mac의 경우 다음 명령어를 콘솔에 입력해 python을 설치합니다.
```bash
brew install python
```

윈도우는 `https://www.python.org/`에서 다운받아 설치합니다.

### 가상환경(venv) 만들기

여기서는 전역 실행환경이 아니라 이 agent폴더안에서 작동하는 환경에 한해서 설명합니다.

1. 가상환경 생성하기

다음 명령어로 .venv 폴더가 생성됩니다.
```bash
cd german-legal-agent/agent
python3 -m venv .venv
```

2. 의존성을 설치합니다
```bash
# german-legal-agent/agent
.venv/bin/pip install -r requirements.txt
```

3. api 키를 설정합니다

.env.example 파일을 .env 파일로 복사하고 안에 groq의 api키를 채워넣습니다.
```bash
cp .env.example .env
```

```bash
# .env
GROQ_API_KEY=please-enter-key
```

groq api키는 이곳에서 생성합니다

`https://console.groq.com`


### 실행

```bash
# german-legal-agent/agent
.venv/bin/python run_cli.py "보증금은 나눠 낼 수 있나요?"
```