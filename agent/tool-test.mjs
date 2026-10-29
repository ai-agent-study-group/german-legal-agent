import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.NVIDIA_API_KEY,
  baseURL: 'https://integrate.api.nvidia.com/v1',
  timeout: 60_000, // 기본값은 10분이라 멈춘 것처럼 보인다. 60초 안에 응답이 없으면 에러를 낸다
  maxRetries: 0, // 기본값은 2회 자동 재시도. 재시도하면 대기 시간이 몇 배로 늘어나서 끈다
});

const MODEL = 'nvidia/nemotron-3.5-lightning-30b-a3b';
// const MODEL = 'deepseek-ai/deepseek-v4.1-flash';

// 1) "법 데이터베이스" 대신 쓰는 가짜 데이터 (설명용 요약본, 실제 법률 조언용 아님)
const LAWS = {
  'BGB §551': '임대차 보증금(Mietkaution)은 월 순임대료(Nettokaltmiete)의 최대 3배까지 가능하다.',
  'BGB §573c': '세입자의 일반 해지 통지 기간은 3개월이다.',
};

// 2) 도구(tool): 키워드로 조문을 찾는 자바스크립트 함수
function searchLaw(keyword) {
  const hits = Object.entries(LAWS)
    .filter(([name, text]) => text.includes(keyword) || name.includes(keyword))
    .map(([name, text]) => `${name}: ${text}`);
  return hits.length ? hits.join('\n') : '검색 결과 없음';
}

// 3) 모델에게 "이런 도구가 있다"고 알려주는 설명서 (OpenAI 형식)
const tools = [
  {
    type: 'function',
    function: {
      name: 'search_law',
      description: '독일 법 조문 DB에서 키워드로 조문을 검색한다.',
      parameters: {
        type: 'object',
        properties: { keyword: { type: 'string', description: '검색할 키워드' } },
        required: ['keyword'],
      },
    },
  },
];

const messages = [
  {
    role: 'system',
    content:
      '너는 독일 법률 정보 도우미다. 반드시 search_law 도구로 찾은 조문만 근거로 답하고, 조문 번호를 인용해라.',
  },
  { role: 'user', content: '독일에서 월세 보증금은 최대 얼마까지 받을 수 있어?' },
];

// 4) 최소 루프. 무료 한도와 폭주 방지를 위해 호출 횟수 상한을 둔다.
const MAX_CALLS = 1;

for (let i = 1; i <= MAX_CALLS; i++) {
  console.log(`\n[호출 ${i}] ${MODEL} 요청 보냄 (제한 60초)...`);
  const t0 = Date.now();
  let res;
  try {
    res = await client.chat.completions.create({
      model: MODEL,
      messages,
      tools,
      max_tokens: 2048, // 추론(reasoning) 모델은 생각하는 데도 토큰을 쓰므로 넉넉히
    });
  } catch (err) {
    console.error(`[실패] ${((Date.now() - t0) / 1000).toFixed(1)}초 후: ${err.name} status=${err.status ?? '-'} ${err.message}`);
    process.exit(1);
  }

  const msg = res.choices[0].message;
  console.log(`[호출 ${i}] ${((Date.now() - t0) / 1000).toFixed(1)}초 걸림, finish_reason=${res.choices[0].finish_reason}`);

  // 모델의 응답을 대화 기록에 추가 (reasoning_content 같은 부가 필드는 빼고 필요한 것만)
  messages.push({ role: 'assistant', content: msg.content, tool_calls: msg.tool_calls });

  if (!msg.tool_calls?.length) {
    console.log('[최종 답변]', msg.content);
    break;
  }

  for (const call of msg.tool_calls) {
    const args = JSON.parse(call.function.arguments); // 인자는 JSON "문자열"로 온다
    const result = searchLaw(args.keyword);
    console.log(`[도구 호출] ${call.function.name}(${JSON.stringify(args)}) -> ${result}`);
    messages.push({ role: 'tool', tool_call_id: call.id, content: result });
  }
}
