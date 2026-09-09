# Claude Code 도구 참고

Claude Code에서 Engineering workflow를 실행할 때에는 현재 session에 실제로 노출된 built-in tool과
입력 schema를 먼저 확인한다. Codex 전용 `functions.exec`, `spawn_agent`, `followup_task`, goal tool이나
model 이름을 Claude Code에 그대로 적용하지 않는다.

## 파일과 명령 실행

- 파일 탐색에는 현재 제공되는 `Glob`, `Grep`, `Read`를 우선하고, 반복 가능한 parser·test·build는
  `Bash`에서 실행한다. 편집에는 현재 제공되는 `Edit` 또는 `Write`를 사용한다.
- 플러그인 내부 script와 hook은 `${CLAUDE_PLUGIN_ROOT}`를 기준으로 찾는다. repository checkout의
  상대 경로나 plugin cache 밖의 sibling directory가 설치 뒤에도 존재한다고 가정하지 않는다.
- 명령 이름과 권한 요구는 현재 `Tools reference`와 실제 session schema를 따른다. tool 부재를
  비슷한 이름의 호출로 추측하지 않는다.

## 질문과 작업 격리

- 사용자 결정이 반드시 필요한 경우 현재 제공되는 `AskUserQuestion`을 사용할 수 있다. 일상적인
  구현 세부사항은 승인된 범위 안에서 합리적으로 결정한다.
- 격리된 workspace가 필요하면 현재 session에 native worktree 기능이 있는지 먼저 확인한다.
  지원되면 이를 사용하고, 없을 때만 `using-git-worktrees`의 Git fallback을 따른다.
- Claude Code의 plugin skill은 `/plugin-name:skill-name`으로 명시적으로 호출할 수 있다. 자연어
  요청에서는 설치된 skill의 description에 따라 `Skill` tool이 선택한다.

## Subagent와 review

사용자 또는 적용되는 프로젝트·스킬 지침이 위임을 허용할 때에만 현재 제공되는 `Agent` tool을
사용한다. Claude Code subagent는 별도 context에서 시작하며 subagent가 다시 subagent를 만들 수
있다고 가정하지 않는다.

- fresh implementer나 reviewer에는 승인된 목표, 고정한 artifact, 검증 결과와 열린 finding만
  전달한다. 이전 reviewer의 결론, 칭찬과 전체 대화는 전달하지 않는다.
- 현재 `Agent` schema가 resume을 제공하지 않으면 기존 agent 재개를 흉내 내지 않는다. 새 context가
  필요한 회차로 처리하고 같은 task·gate의 누적 attempt를 유지한다.
- agent definition이나 tool schema가 `model`을 허용하면 현재 Claude Code가 지원하는 값만 사용한다.
  사용자가 모델을 지정하지 않았고 역할상 override가 필요하지 않으면 `inherit` 또는 host default를
  유지한다. Codex용 역할 표의 모델명을 변환해 사용하지 않는다.
- 독립 review capability가 없거나 위임이 허용되지 않으면 self-review를 독립 review로 바꾸어 말하지
  않는다. 필수 gate는 `blocked` 또는 `not_run`으로 기록한다.

## 상태와 완료

Claude Code에 Codex goal lifecycle과 같은 도구가 있다고 가정하지 않는다. 현재 task 기능이 실제로
노출되고 사용자가 요청한 경우에만 사용한다. 완료 주장은 어느 host에서든 fresh test, build,
validator, loader와 현재 diff 근거가 먼저이며, hook·plugin 설치처럼 host가 소비하는 계약은 가능한
경우 `claude plugin validate --strict`와 격리된 설치로 확인한다.

공식 참고: [Tools reference](https://code.claude.com/docs/en/tools-reference),
[Subagents](https://code.claude.com/docs/en/sub-agents),
[Plugins reference](https://code.claude.com/docs/en/plugins-reference).
