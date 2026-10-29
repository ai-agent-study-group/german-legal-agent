import type { Domain } from "@/lib/types";
export const domains = {
  housing: {
    title: "주거·임대",
    subtitle: "계약서 앞에서 막막할 때",
    description: "보증금과 임대계약의 기본 정보를 준비된 자료에서 찾아보세요.",
    label: "주거 안내",
    examples: [
      "보증금은 어떻게 나눠 낼 수 있나요?",
      "임대계약 종료는 어떤 형식으로 알려야 하나요?",
      "보증금 반환 시점을 알려주세요",
    ],
    instruction:
      "독일 주거·임대의 일반 정보를 한국어로 안내한다. 읽은 자료만 근거로 사용하며, 자료가 없는 쟁점은 확인 불가를 설명한다. 개별 사건의 법적 결론을 단정하지 않는다.",
  },
  visa: {
    title: "체류·비자",
    subtitle: "독일에서의 다음 단계를 준비할 때",
    description:
      "유학과 취업 체류의 기본 정보를 공식 출처와 함께 확인해보세요.",
    label: "체류 안내",
    examples: [
      "체류허가를 연장하고 싶어요",
      "유학 체류의 기본 요건을 알려주세요",
      "취업 비자에는 무엇이 필요한가요?",
    ],
    instruction:
      "독일 체류·비자의 일반 정보를 한국어로 안내한다. 현재 목적이 불분명하면 먼저 묻는다. 읽은 자료를 근거로 설명하며 승인 가능성이나 개별 신청 결과를 확정하지 않는다.",
  },
} satisfies Record<
  Domain,
  {
    title: string;
    subtitle: string;
    description: string;
    label: string;
    examples: string[];
    instruction: string;
  }
>;
export function isDomain(value: unknown): value is Domain {
  return value === "housing" || value === "visa";
}
