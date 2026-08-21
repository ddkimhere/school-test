const MODEL = 'gemini-3.5-flash-lite';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;

const ALLOWED_ORIGINS = new Set([
  'https://ddkimhere.github.io',
  'https://yms-grammar-api.vercel.app'
]);

const DIFFICULTIES = new Set(['기본', '중등 내신', '고난도']);

const RESPONSE_SCHEMA = {
  type: 'object',
  properties: {
    errorCount: { type: 'integer' },
    sentences: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          number: { type: 'integer' },
          original: { type: 'string' },
          question: { type: 'string' },
          hasError: { type: 'boolean' },
          wrong: { type: 'string' },
          correct: { type: 'string' },
          grammarPoint: { type: 'string' },
          reason: { type: 'string' }
        },
        required: [
          'number', 'original', 'question', 'hasError',
          'wrong', 'correct', 'grammarPoint', 'reason'
        ]
      }
    }
  },
  required: ['errorCount', 'sentences']
};

function setCors(req, res) {
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
}

function normalize(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

function replaceFirst(text, search, replacement) {
  const index = text.indexOf(search);
  if (index < 0) return null;
  return text.slice(0, index) + replacement + text.slice(index + search.length);
}

function validateInput(body) {
  const sentences = Array.isArray(body?.sentences) ? body.sentences : null;
  const errorCount = Number(body?.errorCount);
  const difficulty = DIFFICULTIES.has(body?.difficulty) ? body.difficulty : '중등 내신';

  if (!sentences || sentences.length < 1 || sentences.length > 60) {
    return { ok: false, message: '문장은 1~60개 범위로 보내 주세요.' };
  }

  const cleaned = sentences.map((item, index) => ({
    num: Number.isFinite(Number(item?.num)) ? Number(item.num) : index + 1,
    eng: normalize(item?.eng)
  }));

  if (cleaned.some(item => !item.eng || item.eng.length > 1200)) {
    return { ok: false, message: '비어 있거나 너무 긴 문장이 포함되어 있습니다.' };
  }

  const maxErrors = Math.min(15, cleaned.length);
  if (!Number.isInteger(errorCount) || errorCount < 1 || errorCount > maxErrors) {
    return { ok: false, message: `오류 개수는 1~${maxErrors}개로 설정해 주세요.` };
  }

  return { ok: true, sentences: cleaned, errorCount, difficulty };
}

function buildPrompt(sentences, errorCount, difficulty, retryReason = '') {
  const passage = sentences.map((s, i) => `${i + 1}. ${s.eng}`).join('\n');

  const levelGuide = {
    '기본': '중1~중2 수준. 수일치, 시제, 조동사, 기본 준동사처럼 핵심 개념을 우선한다.',
    '중등 내신': '중2~중3 실제 학교 내신 수준. 준동사, 분사, 수동태, 관계사, 비교, 시제/완료, 병렬 등을 균형 있게 사용한다.',
    '고난도': '중3 상위권~고1 초반 수준. 문맥을 읽어야 판단할 수 있는 준동사, 분사, 관계사, 시제/태, 병렬구조를 우선하되 답은 하나로 명확해야 한다.'
  }[difficulty];

  return `
너는 대한민국 중학교 영어 내신시험의 어법 문제 출제위원이다.
아래 교과서 원문을 이용해 '문법 오류 찾기' 문제를 만든다.

[난이도]
${difficulty}: ${levelGuide}

[필수 오류 수]
정확히 ${errorCount}개

[원문]
${passage}

[절대 규칙]
1. 문장 수, 문장 순서, 원문의 의미를 바꾸지 않는다.
2. 새로운 내용이나 문장을 추가/삭제하지 않는다.
3. 정확히 ${errorCount}개의 문장에만 오류를 넣고, 한 문장에는 오류를 최대 1개만 넣는다.
4. 오류가 없는 문장은 question이 original과 문자상 동일해야 한다.
5. 오류가 있는 문장은 원문의 '연속된 한 표현' 하나만 다른 '연속된 한 표현' 하나로 바꾼다.
6. wrong은 question 안에 실제로 존재하는 틀린 표현이어야 하고, correct는 original 안에 실제로 존재하는 올바른 표현이어야 한다.
7. question에서 wrong을 correct로 딱 한 번 바꾸면 original과 완전히 같아져야 한다.
8. 철자 오류, 대소문자만 바꾸기, 구두점 오류, 단순 a/an 교체는 금지한다.
9. 뜻을 바꾸는 어휘 문제는 금지한다. 반드시 문법 지식으로 판단하는 오류만 만든다.
10. 답이 두 개 이상 가능하거나 문맥상 논쟁적인 오류는 금지한다.
11. 같은 grammarPoint를 되도록 반복하지 않는다.
12. 오류 위치를 밑줄, 괄호, 별표, 굵게 등으로 표시하지 않는다.

[우선 출제 문법]
- 주어-동사 수일치
- 시제 / 현재완료 / 과거완료
- 능동태 / 수동태
- to부정사 / 동명사
- 현재분사 / 과거분사
- 관계대명사 / 관계부사
- 형용사 / 부사
- 비교급 / 최상급
- 조동사
- 명사 단수/복수
- 접속사
- 병렬구조
- 대명사 형태

[출력 규칙]
- number는 위 원문의 표시 번호(1부터 시작)를 그대로 사용한다.
- original은 원문을 한 글자도 고치지 말고 그대로 복사한다.
- question은 학생에게 보여줄 최종 문장이다.
- hasError=false면 wrong/correct/grammarPoint/reason은 빈 문자열로 둔다.
- hasError=true면 wrong, correct, grammarPoint, reason을 모두 작성한다.
- reason은 교사용으로 한국어 한 문장 이내로 짧게 설명한다.
${retryReason ? `\n[이전 생성 실패 사유]\n${retryReason}\n위 문제를 반드시 수정해 다시 생성한다.` : ''}
`;
}

async function callGemini(apiKey, prompt) {
  const response = await fetch(GEMINI_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-goog-api-key': apiKey
    },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.35,
        maxOutputTokens: 12000,
        thinkingConfig: { thinkingLevel: 'MEDIUM' },
        responseMimeType: 'application/json',
        responseSchema: RESPONSE_SCHEMA
      }
    })
  });

  const raw = await response.text();
  if (!response.ok) {
    let detail = raw;
    try {
      detail = JSON.parse(raw)?.error?.message || raw;
    } catch (_) {}
    throw new Error(`Gemini API ${response.status}: ${detail}`);
  }

  const payload = JSON.parse(raw);
  const text = payload?.candidates?.[0]?.content?.parts
    ?.map(part => part?.text || '')
    .join('')
    .trim();

  if (!text) throw new Error('Gemini가 빈 응답을 반환했습니다.');
  return JSON.parse(text);
}

