## Subagent 위임에는 multi-agent 지원이 필요하다

현재 노출된 collaboration 도구와 schema를 먼저 확인한다. 로컬 Codex는 사용자 또는 적용되는
프로젝트·스킬 지시가 위임을 요청할 때 subagent를 생성한다. 도구 존재나 Ultra 선택만으로
재귀 위임을 허용하지 않는다. 도구가 이미 제공되는 실행에는 설정 변경이 필요하지 않다.
사용자가 설정을 요청한 경우에만 설치된 제품·버전이 지원하는 설정을 적용한다.

로컬 Codex CLI 0.152.1의 `features --help`는 `--enable multi_agent`가
`-c features.multi_agent=true`와 동등하다고 안내한다. 이 feature flag의 설정 형식은 다음과 같다.

```toml
[features]
multi_agent = true
```

공식 문서(2026-09-06)는 `[agents] enabled = true`와 기본 true를 안내하지만, CLI 0.152.1의
`features list`에서 두 키를 각각 단독으로 바꿔 확인하니 `agents.enabled=false/true`는 baseline의
활성 상태(true)를 바꾸지 않았고 `features.multi_agent=false/true`는 각각 false/true로 표시됐다.
이 문서의 키를 모든 Codex surface에 그대로 적용하지 않는다. 현재 host의 capability와
실제 설정 효과를 확인한다. `agents.max_concurrent_threads_per_session`은 활성화와 별개인
동시수 설정이다(주 agent 제외). [공식 subagent 설정](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)

- **생성:** `spawn_agent {fork_turns: "none"}`으로 child에게 깨끗한 context를 제공한다.
  현재 도구의 기본값 `"all"`은 전체 transcript를 child에 복사하며 이 경우 model/effort override가
  허용되지 않을 수 있다. 사용자 지정 role 파일은 `~/.codex/agents/` 또는 `.codex/agents/`에
  둘 수 있지만 현재 schema에 없는 `agent_type`을 전송하지 않는다.
  현재 tool schema가 허용하는 `fork_turns`와 model override 조합을 신뢰한다. 격리 reviewer는
  `fork_turns: "none"`을 사용하고 필요한 artifact만 prompt에 넣는다.
- **수정 회차:** 1~3회차는 `followup_task`로 원래 implementer를 재개한다. direct 실행은 controller가
  계속한다. 원래 agent를 재개할 수 없거나 새 반례에도 잘못된 가정이 반복되어 진전이 없으면
  사실 중심 handoff로 새 implementer를 만든다.
  4~5회차는 `spawn_agent {fork_turns: "none"}`으로 새 관점을 확보하고 현재 finding에 적합한 모델과
  추론도를 선택한다. 승인된 brief, 현재 exact artifact package, 미해결 finding, 실제 명령·결과와 이미 실패한
  접근을 전달한다. 관찰과 가설을 구분하고 전체 대화, 자기 정당화와 이전 pass/praise는 제외한다.
  구체적인 handoff는 `executing-plans/fix-implementer-prompt.md`를 따른다. session 변경은 task 예산을
  초기화하지 않으며 Fast Path는 별도의 더 낮은 예산과 재진입 금지 규칙을 따른다.
- **Lifecycle:** 현재 surface의 완료 이벤트와 agent 상태를 확인한다. `close_agent`가 없으면
  호출하지 않는다. 완료된 agent의 slot 회수·재사용은 runtime에 맡기고 추정한 종료 명령을 만들지 않는다.
- **모델 이름:** 현재 spawn allowlist와 대조하지 않고 스킬, 표 또는 이전 session의 모델 이름을
  `spawn_agent`에 복사하지 않는다. 모델별 지원 effort도 함께 확인한다.

## Child를 기다리는 방법

`wait_agent`는 poll이 아니라 event subscription이다. 길게 기다려도 child가 mailbox 활동을
만드는 순간 짧은 대기와 같은 latency로 깨어난다. 짧은 timeout polling은 이득 없이 poll마다
도구 호출과 context 재처리 비용을 낸다. 측정한 session에서는 전체 wait 호출의 약 3분의 2가
timeout된 짧은 poll이었다.

- 아직 로컬 작업이 남아 있으면 기다리지 않는다. 완료된 child의 최종 답변은 mailbox로
  전달되어 다음 turn에 도착한다.
