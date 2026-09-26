# Workflow

Git·티켓·PR 작업을 위한 독립 Codex·Claude Code 플러그인입니다.

```sh
codex plugin add workflow@sonsu-marketplace
```

## 제공하는 작업

- `inspect-prs`: 열린 PR 또는 지정 PR의 CI·리뷰·병합 상태 조회
- `repair-pr`: 요청한 PR의 충돌·리뷰 의견·CI 실패 복구
- `branch`: 브랜치 이름 제안·검토와 요청한 브랜치 생성
- `commit`: 메시지 준비, 범위를 확인한 staging과 새 commit
- `push`: 확인한 remote ref로 일반 push
- `review-commit`: commit 후보·기존 commit의 읽기 전용 검토
- `to-ticket`: 티켓 초안·게시와 기존 제목·본문 수정
- `ticket-lifecycle`: 기존 티켓의 상태·담당자·관계 변경
- `to-pr`: 새 PR 초안·게시와 티켓·시각 자료 연결

티켓은 [양식 선택 기준](skills/to-ticket/references/ticket-selection.md)으로 사용자·팀 양식과 필수 필드를 확인하고, [티켓 작성 지침](skills/to-ticket/references/ticket-writing.md)으로 내용을 구성합니다. 기본 양식은 일반 작업·버그·조사 작업이며, 이미지·영상 게시는 프로바이더별 첨부 규칙으로 처리합니다.

PR은 [주제·의존 관계 기준](skills/to-pr/references/stacked-prs.md)으로 단일 PR, 독립 PR 또는 GitHub native stacked PR의 경계를 정합니다. [PR 템플릿 규칙](skills/to-pr/references/pr-template.md)으로 적용 양식을 확인하고, [PR 작성 지침](skills/to-pr/references/pr-writing.md)으로 각 PR의 실제 변경을 설명합니다. Workflow는 diff·티켓·검증 근거 수집, 원격 양식 확인, 연결 문법과 게시·첨부·상태 결과 검증을 담당합니다. 임시로 작성한 본문은 적용 양식이나 게시 조건이 확정됐다는 뜻이 아닙니다.

티켓·PR의 작성 기준과 기본 양식은 이 플러그인에서 직접 관리합니다. Writing은 정보 선별·문서 배치와 문장·문단
구성을, Fluent Languages는 한국어·일본어·영어 표현을 맡습니다. 현재 제공되는 스킬만
[결합 기준](references/writing-composition.md)에 따라 한 초안에 적용하고, 없는 플러그인도 자동 설치하지 않습니다.
Workflow만, Writing과 함께, Fluent와 함께 또는 세 플러그인을 함께 사용할 수 있습니다.
플러그인 사이에 지침이나 양식을 복사하는 생성 단계는 없습니다.

Git 스킬 네 개는 [공통 안전 규칙](references/git-safety.md)을 필요한 경우에 읽고 각각
독립적으로 끝납니다. branch·commit·push가 모두 요청됐으면 실제 결과를 확인하며 순서대로
수행하되, commit 요청만으로 push하지 않습니다.

## 컴팩션 후 작업 재개

[작업 연속성 참고 자료](references/continuity.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 참고 자료·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 참고 자료를
읽고 수동으로 재개할 수 있습니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

기존 Writing 구현에서 이어받은 작성 지침·양식에는 [MIT 고지](WRITING_LICENSE.md)를 보존합니다.
이는 출처·권리 고지이며 Writing 설치나 파일 생성에 의존하지 않습니다. Workflow의 나머지 파일에
새 라이선스를 부여하는 변경은 아닙니다.

## 자동 트리거와 직접 호출

“열린 PR 상태 정리해 줘”, “이 PR의 CI 실패를 고쳐 줘”처럼 요청하면 목적에 맞는 스킬을
선택합니다. `$inspect-prs`, `$repair-pr`로 직접
호출할 수도 있습니다. 이름 지정 자체는 commit·push·댓글·대화 해결 권한이 아닙니다.
조회는 읽기 전용으로 완료하고 복구는 요청된 수정·검증과 승인된 원격 반영을 구분합니다.
[PR 조회 기준](references/pr-inspection.md), [설계 참고](UPSTREAM.md),
[평가 사례](../../evals/skill-expansion/README.md)를 참고하세요.
