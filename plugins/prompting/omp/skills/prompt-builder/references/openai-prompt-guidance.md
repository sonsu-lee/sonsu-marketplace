# OpenAI 프롬프트 지침

지정된 OpenAI 모델, product surface 또는 API 설정이 프롬프트 작성 방식에 영향을 줄 때 이 파일을 읽는다. 공통 작성·축약 절차는 [SKILL.md](../SKILL.md#절차)에 있고, 이 파일은 OpenAI 제품별 차이를 다룬다. 모델별 운영 선택은 공유 프로필에 있다. 최신 또는 현재 권고를 요청받으면 모델별 주장을 하기 전에 현재 OpenAI 공식 문서를 확인한다.

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

필요한 섹션만 출력한다. 목표와 출력이 이미 포함된 짧은 요청은 한 문단으로 유지할 수 있다.

## 제품별 사용 지점

### Codex task용 prompt

원하는 저장소 또는 artifact의 결과, 관련 파일이나 맥락, 제약, 권한 경계, 완료 기준과 필요한 검증을 명시한다. 경로 자체가 요구사항일 때만 경로를 지정하고, 나머지는 Codex가 workspace를 조사해 구현 단계를 선택하게 한다. 상시 적용되는 Codex 정책과 에이전트가 직접 고를 수 있는 명령은 생략한다.

### ChatGPT용 user prompt

요청한 결과, 관련 맥락 또는 원본 자료, 독자, 필요한 제약과 출력 형태를 명시한다. 결과가 달라질 때에만 역할이나 personality를 추가한다. 재사용 가능한 system prompt는 사용자가 요청했을 때 만들고, 그 밖에는 한 번 사용할 요청으로 둔다.

### Responses API용 prompt

안정적인 identity, 동작과 요청 간 공통 규칙은 `instructions` 또는 적절한 상위 권한 메시지에 둔다. 현재 작업과 동적인 사용자 데이터는 `input`에 둔다. prompt caching이 중요하면 안정적인 내용을 동적인 내용보다 앞에 배치한다.

논리적 섹션을 읽기 쉽게 나누려면 Markdown 제목과 목록을 사용한다. 긴 보조 문서, 예시 또는 신뢰할 수 없는 데이터에 명확한 경계가 필요하면 XML tag를 사용한다. 필수 출력 계약을 표현하거나 확인된 실패를 바로잡는 예시만 유지한다.

API integration이 schema를 강제할 수 있다면 JSON schema를 산문으로 설명하기보다 Structured Outputs를 우선한다. `reasoning.effort`와 `text.verbosity`는 API control로 설정하고, 반복적인 “think harder”나 일반적인 간결성 지시는 본문에서 덜어 낸다.

## 모델별 적용

[공유 모델 프로필](../../../references/model-profiles.md)은 현재 Astra/Sol/Luna의 기본
운영 선택과 최소 프롬프트 차이를 제공한다. 프롬프트가 필요한 작업에서 해당 차이만 읽고
현재 host/공통 계약에 없는 지시만 더한다. API 지원값은 지정 모델의 현재 공식 문서에서
확인하고, 프로필의 native effort 표는 운영 선택 참고로만 사용한다.

이 marketplace의 최적화 대상은 GPT/Codex다. 사용자 입력에 다른 모델이 있으면 범위를
밝히고 모델 중립 초안을 만들 수 있으며, 설정은 그 모델이 지원하는 항목만 사용한다.
사용자가 지정한 기존 모델은 그대로 유지한다.

## 공식 출처

출처 기준은 [UPSTREAM.md](../../../UPSTREAM.md)에 있다.

- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://learn.chatgpt.com/docs/build-skills