- 처리 중인 child가 있고 실제로 할 일이 없을 때에는 `timeout_ms` 300000-600000(5-10분)으로
  `wait_agent`를 사용해 제한된 구간 동안 기다린다. 각 구간에서 깨어나거나 timeout된 뒤 상태를
  한 줄로 알리고 `list_agents`를 실행하며, 보고 없이 완료한 child를 확인한다. 5분 미만의 poll을
  연달아 사용하지 않는다. event subscription은 제한된 긴 대기도 짧은 대기만큼 빨리 깨운다.
- 완료 mail은 대기 중인 controller를 깨우지 못한다(turn을 시작하지 않고 전달된다).
  이 idle 구간을 담당하는 것이 `wait_agent`의 유일한 역할이다. 활동 없이 timeout되면 다음
  대기 시간을 줄이지 말고 상태를 다시 맞춘다.

## 생성 시 모델 routing

위임이 허용된 controller가 생성할 때 `spawn_agent`의 실제 schema가 두 override를
모두 지원하면 실행 중인 스킬의 Model Selection 규칙에 따라 `model`과 `reasoning_effort`를 함께
명시한다. 한쪽만 설정하면 의도하지 않은 기본값을 쓰거나 schema validation에 실패할 수 있으므로
부분 override는 하지 않는다.

공식 설정의 `model_reasoning_effort`와 spawn 도구의 `reasoning_effort`는 서로 다른 입력
표면의 이름이다. 둘을 바꾸어 전송하지 않는다. custom agent 파일의 model/effort가 앞서
결정된 spawn·default·parent 값을 덮어쓸 수 있으므로 사용한 role 파일도 확인한다. 설정을
생략하면 parent/default를 상속할 수 있으며, 본문에 모델명이나 “깊게 생각하라”를 쓰는 것으로
실행 설정이 바뀌지 않는다. [설정 우선순위](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)

실제 schema가 두 field 중 하나라도 지원하지 않으면 존재하지 않는 field를 보내지 않는다. 노출된
`agent_type`, role 또는 preset이 있으면 같은 역할의 가장 가까운 조합을 사용하고, 그렇지 않으면
아래 machine-level default를 사용하되 `routing_fallback: tool-schema-no-explicit-overrides`를
기록한다. 필요한 capability를 어떤 지원 경로로도 제공할 수 없을 때에만 해당 reviewer를
`blocked`로 판정한다. tool metadata의 부재를 무시하고 잘못된 호출을 반복하지 않는다.

machine-level backstop은 사용자가 설정을 요청했을 때 선택할 수 있는 보완책이다. 다음 설정을
자동으로 쓰거나 매 작업마다 설정 승인을 요구하지 않는다. 현재 도구로 가능한 명시적 routing을 우선한다.

```toml
[agents]
default_subagent_model = "<a mid-tier model from your spawn allowlist>"
default_subagent_reasoning_effort = "medium"
```

현재 allowlist가 다음 조합을 지원하면 역할별 기본값으로 사용한다. 실제 tool metadata가 다르면
같은 역할을 처리할 수 있는 가장 가까운 허용 조합을 선택하고 fallback을 기록한다.

| 역할 | Model | Reasoning effort |
| --- | --- | --- |
| 정확한 문자열·metadata·경로 변경 | controller의 결정론적 도구 | 해당 없음 |
| 좁은 탐색·명시적 계약의 작은 구현·국소 수정 | `gpt-5.6-luna` | `medium` |
| Fast Path 범위 판정 | controller 직접 실행 | 해당 없음 |
| Mechanical Fast Path와 Code Mode orchestration | controller 직접 실행 | 해당 없음 |
| 탐색 결과 정리·일반 task review | `gpt-5.6-terra` | `medium` |
| 계약·해법이 분명한 여러 모듈·상태·복구·Bash/Git/파일시스템 통합 구현·debugging | `gpt-5.6-terra` | `high` |
| 요구 해석·해법 선택이 모호한 복잡한 구현·debugging | `gpt-5.6-sol` | `medium`; 복잡한 논리·가정·경계 검토는 `high` |
| 범위가 제한된 기계적 re-review | `gpt-5.6-luna` | `medium` |
| fix round 4–5 fresh implementer | 현재 finding의 역할 적합 모델; 회차별 고정 승격 없음 | 복잡도·실패 원인에 맞춤 |
| 영향 큰 architecture·구현 plan·어려운 원인 판단 | `gpt-5.6-sol` | `high` |
| 일반 final whole-change review | `gpt-5.6-sol` | `medium`; 복잡한 논리·가정·경계 검토는 `high` |
| fresh-context red-team whole-structure review | `gpt-5.6-sol` | `high` |
| 위 역할 중 여러 시스템·도구·단계를 아우르며 지속적인 판단이 필요한 가장 어려운 작업 | `gpt-6-astra` | `medium`; 깊은 분석·경계 검증이 필요하면 `high` |

