# Pi 도구 mapping

스킬은 "dispatch a subagent", "create a todo", "read a file" 같은 작업을 표현한다. Pi에서는 이를 아래 도구에 대응한다.

| 스킬이 요청하는 작업 | Pi 대응 도구 |
| --- | --- |
| Subagent 위임(`Subagent (general-purpose):` template) | 사용할 수 있으면 `pi-subagents`의 `subagent`처럼 설치된 subagent 도구를 사용한다. |
| Task 추적("create a todo", "mark complete") | 설치된 todo/task 도구가 있으면 사용하고, 없으면 plan 또는 `TODO.md`에서 task를 추적한다. |

## Subagent 사용

Pi core는 표준 subagent 도구를 제공하지 않는다. 선택적으로 함께 사용하기 좋은 `pi-subagents` package는 single-agent, chain, parallel, async, forked-context, resume/status workflow를 지원하는 `subagent` 도구를 제공한다. subagent 도구를 사용할 수 없다면 `Task` 호출을 지어내지 말고 현재 session에서 순차적으로 실행하거나 선택적인 subagent capability가 설치되지 않았다고 설명한다.

## Task 목록

Pi core는 표준 task-list 도구를 제공하지 않는다. todo/task extension이 설치되어 있으면 문서화된 도구를 사용한다. 그 외에는 Engineering plan 파일, Markdown checklist 또는 저장소 로컬 `TODO.md`로 task를 추적한다. 이전 upstream 문서에서 `TodoWrite`를 언급할 수 있는데, 이는 위의 task 추적 작업으로 취급한다.
