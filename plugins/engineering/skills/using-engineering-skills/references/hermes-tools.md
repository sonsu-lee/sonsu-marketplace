# Hermes Agent 도구 대응

현재 도구와 입력 스키마에서 지원하는 항목을 확인하고 [공통 실행 계약](agent-execution.md)을
적용한다.

| 작업 | 대응 도구 |
| --- | --- |
| 파일 읽기·작성·국소 수정 | `read_file`·`write_file`·`patch` |
| 명령 실행 | `terminal` |
| 파일 내용 검색 | `search_files` |
| 파일 이름 검색 | `terminal`의 설치된 검색 명령 |
| 웹페이지 읽기·검색 | `web_extract(urls=[...])`·`web_search(query=...)` |
| 에이전트 위임 | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| 진행 추적 | `todo` |
| 스킬 호출 | `skill_view("skill-name")` |

## 지침과 스킬

프로젝트 지침은 `AGENTS.md`, 전역 지침은 `~/.hermes/SOUL.md`를 확인한다. 스킬 목록과 읽기는
지원되는 `skills_list`·`skill_view`에 대응한다.

```text
skill_view("brainstorming")
skill_view("test-driven-development")
```

스킬 등록 전이라 목록에서 찾을 수 없으면 실제 설치 경로를 확인해 `SKILL.md`를 직접 읽는다.
다음은 설치 경로의 예시다.

```text
read_file(path="~/.hermes/plugins/engineering/skills/<skill-name>/SKILL.md")
```

## 위임과 추적

위임이 허용되고 `delegate_task`가 제공되면 역할·문맥·도구 범위를 지정한다. 선택 위임 기능이
없으면 직접 수행할 수 있지만, 필수 독립 리뷰의 부재는 `blocked` 또는 `not_run`으로 구분한다.

세션 안의 추적은 `todo`, 여러 에이전트의 작업 보드는 사용 가능한 `hermes kanban`에 대응한다.
원 문서의 `TodoWrite` 표현은 현재 지원되는 진행 추적 작업으로 해석한다.
