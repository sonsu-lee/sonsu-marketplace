---
name: using-engineering-skills
description: 대화를 시작할 때 응답하거나 행동하기 전에 Engineering 플러그인이 제공하는 스킬 중 어떤 스킬을 적용해야 하는지 판단하기 위해 사용한다
---

# using-engineering-skills: Engineering 스킬 사용하기

<SUBAGENT-STOP>
특정 task를 실행하도록 subagent로 위임받았다면 이 스킬을 무시한다.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
현재 작업에 Engineering 스킬이 적용될 가능성이 1%라도 있다고 생각한다면 해당 Engineering 스킬을 반드시 호출해야 한다.

ENGINEERING 스킬이 현재 TASK에 적용된다면 선택의 여지가 없다. 반드시 사용한다.

이 규칙은 협상의 대상이 아니다. 합리화하여 회피할 수 없다.

이 필수 규칙은 Engineering이 제공하는 스킬에만 적용된다. 다른 플러그인의 스킬은 사용자가 요청했거나, 저장소 지침에서 요구하거나, 현재 task의 구체적인 필요 때문에 실질적으로 유용할 때만 사용한다. 주제가 관련 있다는 이유만으로 사용 가능한 모든 외부 스킬을 호출하지 않는다.
</EXTREMELY-IMPORTANT>

<GIT-AUTHORIZATION-GATE>
어떤 plan, skill, 참고 파일, 실행 mode, worktree 상태 또는 플랫폼 제한도 Git 권한을 부여하지 않는다. 요청된 변경의 staging은 명시적으로 승인된 commit의 일부이거나 staging 자체가 요청된 경우에만 수행한다. 현재 작업에 대해 사용자가 명시적으로 승인한 경우에만 commit한다. push, PR 생성, merge, 배포와 파괴적인 Git 작업에는 각각 해당 작업에 대한 승인이 필요하다.

이 게이트는 `using-git-worktrees`의 ignore 파일 commit 단계와 플랫폼별 완료 지침을 포함하여 자동으로 commit하라고 하는 하위 지침보다 우선한다. commit 권한이 없으면 가능한 경우 commit하지 않은 상태로 workspace를 안전하게 만들고, `diff`를 보고한 뒤 commit 결정을 요청한다.
</GIT-AUTHORIZATION-GATE>

## 규칙

명확화 질문, codebase 탐색 또는 파일 확인을 포함한 **모든 응답이나 행동보다 먼저 적용 가능한 Engineering 스킬과 위 정책에 따라 선택한 외부 스킬을 호출한다.** 선택한 스킬이 상황에 맞지 않는 것으로 드러나면 계속 사용할 필요는 없다.

**plan mode로 들어가기 전:** 아직 brainstorming하지 않았다면 먼저 brainstorming 스킬을 호출한다.

그런 다음 "[skill]을 사용해 [purpose]를 진행합니다"라고 알리고 스킬을 정확히 따른다. checklist가 있으면 항목마다 todo를 만든다.

## 스킬 우선순위

여러 Engineering 스킬이 적용될 때에는 process 스킬이 먼저다. process 스킬이 접근 방식을 정하면 implementation 스킬(`frontend-design` 등)이 이를 실행한다. `brainstorming`과 `systematic-debugging`은 Engineering에서 가장 자주 쓰이는 process 스킬이지만, 이 규칙은 task에 선택한 모든 Engineering 스킬에 적용된다.

- "Let's build X" → 먼저 `engineering:brainstorming`, 그다음 implementation 스킬.
- "Fix this bug" → 먼저 `engineering:systematic-debugging`, 그다음 domain 스킬.

## 위험 신호

다음 생각이 들면 멈춘다. 지금 합리화하고 있는 것이다.

| 생각 | 실제 |
|---------|---------|
| "This is just a simple question" | 질문도 task다. 적용 가능한 Engineering 스킬을 확인한다. |
| "I need more context first" | Engineering 스킬 확인은 명확화 질문보다 먼저다. |
| "Let me explore the codebase first" | Engineering 스킬이 탐색 방법을 정할 수 있다. 먼저 확인한다. |
| "I can check git/files quickly" | 파일에는 대화 맥락이 없다. 적용 가능한 Engineering 스킬을 먼저 확인한다. |
| "Let me gather information first" | 적용 가능한 Engineering 스킬이 정보 수집 방법을 정할 수 있다. |
| "This doesn't need a formal skill" | Engineering 스킬이 적용되면 사용한다. |
| "I remember this skill" | Engineering 스킬은 변한다. 현재 버전을 읽는다. |
| "This doesn't count as a task" | 행동은 task다. 적용 가능한 Engineering 스킬을 먼저 확인한다. |
| "The skill is overkill" | Engineering 스킬이 적용되면 그 스킬을 따르고, 허용하는 범위에서 절차의 무게를 조절한다. |
| "I'll just do this one thing first" | 어떤 작업이든 시작하기 전에 적용 가능한 Engineering 스킬을 확인한다. |
| "This feels productive" | 규율 없는 행동은 시간을 낭비한다. 적용 가능한 Engineering 스킬이 이를 막는다. |
| "I know what that means" | 개념을 아는 것과 적용 가능한 Engineering 스킬을 사용하는 것은 다르다. 스킬을 호출한다. |

## 플랫폼별 조정

사용 중인 harness가 아래에 있으면 해당 참고 파일에서 특별 지침을 읽는다.

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`
- Hermes Agent: `references/hermes-tools.md`

## 품질 게이트

Engineering lifecycle 스킬은 단계별 소유 품질 게이트를 사용한다. 선택한 스킬이 게이트를
선언하면 진행, 재시도, 이전 단계로 복귀 또는 중단을 결정하기 전에 공통
[품질 게이트 계약](references/quality-gates.md)을 읽고 적용한다. 이 계약은 중앙 router를
추가하지 않으며 위의 Git 또는 외부 작업 권한 경계를 바꾸지 않는다.

## 사용자 지침

사용자 지침(`CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 등의 파일과 직접 요청)은 스킬보다 우선하고, 스킬은 다시 기본 동작보다 우선한다. 사용자가 명시적으로 지시한 경우에만 스킬 workflow 또는 지침을 생략한다.
