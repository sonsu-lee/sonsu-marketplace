# Hermes Agent 도구 매핑

스킬은 "dispatch a subagent", "create a todo", "read a file" 같은 action으로 지시합니다. Hermes Agent에서는 이를 다음 도구에 대응합니다.

## 도구

| 스킬이 요청하는 action | Hermes 도구 |
|---|---|
| 파일 읽기 | `read_file` |
| 새 파일 만들기 | `write_file` |
| 파일 수정하기(targeted patch) | `patch` |
| shell 명령 실행하기 | `terminal` |
| 파일 내용 검색하기 | `search_files` |
| 이름으로 파일 찾기 | `find`를 사용하는 `terminal` |
| URL 가져오기 / webpage 읽기 | `web_extract(urls=[...])` |
| web 검색하기 | `web_search(query=...)` |
| subagent dispatch하기 | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| task 추적하기 | `todo` 도구 |
| skill 호출하기 | `skill_view("skill-name")` |

## 지침 파일

스킬에서 "your instructions file"을 언급하면 Hermes Agent에서는 project directory의 **`AGENTS.md`** 또는 global file인 `~/.hermes/SOUL.md`의 **`SOUL.md`**를 뜻합니다.

## 스킬 호출하기

Hermes Agent에는 `skill_view`와 `skills_list` 도구로 구성된 `skills` toolset이 있습니다.
Engineering 스킬은 다음과 같이 호출합니다.

```
skill_view("brainstorming")
skill_view("test-driven-development")
```

`skill_view`가 Engineering 스킬을 찾지 못하면(plugin이 완전히 등록되기 전에는 catalog에
표시되지 않을 수 있습니다) SKILL.md를 직접 읽는 방법을 사용합니다.

```
read_file(path="~/.hermes/plugins/engineering/skills/<skill-name>/SKILL.md")
```

이 fallback은 native skill loading이 없는 다른 harness에서 사용하는 방식과 같습니다.

## Subagent dispatch 방식

병렬 또는 순차 workstream을 위한 격리된 subagent를 만들 때는 `delegate_task`를 사용합니다.

```
delegate_task(goal="...", context="...", toolsets=[...], role="leaf")
```

`delegate_task`를 사용할 수 없다면 존재하지 않는 tool call을 만들어 내지 말고 작업을 직접 수행합니다.

## Task 추적

session 안의 task 추적에는 `todo` 도구를 사용합니다. multi-agent task board에는 사용할 수 있는 경우 `hermes kanban` CLI를 사용합니다. 이전 `TodoWrite` 참조는 task-tracking action으로 해석합니다.
