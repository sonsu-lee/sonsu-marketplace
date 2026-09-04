## Subagent 위임에는 multi-agent 지원이 필요하다

Codex 설정(`~/.codex/config.toml`)에 다음을 추가한다.

```toml
[features]
multi_agent = true
```

이 설정은 `dispatching-parallel-agents`, `subagent-driven-development` 같은
스킬이 사용하는 multi-agent 도구를 활성화한다. 제공되는 도구는 모델 preset이 선택한
multi-agent 버전에 따라 달라진다(현재 preset은 V2, 이전 preset은 V1을 사용한다). 이 표를
포함한 문서와 실제 도구 목록이 다르면 실제 목록을 신뢰한다.

- **생성:** `spawn_agent {fork_turns: "none"}`으로 child에게 깨끗한 context를 제공한다.
  기본값 `"all"`은 전체 transcript를 child에 복사한다. Codex 0.145 이상에서는
  `~/.codex/agents/` 아래의 role 파일을 `agent_type`으로 격리 fork에 연결한다.
  현재 tool schema가 허용하는 `fork_turns`와 model override 조합을 신뢰한다. 격리 reviewer는
  `fork_turns: "none"`을 사용하고 필요한 artifact만 prompt에 넣는다.
- **수정 회차:** round 1만 `followup_task`로 원래 implementer를 재개할 수 있다. round 2와 3은
  항상 `spawn_agent {fork_turns: "none"}`으로 서로 다른 fresh implementer를 만든다. controller는
  `fix-handoff create`가 출력한 immutable bundle path와 SHA-256만 전달한다. fresh implementer는 bundle을
  읽거나 추출하거나 수정하기 전에 canonical `fix-handoff verify BUNDLE DIGEST`를 실행하고, 성공 뒤에는
  stdout의 `Extracted:` directory만 읽는다. bundle path를 다시 열거나 직접 tar extract하지 않는다. 검증 실패는
  missing/unreadable이면 `blocked`, malformed/schema/digest mismatch이면 `inconclusive`으로 handoff
  preparation에 반환하며 이전 agent·report·session history를 재사용하지 않는다. Fast Path classifier는
  이 일반 수정 규칙의 예외가 아니며 기존 독립 탐색·재진입 금지 규칙을 그대로 따른다.
- **Lifecycle:** V2에는 `close_agent`가 없다. slot이 필요하면 완료된 child는 자동으로
  제거되므로 닫지 않아도 비용이 들지 않는다. V1 session에만 `close_agent`가 있다. V1에서는
  reviewer가 결과를 반환하면 닫고, implementer는 해당 task 리뷰가 통과한 뒤 닫는다.
- **모델 이름:** 현재 spawn allowlist와 대조하지 않고 스킬, 표 또는 이전 session의 모델 이름을
  `spawn_agent`에 복사하지 않는다. V2는 V2를 지원하는 preset만 허용하고 나머지는 오류로 거부한다.

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

자신이 fan-out을 실행하는 child인 경우를 포함해 `spawn_agent`의 실제 schema가 두 override를
모두 지원하면 실행 중인 스킬의 Model Selection 규칙에 따라 `model`과 `reasoning_effort`를 함께
명시한다. 한쪽만 설정하면 의도하지 않은 기본값을 쓰거나 schema validation에 실패할 수 있으므로
부분 override는 하지 않는다.

실제 schema가 두 field 중 하나라도 지원하지 않으면 존재하지 않는 field를 보내지 않는다. 노출된
`agent_type`, role 또는 preset이 있으면 같은 역할의 가장 가까운 조합을 사용하고, 그렇지 않으면
아래 machine-level default를 사용하되 `routing_fallback: tool-schema-no-explicit-overrides`를
기록한다. 필요한 capability를 어떤 지원 경로로도 제공할 수 없을 때에만 해당 reviewer를
`blocked`로 판정한다. tool metadata의 부재를 무시하고 잘못된 호출을 반복하지 않는다.

누락된 spawn이 session에서 가장 비싼 모델을 조용히 상속하지 않고 의도한 tier로 routing되도록
사용자에게 `~/.codex/config.toml`에 machine-level backstop을 추가해 달라고 요청한다.

```toml
[agents]
default_subagent_model = "<a mid-tier model from your spawn allowlist>"
default_subagent_reasoning_effort = "medium"
```

현재 allowlist가 다음 조합을 지원하면 역할별 기본값으로 사용한다. 실제 tool metadata가 다르면
같은 역할을 처리할 수 있는 가장 가까운 허용 조합을 선택하고 fallback을 기록한다.

| 역할 | Model | Reasoning effort |
| --- | --- | --- |
| 정확한 문자열·metadata·경로 변경 | `gpt-5.6-luna` | `low` |
| 명확한 1~2개 파일 구현 | `gpt-5.6-luna` | `medium` |
| Fast Path classifier (유일한 Fast Path subagent slot) | `gpt-5.6-luna` | `low` |
| Mechanical Fast Path와 Code Mode orchestration | controller 직접 실행 | 해당 없음 |
| 여러 파일 통합·일반 debugging | `gpt-5.6-terra` | `high` |
| 일반 task review | `gpt-5.6-terra` | `medium` 또는 `high` |
| 범위가 제한된 기계적 re-review | `gpt-5.6-luna` | `medium` |
| architecture와 구현 plan | `gpt-5.6-sol` | `high` |
| 일반 final whole-change review | `gpt-5.6-sol` | `high` |
| fresh-context red-team whole-structure review | `gpt-5.6-sol` | `xhigh` |

`max`와 `ultra`는 기본값으로 사용하지 않는다. Fast Path에서는 independent classifier만 한 슬롯으로
만들 수 있으며 implementation 또는 reviewer subagent는 Fast Path 기본 경로에서 만들지 않는다.
classifier는 fresh `gpt-5.6-luna` / `low`로 request, target, controller evidence, proposed oracle,
unknowns만 받고 독립 targeted search를 정확히 한 번 실행한다. model 상향은 변경 없는 입력을 다시
시도할 근거가 아니다.

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
