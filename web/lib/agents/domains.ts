import type { Domain } from "@/lib/types";
export const domains = {
  housing: {
    title: "주거·임대",
    subtitle: "계약서 앞에서 막막할 때",
    description: "보증금과 임대계약의 기본 정보를 준비된 자료에서 찾아보세요.",
    label: "주거 안내",
    eyebrow: "HOUSING & RENT",
    // 채팅을 먼저 보여주고 설명을 오른쪽에 두는 구성
    layout: "chat-first" as const,
    theme: {
      iconWrap: "bg-blue-50 text-blue-600",
      userBubble: "bg-blue-600",
      exampleHover: "hover:border-blue-300 hover:bg-blue-50",
      dot: "bg-blue-500",
    },
    examples: [
      "보증금은 어떻게 나눠 낼 수 있나요?",
      "임대계약 종료는 어떤 형식으로 알려야 하나요?",
      "보증금 반환 시점을 알려주세요",
    ],
    sidebar: [
      {
        title: "지금 읽는 자료",
        body: "BGB §551·§568의 보증금·계약 종료 조항을 사람이 확인한 짧은 한국어 요약입니다. 실시간 검색이 아닙니다.",
      },
      {
        title: "이럴 때 유용해요",
        body: "보증금 분할 납부, 계약 종료 통지 형식, 보증금 반환 시점처럼 계약서에 자주 나오는 쟁점을 확인할 때.",
      },
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
    eyebrow: "VISA & RESIDENCE",
    // 준비 단계를 왼쪽에 먼저 보여주고 채팅을 오른쪽에 두는 구성
    layout: "steps-first" as const,
    theme: {
      iconWrap: "bg-emerald-50 text-emerald-600",
      userBubble: "bg-emerald-600",
      exampleHover: "hover:border-emerald-300 hover:bg-emerald-50",
      dot: "bg-emerald-500",
    },
    examples: [
      "체류허가를 연장하고 싶어요",
      "유학 체류의 기본 요건을 알려주세요",
      "취업 비자에는 무엇이 필요한가요?",
    ],
    steps: [
      "체류 목적(유학·취업) 정하기",
      "목적별 요건과 서류 확인",
      "연장·전환 조건 살펴보기",
    ],
    sidebar: [
      {
        title: "지금 읽는 자료",
        body: "Make it in Germany의 유학·전문인력 취업 안내를 사람이 확인한 짧은 한국어 요약입니다. 실시간 검색이 아닙니다.",
      },
      {
        title: "먼저 확인하세요",
        body: "목적이 분명하지 않으면 데모가 유학인지 취업인지 먼저 되묻습니다. 승인 가능성이나 개별 신청 결과는 판단하지 않습니다.",
      },
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
    eyebrow: string;
    layout: "chat-first" | "steps-first";
    theme: {
      iconWrap: string;
      userBubble: string;
      exampleHover: string;
      dot: string;
    };
    examples: string[];
    steps?: string[];
    sidebar: { title: string; body: string }[];
    instruction: string;
  }
>;
export function isDomain(value: unknown): value is Domain {
  return value === "housing" || value === "visa";
}
