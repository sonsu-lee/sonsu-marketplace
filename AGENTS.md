# Repository guidance

## 작성 언어

- 문서, 스킬, 참고 자료와 생성기 문구는 한국어로 쓴다. 일본어로 쓰지 않는다.
- 예외는 언어 자체가 대상인 내용이다.
  - Fluent English·Japanese 플러그인과 그 평가 자료는 해당 언어로 쓴다.
  - 다른 언어 사용자의 요청을 재현하는 평가 프롬프트와 예시 문장은 그 언어 그대로 둔다.
  - 履歴書·職務経歴書처럼 형식 이름이 그 언어인 용어, 원문 인용, 출처 제목은 원문을 유지한다.
  - `README.en.md`, `README.ja.md`는 `README.md`의 번역본으로 유지한다.
- 코드 식별자, 파일 경로, 명령, 로그는 원문 그대로 둔다.

## Git and Tracker Language

- Write commit messages, pull request titles and bodies, and GitHub issues in English.

## Code Review Rules

- Write the review summary and every inline review comment in Korean. Keep code identifiers,
  file paths, commands, log output, and quoted source text in their original form.

## Subagent Delegation

- For nontrivial work, the root agent identifies independently useful investigation,
  implementation, and review tasks. Assign eligible tasks to subagents in parallel when
  their results can be verified separately and the benefit exceeds coordination cost.
- Give each subagent a bounded goal, inputs, output, and read/write scope. Parallel writers
  use separate worktrees; the root agent integrates their results and verifies the final state.
- For recurring Engineering roles, select the matching project Codex agent in `.codex/agents/`
  only when that role is discoverable and selectable in the current project/session. Host support
  for named selection alone is insufficient because project configuration may not be loaded.
  Read `shared/agent-policy/profiles.json` and pass the role's model and reasoning effort at spawn
  unless the user specifies otherwise. Claude Code uses the matching packaged `engineering:<role>`
  agent. In both hosts, provide the concrete task brief at spawn time; a role name does not
  determine task count or file ownership. If the Codex role is unavailable or selection fails,
  read its definition and pass the role boundaries in the brief; report native role selection as
  unverified.
  A brief-only fallback does not apply the agent file's `sandbox_mode`; report the actual permission
  mode separately from the read-only instruction.
- Keep dependent work and shared writes sequential. When a task appears divisible but is
  handled directly, briefly state the concrete dependency or cost that prevented delegation.
- The root agent owns further assignments. A subagent returns requests for more workers to
  the root agent instead of delegating on its own.
