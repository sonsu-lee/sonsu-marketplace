# OpenAI 프롬프트 지침

지정된 OpenAI 모델, product surface 또는 API 설정이 프롬프트 작성 방식에 영향을 줄 때만 이 파일을 읽는다. 이 문서는 `2026-08-29` snapshot이다. 사용자가 최신 또는 현재 권고를 요청하면 모델별 주장을 하기 전에 현재 OpenAI 공식 문서를 확인한다.

## 공통 구조

결과를 먼저 제시하는 프롬프트를 사용한다. 복잡한 작업에서는 동작을 바꾸는 섹션만 선택한다.

```text
Role: [the model's function and relevant context]

# Goal
[the user-visible outcome]

# Success criteria
[what must be true before the answer or work is complete]

# Constraints
[hard policy, evidence, safety, permission, and scope limits]

# Tools
[non-obvious routing, side effects, and approval boundaries]

# Output
[required content, format, length, and tone]

# Stop rules
[when to ask, retry, fall back, abstain, or finish]
```

모든 섹션을 기본으로 출력하지 않는다. 목표와 출력이 이미 포함된 짧은 요청은 한 문단으로 유지할 수 있다.

## 제품별 사용 지점

### Codex task용 prompt

원하는 저장소 또는 artifact의 결과, 관련 파일이나 맥락, 제약, 권한 경계, 완료 기준과 필요한 검증을 명시한다. 경로 자체가 요구사항이 아니라면 Codex가 workspace를 조사하고 구현 단계를 선택하게 한다. 상시 적용되는 Codex 정책을 반복하거나 에이전트가 직접 선택할 수 있는 명령어를 나열하지 않는다.

### ChatGPT용 user prompt

요청한 결과, 관련 맥락 또는 원본 자료, 독자, 필요한 제약과 출력 형태를 명시한다. 결과가 달라질 때에만 역할이나 personality를 추가한다. 사용자가 요청하지 않았다면 한 번 사용할 요청을 재사용 가능한 system prompt로 바꾸지 않는다.

### Responses API용 prompt

안정적인 identity, 동작과 요청 간 공통 규칙은 `instructions` 또는 적절한 상위 권한 메시지에 둔다. 현재 작업과 동적인 사용자 데이터는 `input`에 둔다. prompt caching이 중요하면 안정적인 내용을 동적인 내용보다 앞에 배치한다.

논리적 섹션을 읽기 쉽게 나누려면 Markdown 제목과 목록을 사용한다. 긴 보조 문서, 예시 또는 신뢰할 수 없는 데이터에 명확한 경계가 필요하면 XML tag를 사용한다. 필수 출력 계약을 표현하거나 확인된 실패를 바로잡는 예시만 유지한다.

API integration이 schema를 강제할 수 있다면 JSON schema를 산문으로 설명하기보다 Structured Outputs를 우선한다. `reasoning.effort`와 `text.verbosity`는 API control로 설정하고, 반복적인 “think harder” 또는 일반적인 간결성 지시로 흉내 내지 않는다.

## 모델 profile

### GPT-5.6 계열

이 profile은 `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`에 적용한다. 공식 지침은 이 모델들을 서로 다른 프롬프트 형식이 아니라 capability, 비용과 throughput으로 구분한다. 평가에서 모델별 실패가 확인되지 않았다면 같은 간결한 결과 우선 구조를 사용한다.

- 일반적인 실행 단계는 모델이 추론하게 한다. 도메인 맥락, 강한 제약, 승인 경계, 성공 기준과 질문을 유발해야 하는 모호함을 제공한다.
- 각 규칙은 한 번만 명시하고 관련 도구만 노출한다. 정책을 반복하면 불필요한 확인과 누적 context 증가를 유발할 수 있다.
- 광범위한 “be concise” 지시를 기본으로 추가하지 않는다. 짧은 답변이 보존해야 할 내용과 생략할 수 있는 내용을 정하거나 API의 `text.verbosity`를 사용한다.
- pro mode에서도 같은 결과 중심 프롬프트를 유지한다. 모델에게 더 깊게 생각하거나 여러 후보를 생성하라고 지시하지 말고 API에서 pro mode와 reasoning effort를 설정한다.
- 여러 단계로 진행하는 작업에는 범위 안에서 안전하게 할 수 있는 동작과, 확인이 필요한 외부·파괴적·유료·범위 확장 동작을 정의한다.

### GPT-5.5

같은 결과 우선 구조를 사용하되, 작업이 오래 걸리거나 도구 사용이 많거나 코딩 중심일 때에는 orchestration을 조금 더 명시한다.

- 기대 결과, 성공 기준, 허용된 side effect, 근거 규칙, 출력 형태와 중단 조건을 명시한다.
- 정확한 경로 자체가 제품 요구사항이 아니라면 세부적인 단계별 지침을 피한다.
- 코딩 에이전트에는 환경이 해당 내용을 제공하지 않을 때에만 재사용 기준, 테스트 또는 검증 요구사항, 인수 기준과 계속 진행할지 도움을 요청할지 결정하는 조건을 추가한다.
- 기본 동작이 직접적이고 작업 중심이므로 고객 대상 작업에는 personality와 협업 방식을 정의한다.
- 재사용 가능한 정적 지시를 앞에 두고 동적 context를 뒤에 둔다. 사용자 지역, 정책 효력 또는 business timezone의 날짜가 중요하지 않다면 현재 날짜를 추가하지 않는다.

### GPT-5.4, GPT-5.3 Codex variant와 다른 GPT-5 모델

공통 결과 우선 구조를 사용한다. 현재 공식 근거 없이 특별한 syntax를 만들거나 동작 차이를 주장하지 않는다. 정확한 최적화가 중요하면 해당 모델의 공식 지침을 확인하고, 더 새로운 모델로 대체하지 말고 원래 모델 이름을 보존한다.

### 알 수 없거나 OpenAI가 아닌 모델

공통된 모델 중립 구조를 사용한다. OpenAI에 한정된 동작 주장을 적용하지 않는다. 사용자가 특정 vendor에 맞춘 최적화를 원하면 가능한 경우 해당 vendor의 원문 문서를 확인한다.

## 최종 모델별 점검

프롬프트를 반환하기 전에 다음을 확인한다.

1. 지정된 모델과 product surface를 보존했다.
2. API 설정을 가짜 자연어 reasoning 지시로 삽입하지 않았다.
3. 모든 섹션이 동작을 바꾼다.
4. 각 규칙이 프롬프트에 한 번만 들어 있다.
5. 중요한 성공 조건, 권한, 근거, 출력과 중단 조건이 남아 있다.

## 공식 출처

- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://learn.chatgpt.com/docs/build-skills
