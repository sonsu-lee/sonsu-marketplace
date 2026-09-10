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

티켓은 작업을 전달하고 추적하는 문서로 작성합니다. [양식 선택 기준](skills/to-ticket/references/ticket-selection.md)에 따라 일반 작업·버그·조사 작업 중 하나를 고르며, 사용자나 팀의 지정 양식이 있으면 우선합니다. 항목과 작성 안내는 각 템플릿을 따르고, 이미지·영상 게시는 프로바이더별 첨부 규칙으로 처리합니다.

PR은 [PR 템플릿 규칙](skills/to-pr/references/pr-template.md)에 따라 작성합니다. 메인 스킬은 작성·게시 흐름을, 참고 문서는 양식·작성 품질·프로바이더 작업·미디어 처리를 나눠 담당합니다.

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
