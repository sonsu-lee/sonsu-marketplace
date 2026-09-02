# 0006 Keep Prompting Independent

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-02 현재 대화에서 독립 `Prompting` 플러그인 제안과 적용을 명시적으로 승인했습니다.

## Context

기존 standalone `prompt-builder`는 Codex, ChatGPT와 OpenAI API에서 사용할 프롬프트를
생성·재작성·최적화합니다. Codex 작업 프롬프트를 다룬다는 점에서는 Engineering과, 반복 가능한
작업 산출물을 만든다는 점에서는 Workflow와 표면이 일부 겹치지만, 실제 책임은 소프트웨어
구현 방법이나 Git delivery가 아니라 프롬프트 산출물입니다.

마켓플레이스는 책임과 업데이트 경계에 따라 플러그인을 독립적으로 설치하는 결정을 이미
[0003](0003-keep-plugins-independent.md)에 기록했습니다. `prompt-builder`도 다른 플러그인의
설치나 선행 실행 없이 사용할 수 있고 Codex 외의 제품 surface까지 다루므로, 기존 플러그인에
포함할지 별도 플러그인으로 둘지 결정해야 합니다.

## Decision

`prompt-builder`를 `Prompting`이라는 독립 플러그인으로 배포합니다. 플러그인 ID와 디렉터리는
`prompting`과 `plugins/prompting/`, 스킬 ID는 `prompting:prompt-builder`를 사용합니다.

Prompting은 사용자가 실제로 사용할 프롬프트의 생성·재작성·최적화를 요청했을 때 선택합니다.
prompt engineering 개념 설명만 요청하거나 일반 구현 요구사항을 전달했다는 이유만으로 선택하지
않습니다. Prompting과 다른 플러그인은 서로의 설치나 특정 skill ID를 필수로 가정하지 않으며,
한 요청에 프롬프트 산출물과 다른 책임이 함께 있을 때에만 runtime에서 조합합니다.

기존 standalone의 `SKILL.md`, `agents/openai.yaml`과 OpenAI prompt guidance snapshot을 함께
배포합니다. snapshot은 특정 OpenAI 모델이나 제품 surface가 프롬프트 구성을 바꿀 때만 읽고,
최신 또는 현재 권고를 요청받으면 OpenAI 공식 문서를 다시 확인합니다.

## Alternatives Considered

- Workflow에 포함: 반복 가능한 산출물을 만든다는 공통점은 있지만 Workflow의 현재 책임인
  branch·commit·ticket·PR과 프롬프트 작성의 업데이트 경계가 다릅니다.
- Engineering에 포함: Codex 작업 프롬프트와 개발 요청이 만날 수 있지만 ChatGPT와 OpenAI API용
  프롬프트까지 개발 lifecycle에 결합하고 일반 구현 요청에도 불필요한 라우팅 경쟁을 만듭니다.
- standalone 스킬로 계속 유지: 설치 구조는 가장 작지만 마켓플레이스의 버전 관리, 문서화와
  플러그인 단위 배포 흐름에서 제외됩니다.
- 플러그인과 스킬을 모두 `prompt-builder`로 명명: 구성은 직접적이지만
  `prompt-builder:prompt-builder`라는 중복 namespace보다 `prompting:prompt-builder`가 플러그인
  책임과 스킬 동작을 구분하기 쉽습니다.

## Consequences

Prompting은 한 개 스킬만 포함하더라도 다른 플러그인과 독립적으로 설치하고 업데이트할 수
있습니다. `prompting:prompt-builder`는 프롬프트 산출물 요청과 개념 설명 near-miss를 description과
routing fixture로 구분해야 합니다.

기존 standalone `prompt-builder`와 Prompting을 동시에 노출하면 같은 요청에 두 스킬이 경쟁할 수
있습니다. 플러그인판을 격리 검증한 뒤 실제 사용 환경에서는 standalone 복사본을 discovery
경로에서 제외해야 합니다.

포함된 OpenAI guidance는 고정 snapshot이므로 모델과 API 권고가 바뀔 수 있습니다. 최신성이
중요한 요청에서는 공식 문서 확인을 생략하지 않으며, snapshot 갱신과 플러그인 버전 변경을 함께
검토합니다.

## Revisit When

프롬프트 요청과 Engineering 또는 Workflow의 잘못된 동시 선택이 반복될 때, 독립 설치 비용이
실제 사용에서 이점보다 커질 때, 또는 prompt evaluation처럼 함께 배포해야 할 책임이 추가되어
플러그인 경계를 다시 정의해야 할 때 재검토합니다.
