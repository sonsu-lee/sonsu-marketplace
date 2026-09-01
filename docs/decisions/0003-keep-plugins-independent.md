# 0003 Keep Superpowers and Workflow Independent

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None

## Context

Superpowers는 구현 계획, 검증과 개발 branch 완료 방법을 다루고, Workflow는 Git 변경,
ticket과 GitHub PR 산출물을 다룹니다. `finishing-a-development-branch`의 push·PR 선택지는
Workflow의 `git-workflow`와 `to-pr` 일부와 겹칩니다. 두 플러그인 중 하나만 설치하는 경우도
지원해야 하므로 한쪽이 다른 쪽의 존재를 필수로 가정할 수 없습니다.

조사한 주요 plugin·skill 저장소에서는 독립적인 전문 스킬을 description으로 라우팅하고,
강한 스킬 간 호출은 주로 같은 플러그인 내부에서 사용했습니다. 공통 orchestrator가 있는
경우에도 전문 스킬은 직접 사용할 수 있도록 유지하거나 필요한 구성요소를 같은 플러그인에
포함했습니다.

근거가 된 현재 구조는 다음 원문에서 확인했습니다.

- [OpenAI plugin manifest 명세](https://github.com/openai/plugins/blob/1e285826e604f66f7208f7ac4dba0fe8341d1f57/.agents/skills/plugin-creator/references/plugin-json-spec.md)
- [Anthropic Claude Code plugin marketplace](https://github.com/anthropics/claude-code/blob/f275fa282e76c5e5456912268f2c367a7f4f4797/.claude-plugin/marketplace.json)
- [Superpowers executing-plans 내부 조합](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/executing-plans/SKILL.md)
- [Matt Pocock ask-matt router](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/ask-matt/SKILL.md)
- [Wshobson git-pr-workflows의 cross-plugin dependency 정책](https://github.com/wshobson/agents/blob/554237f7515b7012ce22e753c5c2e5b65369e3a4/plugins/git-pr-workflows/commands/git-workflow.md)

## Decision

Superpowers와 Workflow를 독립 플러그인으로 유지합니다. 두 매니페스트 사이에 dependency를
만들거나 한 플러그인의 스킬에서 다른 플러그인의 skill ID를 필수로 호출하지 않습니다.

직접적인 branch·commit·push 요청은 `workflow:git-workflow`, ticket 산출물은
`workflow:to-ticket`, 현재 branch의 새 GitHub PR 산출물은 `workflow:to-pr`이 담당합니다.
구현, 디버깅, 계획 실행과 완료된 개발 branch의 통합 결정은 Superpowers가 담당합니다.
한 요청이 두 책임을 포함하면 Codex가 현재 설치된 스킬을 실행 순서에 맞게 선택합니다.

공통 router는 만들지 않습니다. description 조정과 repository-level 경쟁 트리거 사례로
경계를 검증하고, 반복되는 실제 오동작이 확인될 때 router 또는 다른 통합 계층을 재검토합니다.

## Alternatives Considered

- Superpowers가 Workflow를 직접 호출: 실행 순서는 명확하지만 Workflow가 없는 환경에서
  Superpowers의 독립성이 깨지고 현재 매니페스트에서 의존성을 강제할 계약도 없습니다.
- Workflow에 Superpowers를 포함: 사용은 단순해지지만 업스트림 방법론과 개인 delivery
  정책의 업데이트 경계가 섞입니다.
- 별도 orchestrator 플러그인 추가: 두 플러그인을 건드리지 않고 조합할 수 있지만 현재
  확인된 충돌에 비해 설치와 라우팅 구조가 복잡해집니다.
- 겹치는 기능을 한쪽에서 제거: 책임은 선명하지만 한 플러그인만 설치한 환경의 기능이 줄어듭니다.

## Consequences

각 플러그인은 단독으로 설치하고 업데이트할 수 있습니다. 둘을 함께 설치하면 직접 산출물
요청과 개발 lifecycle 요청을 description으로 구분해야 하며, 구현부터 PR까지 이어지는 요청은
두 플러그인이 순서대로 선택될 수 있습니다. `finishing-a-development-branch`와 PR 관련 스킬의
경계는 평가 사례와 실제 사용 결과를 통해 계속 확인해야 합니다.

## Revisit When

동일한 요청에서 두 스킬이 반복적으로 경쟁하거나 잘못된 스킬이 선택되는 실제 결과가 누적될
때, Codex가 공식적인 plugin dependency·router 계약을 제공할 때, 또는 여러 delivery plugin을
하나의 고정 흐름으로 조합해야 할 때 재검토합니다.
