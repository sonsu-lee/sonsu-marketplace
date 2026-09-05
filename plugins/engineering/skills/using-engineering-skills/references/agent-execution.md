# Agent 실행과 context 계약

스킬은 작업 분류, routing, 검증, 예산과 인계를 소유한다. 별도 agent/session은 구현·조사·리뷰의
집중된 context를 맡는다. 스킬에 모델명을 쓰는 것만으로 모델이나 세션이 바뀌지는 않는다.
controller는 현재 runtime이 제공하는 실행 도구로 적용하고 관측 가능한 결과를 기록한다.
새 중앙 router, 작업별 role 파일 또는 전역 설정 변경을 요구하지 않는다.

## 실행 전에 고정할 정보

기존 plan, task brief, gate ledger와 report를 재사용한다. 같은 정보를 여러 파일에 복사하거나
새 strict JSON schema를 만들 필요는 없다. controller의 실행 기록에는 다음 항목을 연결한다.

```text
Task / Gate: stable ID + 승인된 계약 revision
Artifact: 현재 source/diff revision + 읽을 수 있는 고정 package
Role / Scope: 역할, 필요한 capability, 작업 cwd와 쓰기 소유 범위
Routing: requested model/effort → observed model/effort, 관측 출처 또는 unknown, fallback 이유
Selection: 역할·불확실성에 따른 선택 이유, 적용한 prompt reference/revision, 필요한 team 구성
Session: fresh | resume | fork, 현재/부모 session ID 또는 unavailable
Environment: 검증 명령, runtime/dependencies, 허용된 source와 scratch, network 조건
Budget: 해당 task/gate의 소비량/상한, 남은 부모 예산, deadline, controller의 동시 실행 상한
Result: 실제 실행 완료 상태, 명령/출력의 증거 경로, 열린 finding, 남은 예산
```

source/diff의 revision은 commit SHA 또는 내용 digest로 고정한다. 구현자는 수정할 현재 source를
받고, reviewer는 판정할 artifact와 검증 증거의 고정 사본을 받는다. 수정하면 영향받은 증거를
[품질 게이트 계약](quality-gates.md)에 따라 갱신한다.

요청 옵션, 실제 native metadata와 agent의 자기보고를 구별한다. native 값이 없으면
`observed: unknown`으로 남기며 적용 성공으로 표현하지 않는다. 요청과 관측이 다르면 mismatch를
기록하고 다음 위임 전에 지원 경로를 확인한다. 실제 capability로도 계약을 충족할 수 있고 명시된
사용자 제약을 위반하지 않을 때에만 이유를 기록한 fallback으로 계속한다. 필수 capability나 명시된
모델 제약을 충족할 수 없으면 해당 실행을 `blocked`로 돌려보낸다. 단순히 관측 수단이 없다는
이유만으로 모든 작업을 막거나, 허용되지 않은 설정 변경으로 관측을 강제하지 않는다.

## 실행 환경과 결과

실제 소비 명령에 필요한 환경을 짧게 확인한다. 파일 읽기와 Git fixture 생성, Python import와
pytest collection은 서로 다른 검사다. tool 실패가 난 계층을 확인하고 관련 preflight만 보완한다.
source가 read-only인 reviewer도 shell/test용 writable scratch가 필요할 수 있다. controller가
각 실행의 쓰기 범위와 scratch를 지정하고, 동시 실행끼리 임시 파일·테스트 자원을 공유하지 않게 한다.
비공개 자료 경로를 deny하면서 그 아래 worker 경로만 다시 허용하면 부모 metadata를 읽는 도구가
실패할 수 있으므로 작업 공간과 비공개 자료의 상위 경로를 분리한다. runtime별 실제 권한을 확인한다.

완료 이벤트가 없는 deadline 종료, 취소와 일부 출력은 완성된 답변으로 채점하지 않는다.
`execution: incomplete`와 종료 원인을 기록하고, 만들어진 파일·증거와 소비한 예산을 보존한다.
`incomplete`는 실행 상태이며 gate 상태 이름이 아니다. 예를 들어 deadline 종료와 확인된 pytest
권한 오류가 함께 있으면 `execution: incomplete; cause: deadline; gate: blocked; return: environment-owner`다.
환경을 고친 뒤에도 유효한 코드 검사 근거가 없으면 gate를 통과시키지 않는다.
실행 미완료가 코드 오답이나 context 열화를 증명하지 않는다. 후속 검증에서 확인된 코드 결함은
별도 기록할 수 있지만 미완료 응답 자체를 pass/fail로 바꾸지는 않는다.

## Context와 역할

brief는 목표, 현재 계약과 근거, 쓰기 소유 범위, 필수 검증과 완료 조건을 중심으로 작성한다.
공통 정책은 한 곳에서 참조하고 같은 지시를 여러 역할에 반복 복사하지 않는다. controller는
모델, reasoning effort, team 구성을 별도로 선택한다. 모델의 이름만 바꾸면서 역할·context·검증
조건까지 암묵적으로 바꾸지 않는다. 모델별 조정은 platform reference를 사용하며 공통 권한과
품질 게이트를 약화하지 않는다.