이 표는 측정으로 보장된 최적 조합이 아니라 시작 기본값이다. 파일 수보다 판단의 어려움,
불확실성, 실패 비용과 총 완료 시간(재탐색·tool 왕복·재작업 포함)으로 조정한다. 문장으로만 주어진
모호한 구현은 작은 파일이어도 중간 tier 이상이 적합할 수 있다. 같은 형태의 독립적인 기계적 변경은
하나로 묶고, 결정론적 실행으로 끝낼 수 있으면 위임하지 않는다.

모델과 추론도는 별도로 선택한다. Sol은 복잡하고 모호한 작업의 정상적인 선택 후보이며,
Astra도 해당 역할에서 처음부터 선택할 수 있다. Luna→Terra→Sol→Astra를 순서대로 거치거나
회차만으로 승격하지 않는다. 사용자 지정·현재 allowlist를 우선하고 선택 이유를 brief에 남긴다.

위 표는 [공식 모델 역할·추론도 안내](https://learn.chatgpt.com/docs/models)에 따른 잠정 운영값이다.
일반 리뷰의 Sol medium과 red-team의 Sol high도 해당 workflow에서 비교 검증된 최적값은 아니다.
작은 tool-free 리뷰에서는 모든 설정이 사전 결함을 찾았고 사후 추가 결함에서 차이가 관찰됐다.
후속 tool-enabled 실험은 Sol과 Terra high 구현을 비교하지 않았으며, 완료된 한 artifact 리뷰에서는
Astra medium/high가 같은 결함을 찾았다. 이 결과는 Sol 제외나 모든 리뷰의 high 필수화를 지지하지 않는다.
공식 안내, 로컬 관찰과 미검증 선택의 구분은 [ADR 0012](../../../../../docs/decisions/0012-use-role-routing-and-execution-evidence.md)를 따른다.

Luna보다 낮은 모델로 내리는 것도 총 완료 비용의 근거가 있을 때 선택한다. 현재 가격·속도 설정,
입력·캐시·출력·추론량, tool 왕복과 재작업을 함께 비교하며 단가나 token 수만으로 최적이라고 하지 않는다.

`low`, `xhigh`, `max`와 `ultra`를 새 상시 기본값으로 두지 않는다. Fast Path에는 classifier,
implementation 또는 reviewer subagent를 기본으로 만들지 않는다. 독립 판단이 필요할 만큼 불확실하면
일반 workflow로 올린다. model 상향은 변경 없는 입력을 다시 시도할 근거가 아니다.

### 모델·추론도·팀을 따로 선택한다

기존 medium/high 기본값을 기준선으로 유지하고 다음 조건에서 선택적으로 조정한다.

| 선택 | 조건과 확인할 근거 |
| --- | --- |
| `low` / Light | 정답 형태와 범위가 명확한 조회·추출·짧은 후속 작업. 낮춰도 필수 근거와 정확성이 유지되는지 비교 |
| `medium` | 일반적인 agent 작업의 균형점. Astra의 어려운 전체 작업도 우선 후보 |
| `high` | 복잡한 논리, 상태·복구·권한 경계와 가정을 추적해야 하는 역할 |
| `xhigh` / Extra High | high에서 남는 중요한 분석 문제에 추가 판단이 유효한지 비교 |
| `max` | 속도·사용량보다 깊이가 중요한 가장 어려운 단일 문제. 해당 단계가 끝나면 다음 역할에 맞게 재선택 |
| `ultra` | 독립 부분으로 나뉘는 복합 작업 후보. 실제 host의 effort 지원과 위임 trigger·동시수·재귀 제한을 별도로 확인 |

API의 effort 목록을 Codex allowlist로 사용하지 않는다. Ultra는 공식 모델 안내에서 subagent를
활용하는 실행으로 설명하지만, 로컬 위임은 사용자 또는 프로젝트·스킬 지시를 따른다. worker와
reviewer의 재위임 금지는 유지한다. 같은 effort 이름이 다른 모델의 같은 품질·계산량을 뜻하지
않으며 `Terra high = Sol medium` 같은 등식을 만들지 않는다.

Astra를 처음부터 선택할 예는 브라우저 재현·API·저장소 상태를 오가며 원인을 좁히는 장애,
여러 서비스의 권한·데이터·복구 계약을 함께 바꾸는 구현, 개별 task 결과를 전체 사용자 목표와
연결하는 어려운 검증이다. 여러 파일이라는 이유만으로 선택하지 않는다. 여러 도구가 있어도
작업 사이에 새 판단이 없는 반복 변환은 결정론적 실행으로 처리한다.

### 역할별 실행 순서

| 작업 | 소유와 인계 |
| --- | --- |
| 분류·작은 변경 | controller 직접 처리. Fast Path에는 기본 team을 만들지 않음 |
| 설계·계획 | Sol 또는 어려운 전체 작업의 Astra가 결정 책임. 조사자는 독립된 근거만 반환 |
| task 구현 | task별 구현자 한 명. SDD 기본 loop는 직렬; 병렬 구현에는 닫힌 계약·독립 쓰기 범위 또는 별도 worktree와 통합 소유자 필요 |
| task 검증·리뷰 | 결정론적 검증 뒤 fresh reviewer. 구현 이력 대신 계약·고정 artifact·검증 사실을 전달 |
| 전체 통합·리뷰 | 통합 소유자 한 명과 전체 변경 reviewer. 전문 리뷰는 명명된 독립 위험에만 추가 |
| red-team·수정 | 일반 전체 리뷰 뒤 별도 fresh red-team. 수정은 같은 task 예산과 영향 기반 재검증 규칙 유지 |

controller는 독립성과 예상 이득을 확인한 작업만 위임하고 유한한 동시수·호출 예산을 정한다.
2–3개의 독립 worker는 비교를 시작할 수 있는 예시이지 최적값이나 필수 최소수는 아니다.
역할 수와 동시 실행 수는 다르다. 같은 파일·브라우저 세션·테스트 DB·port를 함께 쓰면 자원
소유권을 분리하거나 직렬화한다. 작은 작업에서 새 agent를 만들어 controller 모델을 바꾸는
간접 경로를 사용하지 않는다.

### 모델별 prompt 조정

목표·근거·제약·완료 조건을 보존하고 같은 지시는 한 번만 전달한다. 아래 차이는 모델별
복제 스킬이 아니라 기존 brief에 필요한 부분만 적용한다.

| 모델 | brief에서 강조할 내용 |
| --- | --- |
| Luna | 좁은 대상, 입력·기대 결과, 필요한 경계 사례와 범위 밖 결정의 반환 조건 |
| Terra | 담당 범위, 확인할 경로·자료, 근거를 포함한 짧은 결과와 controller 인계 지점 |
| Sol | 목표·tradeoff·완료 기준, 해법을 제한하는 실제 계약. 해법 선택과 무관한 절차 나열은 줄임 |
| Astra | 승인된 작업의 지속, 결과를 바꾸는 질문 조건, 허용된 독립 위임 범위와 검증 종료 조건 |

GPT-5.6 지침은 Sol과 제품군 공통 가이드다. Luna·Terra의 위 조정은 공식 역할 안내에서 도출한
운영 권고이며 별도 전용 프롬프트의 검증 결과가 아니다. Astra는 스킬 지시에 민감하므로
“모든 불확실성에서 질문”과 “일상적인 선택은 진행” 같은 충돌을 먼저 제거한다. 중단이 필요하면
읽은 스킬의 정확한 규칙과 실제 필요한 결정을 controller에 반환한다. 기존 권한을 다시 받는
절차, 무조건적인 재귀 위임이나 반복 검증을 추가하지 않는다.

공식 근거: [Codex 모델·추론도](https://learn.chatgpt.com/docs/models),
[GPT-5.6 prompt 가이드](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6),
[Astra prompt 가이드](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices).

생성 뒤에는 [공통 실행 계약](agent-execution.md)에 따라 요청값과 native 관측값을 별도 기록한다.
현재 surface의 spawn 결과·실행 metadata·CLI turn context 중 실제 제공되는 출처를 사용한다.
자기보고나 요청 JSON만으로 적용을 확인하지 않는다. 관측 불가와 mismatch는 각각 그대로 남기고
필수 capability·사용자 제약 충족 여부에 따라 fallback 또는 blocked를 결정한다.
fresh/resume/fork와 parent/session ID는 controller 기록에 남기되 fresh child에게 이전 이력을
읽게 하지 않는다. 이 계약을 구현하기 위해 사용자 설정을 자동으로 덮어쓰지 않는다.

## Code Mode

현재 surface가 `functions.exec` 또는 동등한 JavaScript orchestration을 제공하고 작업이 결정론적인
tool 호출로 표현되면 Code Mode를 우선한다. 독립적인 read-only 검사, 참조·잔여 pattern 검색,
JSON/YAML parse, formatter·canonical generator, mechanical transform과 postcondition 검사를 한
호출에서 안전하게 구성하고 같은 입력의 결정론적 validation을 반복 가능하게 만들 수 있다.

Code Mode는 실행 수단이지 Fast Path 또는 quality pass의 근거가 아니다. public contract, DB
migration, 인증·권한, dependency major update, broad delete와 의미 판단이 필요한 치환을
기계적인 작업으로 낮추지 않는다. 현재 runtime의 파일 편집, destructive action과 권한 규칙을
그대로 적용하고, 변경 뒤 전체 diff와 실제 consumer command를 검증한다. Code Mode로 승인이나
Git 권한을 우회하거나 script의 exit 0만으로 안전·완료를 주장하지 않는다. 파일 편집에
`apply_patch`가 요구되는 runtime에서는 orchestration 안에서도 같은 규칙을 지킨다.

Mechanical Fast Path의 변환에는 전체 참조 집합의 사전 확인, 변환 뒤 old pattern 0건,
unexpected new pattern과 unrelated diff 확인, syntax/parser 검사, 실제 consumer가 사용하는 가장
작은 build·test·loader 또는 consuming command를 postcondition으로 둔다.

## Goal lifecycle

Codex goal은 사용자가 goal 사용을 명시적으로 요청한 경우에만 만든다. plan-backed 작업에는
최대 하나의 상위 goal을 사용하고 세부 task는 todo와 ledger로 추적한다. token budget은 사용자가
숫자로 명시했을 때만 설정한다.

- plan의 `Goal`과 active goal objective를 정렬한다.
- 완료 조건에는 사용자가 관찰할 결과를 포함한다. goal 상태와 테스트 개수는 정확성의 증거가 아니며
  실제 동작·consumer 결과와 해당 검증의 한계를 기록한다.
- red-team package에 원래 goal objective를 포함한다.
- 결정론적 검증, 일반 final review와 필수 red-team gate까지 끝난 뒤에만 `complete`로 갱신한다.
- retry cap, 시간 또는 token 부족을 완료로 바꾸지 않는다.
- `blocked`는 현재 goal tool이 요구하는 반복 blocker 조건을 충족할 때만 사용한다.
- goal tool이 없으면 plan과 ledger만 사용하고 goal을 사용했다고 주장하지 않는다.

## 환경 감지

worktree를 만들거나 브랜치를 완료하는 스킬은 진행하기 전에 읽기 전용 git 명령으로 환경을 감지한다.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → 이미 linked worktree에 있음(생성 생략)
- `BRANCH`가 비어 있음 → detached HEAD(sandbox에서 branch/push/PR 불가)

각 스킬이 이 signal을 사용하는 방법은 `using-git-worktrees` 0단계와
`finishing-a-development-branch` 1단계를 참고한다.

## Codex App에서 완료하기

외부에서 관리되는 worktree의 detached HEAD처럼 sandbox가 branch/push 작업을 막으면
`using-engineering-skills`의 Git 권한 게이트를 따른다. 사용자가 현재 commit 범위를 명시적으로
승인한 경우에만 commit한다. 그 외에는 검증된 변경을 commit하지 않은 상태로 두고 `diff`를
보고한 뒤 작업을 계속할 수 있는 App control을 사용자에게 안내한다.

- **"Create branch"** — 브랜치 이름을 정한 뒤 App UI에서 별도로 승인된 commit/push/PR 작업을 지원한다.
- **"Hand off to local"** — 작업을 사용자의 로컬 checkout으로 옮긴다.

에이전트는 변경에 비례한 검증을 실행하고 브랜치 이름, commit message와 PR 설명을 제안할 수
있다. staging, commit, push와 PR 생성에는 계속 각 작업에 해당하는 승인이 필요하다.
