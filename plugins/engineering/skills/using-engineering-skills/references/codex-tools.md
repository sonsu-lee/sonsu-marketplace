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
  전체 history fork에는 `model`, `reasoning_effort` override를 사용할 수 있다(여기서는
  `agent_type`만 거부된다). 격리 fork가 SDD의 기본값인 이유는 context 관리 때문이지
  override에 필요하기 때문이 아니다.
- **수정 회차:** `followup_task`로 implementer를 재개한다. 이 도구는 메시지를 전달하고
  turn을 시작하며 harness가 내보낸 child를 투명하게 다시 불러온다. 생성된 에이전트에게 다시
  메시지를 보낼 수 없다는 생각으로 새 implementer를 위임하지 않는다. V2에서는 항상 가능하다.
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

자신이 fan-out을 실행하는 child인 경우를 포함해 모든 `spawn_agent` 호출에는 실행 중인 스킬의
Model Selection 규칙에 따라 `model`과 `reasoning_effort`를 모두 명시한다. `model`만 설정하면
child의 effort가 자신의 값이 아니라 해당 모델의 기본값으로 조용히 재설정된다.

누락된 spawn이 session에서 가장 비싼 모델을 조용히 상속하지 않고 의도한 tier로 routing되도록
사용자에게 `~/.codex/config.toml`에 machine-level backstop을 추가해 달라고 요청한다.

```toml
[agents]
default_subagent_model = "<a mid-tier model from your spawn allowlist>"
default_subagent_reasoning_effort = "medium"
```

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