- 승인 계약·외부 동작·권한·쓰기 소유 범위가 바뀌거나 필수 규칙 누락·계약 모순이 있으면,
  implementer는 해당 결정과 의존 작업을 멈추고 controller에게 필요한 결정과 근거를 반환한다.
  controller는 확인된 승인으로 해결할 수 있는지 판단하고, 새 사용자 결정이 필요한 경우에만
  요청한다. 그 결정과 독립적인 승인 작업은 계속한다.
- 기존 관례로 정할 수 있는 private 이름이나 동등한 내부 표현은 직접 선택하고 필요한 가정만
  보고한다. 필수 business rule과 권한을 일상적인 선택으로 취급하지 않는다.
- 현재 revision의 필수 검사가 충족되고 새 변경·실패·미해결 위험이 없으면 해당 검증을 끝낸다.
  후속 필수 리뷰·red-team은 유지하며, 확신을 더 얻으려고 무관한 suite나 같은 검사를 반복하지 않는다.

- **Implementer:** 승인 계약, 적용할 의사코드, 현재 source와 검증 환경을 받는다. 같은 task의
  집중 수정에는 열린 finding, 새 반례와 현재 revision을 전달한다. 오래된 session 기억을 현재
  source의 증거로 사용하지 않는다.
- **Reviewer:** fresh context에서 승인 계약, 고정 source/diff와 사실 중심 검증 자료를 받는다.
  controller는 원 report에서 명령·출력, 변경 범위와 제약을 복사하되 구현 서사·자기 정당화·자체
  pass 판정·칭찬은 제외한다. 원 report는 controller 기록으로 보존한다. 독립적인 최초 리뷰들에는
  서로의 finding을 먼저 보여 주지 않는다. 재리뷰에는 검증할 기존 finding과 수정 근거를 제공한다.
- **Red-team:** 일반 최종 리뷰 뒤 현재 전체 목표와 가정을 fresh context에서 검토한다.
  기존 immutable bundle과 finding-to-fix provenance 계약을 따른다.
- **Specialist:** 독립된 위험이나 자료 조사에만 추가한다. 전체 범위 reviewer를 전문 관점들의
  합이나 다수결로 대체하지 않는다. controller가 필요성과 유한한 호출·동시수 예산을 정한다.

session lineage와 agent identity는 controller의 복구 기록이다. fresh reviewer/fix implementer에게
이전 session ID나 transcript를 탐색하라고 보내지 않는다. 별도 session도 같은 파일을 공유할 수
있다. 병렬 실행의 소유 범위와 통합은 [dispatching-parallel-agents](../../dispatching-parallel-agents/SKILL.md)를
따르고, SDD 기본 task loop는 직렬로 유지한다.

## 수정 회차와 인계

3+2/max5는 운영 기본값이며 모델의 최적 횟수나 세 번째 이후 열화를 입증한 값이 아니다.
더 낮은 stage 상한과 Fast Path 예산은 계속 우선한다.

- 같은 task 수정 1–3회는 원 implementer를 재개한다. 원 agent가 없거나, 새 반례에도 같은
  잘못된 가정을 반복해 진전이 없으면 3회 전에도 fresh 진단·수정으로 전환할 수 있다.
- 4–5회는 사실 중심 handoff로 fresh implementer를 사용한다. 복잡도와 확인된 실패 원인에
  맞는 capability를 선택하며 회차만으로 특정 모델이나 더 높은 effort를 강제하지 않는다.
- handoff에도 같은 task/gate ID, 현재 revision, 소비·남은 예산과 deadline을 전달한다.
  session/model/owner/package 교체는 예산을 초기화하지 않는다. 조기 fresh 진단도 같은
  부모 예산 안에 포함하며 중첩 호출에 새 max5를 주지 않는다.
- 새 정보 없이 같은 시도를 반복하지 않는다. 필요한 검증을 충족하면 상한 전에도 끝낸다.
  서로 다른 작업 세 개를 완료했다고 session 전체를 자동 폐기하지 않는다.

## Platform 적용

Codex의 구체적인 역할 표와 schema 대응은 [codex-tools.md](codex-tools.md)를 따른다.
`fresh`는 이전 이력을 상속하지 않는 실행, `resume`은 같은 세션 재개, `fork`는 기존 이력을
분기하는 실행이다. 각 platform의 이름보다 실제 이력 전달 동작을 확인한다.

Claude Code에서는 설치 버전이 지원하는 subagent model/effort, 별도 context와 resume 설정으로
같은 의도를 표현한다. 지원되지 않는 필드를 만들거나 Codex 모델명을 그대로 전달하지 않는다.
Codex와 Claude의 같은 effort 문자열을 같은 계산량으로 취급하지 않는다. 공식 설정이나 도구
schema만으로 그 모델의 성능이나 전체 workflow 동작이 검증됐다고 주장하지 않는다.

참고: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Claude Code subagents](https://code.claude.com/docs/en/sub-agents),
[Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
