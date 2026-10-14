import "server-only";
import type { Source, SourceHit } from "@/lib/types";
import type { ModelProvider } from "./types";
// 모델 호출이 없습니다. 정해진 규칙으로 같은 도구 흐름을 재현합니다.
export const demoProvider: ModelProvider = {
  mode: "demo",
  async decide({ domain, messages, toolResults }) {
    const latest = messages.at(-1)?.content ?? "";
    const priorQuestion =
      messages.filter((t) => t.role === "user").at(-2)?.content ?? "";
    const waiting =
      messages.at(-2)?.role === "assistant" &&
      messages.at(-2)?.content.includes("유학과 취업 중");
    const query = waiting ? `${priorQuestion} ${latest}` : latest;
    if (!toolResults.length) {
      if (
        domain === "visa" &&
        /연장|체류허가/.test(latest) &&
        !/유학|학생|취업|근로/.test(query)
      )
        return {
          type: "answer",
          text: "현재 어떤 목적으로 체류하고 계신가요? 유학과 취업 중 해당하는 목적을 알려주세요. 그 외 목적은 준비된 자료에 없습니다.",
          sourceIds: [],
        };
      return {
        type: "tool_call",
        callId: "demo-search",
        name: "search_sources",
        arguments: { query },
      };
    }
    const last = toolResults.at(-1)!;
    if (!last.ok)
      return {
        type: "answer",
        text: "자료를 확인하는 중 문제가 발생했습니다. 확인하지 못한 내용을 답하지 않겠습니다. 잠시 후 다시 시도해주세요.",
        sourceIds: [],
      };
    const search = toolResults.find((t) => t.request.name === "search_sources");
    const hits = (search?.value ?? []) as SourceHit[];
    if (!hits.length)
      return {
        type: "answer",
        text: "이 질문에 답할 검토된 자료가 아직 없습니다. 현재 자료로는 답변을 제공하기 어렵습니다. 공식 원문이나 해당 기관의 안내를 추가로 확인해주세요.",
        sourceIds: [],
      };
    const read = toolResults.find((t) => t.request.name === "read_source");
    if (!read)
      return {
        type: "tool_call",
        callId: "demo-read",
        name: "read_source",
        arguments: { id: hits[0].id },
      };
    const source = read.value as Source;
    if (
      domain === "housing" &&
      /반환|돌려|언제/.test(latest) &&
      /보증금/.test(latest)
    )
      return {
        type: "answer",
        text: "보증금 관련 자료는 찾았지만, 준비된 요약에는 반환 시점이 없습니다. 이 자료만으로 반환 기한을 단정할 수 없습니다. 원문과 추가 자료를 확인해야 합니다.",
        sourceIds: [source.id],
      };
    if (domain === "visa" && /연장/.test(query))
      return {
        type: "answer",
        text: `${source.body}\n\n이 자료만으로 개인의 연장 가능 여부나 관할 기관의 제출 서류를 확정할 수 없습니다. 거주 지역 담당 기관의 안내를 추가로 확인해주세요.`,
        sourceIds: [source.id],
      };
    return {
      type: "answer",
      text: `${source.body}\n\n준비된 자료를 읽어 보여주는 데모입니다. 구체적인 상황에 적용하기 전 원문과 담당 기관의 안내를 확인해주세요.`,
      sourceIds: [source.id],
    };
  },
};
