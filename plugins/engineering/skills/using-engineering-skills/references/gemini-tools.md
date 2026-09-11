# Gemini CLI 도구 대응

아래는 작업과 도구의 대응표다. 현재 설치 버전의 도구·입력 스키마를 확인해 제공되는 항목만
사용하고 [공통 실행 계약](agent-execution.md)을 적용한다.

| 작업 | 대응 도구 |
| --- | --- |
| 파일 읽기·여러 파일 읽기 | `read_file`·`read_many_files` |
| 파일 작성·수정 | `write_file`·`replace` |
| 명령 실행 | `run_shell_command` |
| 내용 검색·이름 검색·목록 | `grep_search`·`glob`·`list_directory` |
| URL 읽기·웹 검색 | `web_fetch`·`google_web_search` |
| 스킬 호출 | `activate_skill` |
| 에이전트 위임 | `invoke_agent`의 `agent_name`·`prompt` |
| 진행 추적 | `write_todos`의 `pending`, `in_progress`, `completed`, `cancelled`, `blocked` |

## 지침과 스킬 경로

Gemini CLI의 지침 파일은 `GEMINI.md`다. 전역 `~/.gemini/GEMINI.md`, 작업 공간과 상위 경로,
접근하는 하위 경로의 지침을 계층적으로 확인한다.

개인 스킬 경로는 `~/.gemini/skills/`이며 `~/.agents/skills/`는 여러 실행 환경에서 공유하는
경로다. 같은 범위에서는 `.agents/skills/`가 우선하는 구성을 참고하되 실제 설치·탐색 결과를
확인한다. 각 스킬 하위 폴더는 `name`·`description`이 있는 `SKILL.md`를 포함한다.

## 에이전트 위임

위임이 허용된 경우 현재 제공되는 에이전트를 선택한다. `generalist`, `cli_help`,
`codebase_investigator`, 브라우저 기능의 `browser_agent`는 지원 여부를 확인할 이름이다.
`@generalist <prompt>` 단축 구문이 지원되면 `agent_name: "generalist"` 호출에 대응한다.

`Subagent (general-purpose):` 또는 `*-prompt.md` 템플릿의 빈칸을 채워 실제 프롬프트를 전달한다.
예를 들어 `requesting-code-review/code-reviewer.md`는 공통 리뷰 기준과 고정 패키지·검증
근거를 포함한다. 문맥 격리와 재개는 현재 도구의 실제 동작으로 확인한다.

독립 작업의 병렬 호출이 지원되고 승인 범위에 있으면 함께 실행할 수 있다. 의존 작업과
공유 자원은 순서를 정하며 동시수·쓰기 범위·예산은 공통 실행 계약을 따른다.

## 추가 기능

| 도구 | 용도와 확인할 조건 |
| --- | --- |
| `save_memory` | 기존 방식의 기억 저장. `experimental.memoryV2 = false` 설정과 사용자 권한을 확인한다 |
| `get_internal_docs` | 설치에 포함된 문서 조회 |
| `ask_user` | `text`·`single-select`·`multi-select` 질문 |
| `enter_plan_mode`·`exit_plan_mode` | 읽기 전용 계획 모드 전환 |
| `update_topic` | 대화 주제 메타데이터 갱신 |
| `complete_task` | 위임 작업 완료와 상위 에이전트 결과 반환 |
| `tracker_create_task`·`tracker_update_task`·`tracker_get_task`·`tracker_list_tasks`·`tracker_add_dependency`·`tracker_visualize` | 의존 관계와 표시 기능을 포함한 작업 추적 |
| `read_mcp_resource`·`list_mcp_resources` | MCP 자료 접근 |
