# Antigravity CLI (`agy`) 도구 대응

현재 도구와 입력 스키마를 확인해 다음 대응을 적용한다. 위임·환경·예산은
[공통 실행 계약](agent-execution.md)을 따른다.

| 작업 | 대응 기능 |
| --- | --- |
| 에이전트 위임 | `invoke_subagent`의 기본 `TypeName`. `self`는 전체 기능, `research`는 읽기 전용 작업에 대응한다 |
| 진행 추적 | `write_to_file`로 작업 산출물을 만들고 제공되는 편집 도구로 갱신한다 |

## 진행 추적

`manage_task`는 백그라운드 프로세스의 `list`·`kill`·`status`·`send_input`을 관리하는 기능이다.
작업 체크리스트는 지원되는 경우 `write_to_file`의 `IsArtifact: true`와
`ArtifactMetadata.ArtifactType: "task"`로 저장한다. 실제 필드 배치는 현재 스키마를 따른다.

여러 단계의 진행 기록이 필요하면 기존 계획을 체크리스트로 사용하고 `replace_file_content`
또는 `multi_replace_file_content`로 완료 항목과 계획 변경을 반영한다. 재개할 때 현재 파일·
근거와 대조한다. 별도 파일을 만들 권한이 없으면 허용된 대화 기록을 사용한다.
