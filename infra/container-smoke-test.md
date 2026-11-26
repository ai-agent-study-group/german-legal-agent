# 웹 컨테이너 로컬 테스트 가이드

이 가이드는 이미 빌드된 `german-legal-web:issue-22` 이미지와 실행 중인 Docker 데몬을 사용합니다. 이미지가 없으면 저장소 루트에서 `docker build -t german-legal-web:issue-22 web`으로 먼저 빌드하세요. 이 검사는 웹 데모의 로컬 동작을 확인하며 Railway 배포나 별도 FastAPI 백엔드의 동작을 검증하지 않습니다.

예시는 Bash 또는 호환 셸과 `curl`, `python3`를 사용합니다. 컨테이너 이름과 호스트 포트 3456이 사용 중이면 기존 프로세스를 먼저 확인하고, 필요하면 다른 이름이나 호스트 포트를 사용하세요.

## 1. 컨테이너 실행

```bash
docker run --rm -d \
  --name german-legal-test \
  -e PORT=3456 \
  -p 3456:3456 \
  german-legal-web:issue-22

docker ps --filter name=german-legal-test
docker logs german-legal-test
```

`docker ps`에서 상태가 `Up`인지 확인합니다. `PORT`는 컨테이너 내부 서버 포트, `-p`는 호스트와 컨테이너 포트의 연결입니다.

## 2. 웹 페이지 검사

```bash
for path in / /housing /visa; do
  echo "$path"
  curl -s -o /dev/null -w "HTTP %{http_code}\n" "http://localhost:3456$path"
done
```

각 경로의 응답이 `HTTP 200`인지 확인합니다. 브라우저에서 `http://localhost:3456`을 열어 화면도 확인할 수 있습니다.

## 3. 데모 API와 출처 검사

```bash
curl -sS http://localhost:3456/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"domain":"housing","messages":[{"role":"user","content":"보증금"}]}' \
  | python3 -m json.tool
```

`mode`가 `demo`인지, 보증금 답변과 `citations`의 `housing-deposit` 출처가 있는지 확인합니다. HTTP 상태는 별도로 확인합니다.

```bash
curl -sS -w '\nHTTP %{http_code}\n' \
  http://localhost:3456/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"domain":"housing","messages":[{"role":"user","content":"보증금"}]}'
```

응답 끝에 `HTTP 200`이 표시되어야 합니다. 실제 개인정보 대신 예시 질문을 사용하세요.

## 4. 종료 및 문제 확인

```bash
docker stop german-legal-test
docker ps -a --filter name=german-legal-test
lsof -i :3456
```

`--rm`으로 지정했으므로 컨테이너는 종료 시 자동 삭제되고 이미지는 남습니다. 마지막 두 명령은 컨테이너와 포트 사용 여부 확인용이며, 사용 중인 항목이 없으면 출력이 없을 수 있습니다. macOS에서 `lsof`는 결과가 없으면 종료 코드 1을 반환할 수 있습니다. 시작 실패 시 종료 전에 `docker logs german-legal-test`를 확인하세요. 이미 종료된 `--rm` 컨테이너의 로그는 남지 않습니다.
