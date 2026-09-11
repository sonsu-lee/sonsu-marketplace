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

티켓은 [양식 선택 기준](skills/to-ticket/references/ticket-selection.md)으로 사용자·팀 양식과 필수 필드를 확인하고, 번들 [티켓 작성 지침](skills/to-ticket/references/ticket-writing.md)으로 내용을 구성합니다. 기본 양식은 일반 작업·버그·조사 작업이며, 이미지·영상 게시는 프로바이더별 첨부 규칙으로 처리합니다.

PR은 [PR 템플릿 규칙](skills/to-pr/references/pr-template.md)으로 적용 양식을 확인하고, 번들 [PR 작성 지침](skills/to-pr/references/pr-writing.md)으로 실제 변경을 설명합니다. Workflow는 diff·티켓·검증 근거 수집, 원격 양식 확인, 연결 문법과 게시·첨부·상태 결과 검증을 담당합니다. 임시로 작성한 본문은 적용 양식이나 게시 조건이 확정됐다는 뜻이 아닙니다.

티켓·PR의 작성 기준과 기본 양식은 Writing의 원본에서 생성한 사본을 이 플러그인에 포함합니다. Writing을 설치하지 않아도 번들 지침으로 작성할 수 있습니다. `writing:writing`이 있으면 문서·설명·보고에 함께 적용하되, 정해진 조건·명령·식별자와 권한 범위를 보존하고 자동 설치하지 않습니다. 생성된 지침과 양식은 직접 고치지 않고 Writing 원본과 저장소 생성기로 갱신합니다.

## 컴팩션 후 작업 재개

[`workflow:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 스킬을
직접 호출해 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

Writing에서 자동으로 포함한 티켓·PR 작성 지침과 양식에는
[Writing의 MIT 고지](WRITING_LICENSE.md)를 함께 제공합니다. Workflow의 나머지 파일에
새 라이선스를 부여하는 변경은 아닙니다.
