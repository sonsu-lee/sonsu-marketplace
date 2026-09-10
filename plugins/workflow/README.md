# Workflow

Git·티켓·PR 작업을 위한 독립 Codex·Claude Code 플러그인입니다.

```sh
# Codex
codex plugin add workflow@sonsu-marketplace

# Claude Code
claude plugin install workflow@sonsu-marketplace
```

## 제공하는 작업

- `git-workflow`: 브랜치·commit·push와 Git 변경 검토
- `to-ticket`: 티켓 초안·게시와 기존 제목·본문 수정
- `ticket-lifecycle`: 기존 티켓의 상태·담당자·관계 변경
- `to-pr`: 새 PR 초안·게시와 티켓·시각 자료 연결

티켓은 [공통 양식](skills/to-ticket/assets/templates/default.md)을 사용합니다. `문제`를 필수로 작성하고, 필요한 경우 `재현 정보`와 `고려 사항`, 선택 항목인 `관련 자료`를 덧붙입니다. 재현 정보에는 순서와 동영상·이미지를 함께 담으며, 업로드는 프로바이더별 규칙을 따릅니다. 사용자나 팀의 지정 양식이 있으면 우선합니다.

설명과 보고는 사용할 수 있는 출력 언어의 Fluent Languages 스킬에 맞춰 간결하게 작성합니다. 한국어는 `fluent-languages:fluent-korean`을 사용하며, 정해진 조건·명령·식별자와 권한 범위를 보존합니다.

## 컴팩션 후 작업 재개

[`workflow:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 스킬을
직접 호출해 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