function validateGenerated(originalSentences, result, requestedErrorCount) {
  if (!result || !Array.isArray(result.sentences)) {
    return { ok: false, reason: 'sentences 배열이 없습니다.' };
  }
  if (result.sentences.length !== originalSentences.length) {
    return { ok: false, reason: '원문과 생성된 문장 수가 다릅니다.' };
  }

  const errors = result.sentences.filter(item => item?.hasError === true);
  if (errors.length !== requestedErrorCount || Number(result.errorCount) !== requestedErrorCount) {
    return { ok: false, reason: `오류 수가 ${requestedErrorCount}개가 아닙니다.` };
  }

  for (let i = 0; i < result.sentences.length; i++) {
    const source = normalize(originalSentences[i].eng);
    const item = result.sentences[i];

    if (Number(item?.number) !== i + 1) {
      return { ok: false, reason: `${i + 1}번 문장 번호가 바뀌었습니다.` };
    }
    if (normalize(item?.original) !== source) {
      return { ok: false, reason: `${i + 1}번 original이 원문과 다릅니다.` };
    }

    const question = normalize(item?.question);
    if (!item?.hasError) {
      if (question !== source) {
        return { ok: false, reason: `${i + 1}번 정상 문장이 수정되었습니다.` };
      }
      continue;
    }

    const wrong = normalize(item?.wrong);
    const correct = normalize(item?.correct);
    const grammarPoint = normalize(item?.grammarPoint);
    const reason = normalize(item?.reason);

    if (!wrong || !correct || !grammarPoint || !reason || wrong === correct) {
      return { ok: false, reason: `${i + 1}번 정답 정보가 불완전합니다.` };
    }
    if (!question.includes(wrong)) {
      return { ok: false, reason: `${i + 1}번 wrong 표현이 문제 문장에 없습니다.` };
    }
    if (!source.includes(correct)) {
      return { ok: false, reason: `${i + 1}번 correct 표현이 원문에 없습니다.` };
    }

    const restored = replaceFirst(question, wrong, correct);
    if (restored === null || normalize(restored) !== source) {
      return { ok: false, reason: `${i + 1}번은 한 표현만 고쳐 원문으로 복원되지 않습니다.` };
    }
  }

  return { ok: true };
}

async function createVerifiedTest(apiKey, sentences, errorCount, difficulty) {
  let retryReason = '';

  for (let attempt = 0; attempt < 2; attempt++) {
    const prompt = buildPrompt(sentences, errorCount, difficulty, retryReason);
    const result = await callGemini(apiKey, prompt);
    const validation = validateGenerated(sentences, result, errorCount);
    if (validation.ok) {
      return {
        ...result,
        model: MODEL,
        difficulty
      };
    }
    retryReason = validation.reason;
  }

  throw new Error(`생성 결과 검증 실패: ${retryReason}`);
}

module.exports = async function handler(req, res) {
  setCors(req, res);

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST 요청만 지원합니다.' });
  }

  const origin = req.headers.origin;
  if (origin && !ALLOWED_ORIGINS.has(origin)) {
    return res.status(403).json({ error: '허용되지 않은 요청 출처입니다.' });
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return res.status(503).json({
      error: '서버에 GEMINI_API_KEY가 설정되지 않았습니다.'
    });
  }

  const input = validateInput(req.body);
  if (!input.ok) return res.status(400).json({ error: input.message });

  try {
    const result = await createVerifiedTest(
      apiKey,
      input.sentences,
      input.errorCount,
      input.difficulty
    );
    return res.status(200).json(result);
  } catch (error) {
    console.error('[grammar-api]', error);
    return res.status(500).json({
      error: '문법 문제 생성에 실패했습니다. 다시 생성해 주세요.',
      detail: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
};
