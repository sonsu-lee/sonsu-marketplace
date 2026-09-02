# Gemini CLI 도구 매핑

스킬은 "dispatch a subagent", "create a todo", "read a file" 같은 action으로 지시합니다. Gemini CLI에서는 이를 다음 도구에 대응합니다.

| 스킬이 요청하는 action | Gemini CLI 대응 도구 |
|----------------------|----------------------|
| 파일 읽기 | `read_file` |
| 여러 파일을 한 번에 읽기 | `read_many_files` |
| 새 파일 만들기 | `write_file` |
| 파일 수정하기 | `replace` |
| shell 명령 실행하기 | `run_shell_command` |
| 파일 내용 검색하기 | `grep_search` |
| 이름으로 파일 찾기 | `glob` |
| 파일과 하위 directory 나열하기 | `list_directory` |
| URL 가져오기 | `web_fetch` |
| web 검색하기 | `google_web_search` |
| skill 호출하기 | `activate_skill` |
| subagent dispatch하기(`Subagent (general-purpose):` template) | `agent_name: "generalist"`로 `invoke_agent` 호출(`@generalist` chat syntax로도 호출 가능 — [Subagent 지원](#subagent-support) 참고) |
| 여러 작업을 병렬 dispatch하기 | 같은 response에서 여러 `invoke_agent` 호출 |
| task 추적하기("create a todo", "mark complete") | `write_todos`(statuses: pending, in_progress, completed, cancelled, blocked) |

## 지침 파일

스킬에서 "your instructions file"을 언급하면 Gemini CLI에서는 **`GEMINI.md`**를 뜻합니다. Gemini CLI는 `GEMINI.md`를 계층적으로 불러옵니다. global file은 `~/.gemini/GEMINI.md`에 있으며, project-level file은 workspace directory와 그 상위 directory에 있습니다. 도구가 하위 directory의 파일에 접근하면 해당 directory의 `GEMINI.md`도 불러옵니다.

## 개인 스킬 directory

user-level skill은 **`~/.gemini/skills/`**에 있으며 **`~/.agents/skills/`**는 Codex 및 Copilot CLI와 공유하는 cross-runtime alias입니다. 같은 scope에 두 directory가 모두 있으면 `.agents/skills/`가 우선합니다. 각 스킬은 `name`과 `description` frontmatter가 있는 `SKILL.md`를 포함한 하위 directory입니다.

## subagent 지원

Gemini CLI는 `agent_name`과 `prompt` parameter를 받는 `invoke_agent` 도구로 subagent를 dispatch합니다. 같은 dispatch를 chat-syntax shortcut으로도 사용할 수 있습니다. `@generalist <prompt>`를 입력하면 `agent_name: "generalist"`로 `invoke_agent`를 호출하는 것과 같습니다. built-in agent name에는 `generalist`, `cli_help`, `codebase_investigator` 및 browser 도구를 활성화했을 때 사용할 수 있는 `browser_agent`가 있습니다.

스킬은 `Subagent (general-purpose):`로 dispatch하며 prompt template file(예: `engineering:subagent-driven-development`의 `./implementer-prompt.md`)을 참조하거나 inline prompt를 제공합니다. Gemini CLI에서는 다음과 같이 대응합니다.

| skill dispatch 형식 | Gemini CLI 대응 방식 |
|---------------------|----------------------|
| `*-prompt.md` template(implementer, task-reviewer, code-reviewer 등) 참조 | template을 채운 뒤 `agent_name: "generalist"`와 완성한 prompt로 `invoke_agent`를 호출합니다 |
| `engineering:requesting-code-review`의 `./code-reviewer.md` 참조 | `agent_name: "generalist"`와 완성한 review template으로 `invoke_agent`를 호출합니다 |
| inline prompt(template을 참조하지 않음) | `agent_name: "generalist"`와 inline prompt로 `invoke_agent`를 호출합니다 |

### Prompt 채우기

스킬은 `{WHAT_WAS_IMPLEMENTED}` 또는 `[FULL TEXT of task]` 같은 placeholder가 있는 prompt template을 제공합니다. 완성한 prompt를 `invoke_agent`에 전달하기 전에 모든 placeholder를 채웁니다. prompt template 자체에 agent role, review criteria 및 expected output format이 들어 있으며 subagent는 이를 따릅니다.

### 병렬 dispatch

Gemini CLI는 병렬 subagent dispatch를 지원합니다. 독립적인 subagent 작업을 병렬로 실행하려면 같은 response에서 여러 `invoke_agent`를 호출하거나 한 prompt에서 `@generalist`를 여러 번 호출합니다. dependency가 있는 task는 순차적으로 유지하되, 더 단순한 history를 유지한다는 이유만으로 독립적인 subagent task를 직렬화하지 않습니다.

## 추가 Gemini CLI 도구

다음 도구는 Gemini CLI에만 있습니다.

| 도구 | 용도 |
|------|---------|
| `save_memory` (legacy) | `experimental.memoryV2 = false`일 때 session 간에 fact를 보존합니다 |
| `get_internal_docs` | Gemini CLI의 bundled documentation을 조회합니다 |
| `ask_user` | 사용자에게 구조화된 질문(text / single-select / multi-select)을 제시합니다 |
| `enter_plan_mode` / `exit_plan_mode` | read-only plan mode를 시작하거나 종료합니다 |
| `update_topic` | 현재 conversation의 topic / strategic-intent metadata를 갱신합니다 |
| `complete_task` | Gemini subagent가 완료되었음을 알리고 결과를 parent agent에 반환합니다 |
| `tracker_create_task`, `tracker_update_task`, `tracker_get_task`, `tracker_list_tasks`, `tracker_add_dependency`, `tracker_visualize` | dependency와 visualization을 지원하는 상세 task tracker입니다 |
| `read_mcp_resource`, `list_mcp_resources` | MCP resource에 접근합니다 |
