# 호스트별 도구

같은 절차를 omp, Claude Code, Codex에서 실행할 때 쓰는 도구다.

| 작업 | omp | Claude Code | Codex |
| --- | --- | --- | --- |
| PR·이슈 읽기 | `pr://<n>`, `pr://<n>/diff`, `issue://<n>` | `gh` | `gh` |
| 구조화된 GitHub 쓰기 | GitHub MCP(`pull_request_review_write`, `add_comment_to_pending_review`, `add_reply_to_pull_request_comment`, `issue_write`) | 연결된 GitHub MCP, 없으면 `gh` | `gh` |
| 화면 캡처 | `browser` 탭 스크린샷 | 연결된 브라우저 도구 또는 사용자 제공 파일 | 같음 |
| 게시 전 확인 | `ask` | 대화로 확인 | 대화로 확인 |
| 하위 리뷰어 | `task`의 순정 `reviewer`(역할 agent는 사용자가 직접 등록한 경우만) | Task 도구의 `review:<role>` | 현재 Codex의 하위 에이전트 기능 |
| 순정 리뷰 명령 | `/review`·`/annotate code-review`도 순정 `reviewer`를 쓰며, `sonsu-review-standard` 규칙이 함께 적용된다 | 해당 없음 | 해당 없음 |

- omp에서는 스킬을 `/skill:<name>`으로 호출하며 플러그인 접두사를 붙이지 않는다.
- 정본 절차의 명령은 `git`, `gh`, `ffmpeg`, `ffprobe`만 쓴다.
- omp advisor는 메인 에이전트의 작업을 감시하는 별도 기능이다. 이 플러그인은 advisor 설정을 바꾸지 않는다.
