import test from "node:test";
import assert from "node:assert/strict";
import { runAgent } from "../lib/agents/run";
import { searchSources, readSource } from "../lib/tools/sources";
import { validSource } from "../lib/sources/repository";
import { POST } from "../app/api/chat/route";
import type { ModelProvider } from "../lib/providers/types";
import type { Source } from "../lib/types";

test("보증금: 실제 검색→읽기→출처", async () => {
  const result = await runAgent("housing", [
    { role: "user", content: "보증금 분할 납부" },
  ]);
  assert.deepEqual(
    result.activities.map((a) => a.type),
    ["search", "read", "answer"],
  );
  assert.equal(result.citations[0].id, "housing-deposit");
  assert.match(result.answer, /나누어/);
});
test("분야별 자료와 읽기 격리", async () => {
  assert.equal((await searchSources("housing", "유학 비자")).length, 0);
  assert.equal(await readSource("housing", "visa-study"), null);
  assert.equal(await readSource("visa", "housing-deposit"), null);
});
test("근거 없음", async () => {
  const result = await runAgent("housing", [
    { role: "user", content: "xyzxyz" },
  ]);
  assert.equal(result.citations.length, 0);
  assert.match(result.answer, /아직 없습니다/);
  assert.deepEqual(
    result.activities.map((a) => a.type),
    ["search", "answer"],
  );
});
test("자료가 있어도 보증금 반환 기한은 보류", async () => {
  const result = await runAgent("housing", [
    { role: "user", content: "보증금 반환은 언제인가요?" },
  ]);
  assert.match(result.answer, /반환 시점이 없습니다/);
  assert.equal(result.citations[0].id, "housing-deposit");
});
test("목적 되묻기 후 사용자 맥락 유지", async () => {
  const first = await runAgent("visa", [
    { role: "user", content: "체류허가를 연장하고 싶어요" },
  ]);
  assert.match(first.answer, /유학과 취업 중/);
  assert.equal(first.citations.length, 0);
  const second = await runAgent("visa", [
    { role: "user", content: "체류허가를 연장하고 싶어요" },
    { role: "assistant", content: first.answer },
    { role: "user", content: "유학이에요" },
  ]);
  assert.equal(second.citations[0].id, "visa-study");
  assert.match(second.answer, /연장 가능 여부/);
});
test("반복 도구 요청의 실행 한도", async () => {
  const provider: ModelProvider = {
    mode: "demo",
    async decide() {
      return {
        type: "tool_call",
        callId: "repeat",
        name: "search_sources",
        arguments: { query: "보증금" },
      };
    },
  };
  const result = await runAgent(
    "housing",
    [{ role: "user", content: "보증금" }],
    { provider },
  );
  assert.equal(result.activities.filter((a) => a.type === "search").length, 3);
  assert.equal(result.activities.at(-1)?.type, "limit");
});
test("미등록 도구와 잘못된 입력은 실행하지 않음", async () => {
  for (const [name, args] of [
    ["delete_file", { path: "x" }],
    ["search_sources", { query: 3 }],
    ["read_source", { id: "visa-study" }],
  ] as const) {
    const provider: ModelProvider = {
      mode: "demo",
      async decide({ toolResults }) {
        return toolResults.length
          ? { type: "answer", text: "error handled", sourceIds: [] }
          : { type: "tool_call", callId: "bad", name, arguments: args };
      },
    };
    const result = await runAgent(
      "housing",
      [{ role: "user", content: "보증금" }],
      { provider },
    );
    assert.equal(result.activities[0].type, "error");
  }
});
test("읽지 않은 자료의 인용과 중복 출처 제거", async () => {
  const provider: ModelProvider = {
    mode: "demo",
    async decide() {
      return {
        type: "answer",
        text: "answer",
        sourceIds: ["housing-deposit", "visa-study"],
      };
    },
  };
  const result = await runAgent("housing", [{ role: "user", content: "hi" }], {
    provider,
  });
  assert.deepEqual(result.citations, []);
});
test("저장소와 제공자 실패가 사용자 답변으로 처리됨", async () => {
  const result = await runAgent(
    "housing",
    [{ role: "user", content: "보증금" }],
    {
      repository: {
        async list() {
          throw new Error("unavailable");
        },
      },
    },
  );
  assert.equal(result.activities[0].type, "error");
  assert.equal(result.citations.length, 0);
  const provider: ModelProvider = {
    mode: "demo",
    async decide() {
      throw new Error("timeout");
    },
  };
  const failure = await runAgent("housing", [{ role: "user", content: "hi" }], {
    provider,
  });
  assert.match(failure.answer, /다시 시도/);
});
test("검토 대기와 잘못된 메타데이터는 제외", async () => {
  const source = await readSource("housing", "housing-deposit");
  assert.ok(source);
  assert.equal(validSource({ ...source, reviewed: false }, "housing"), false);
  assert.equal(
    validSource({ ...source, url: "javascript:bad" }, "housing"),
    false,
  );
  assert.equal(validSource({ ...source, domain: "visa" }, "housing"), false);
  const results = await searchSources("housing", "보증금", {
    async list() {
      return [{ ...source, reviewed: false }] as Source[];
    },
  });
  assert.equal(results.length, 0);
});
test("API 입력 검증과 정상 실행", async () => {
  const call = (body: unknown) =>
    POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    );
  assert.equal((await call({ domain: "other", messages: [] })).status, 400);
  assert.equal(
    (
      await call({
        domain: "housing",
        messages: [{ role: "assistant", content: "x" }],
      })
    ).status,
    400,
  );
  assert.equal(
    (
      await call({
        domain: "housing",
        messages: [{ role: "user", content: "x".repeat(2001) }],
      })
    ).status,
    400,
  );
  assert.equal((await call(null)).status, 400);
  const ok = await call({
    domain: "housing",
    messages: [{ role: "user", content: "보증금" }],
  });
  assert.equal(ok.status, 200);
  assert.equal((await ok.json()).mode, "demo");
});
