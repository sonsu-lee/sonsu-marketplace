# Workflow

Git branch·commit·push, 티켓, PR 작성과 PR 상태 조회·복구를 승인 범위 안에서 수행하고 초안·실제 반영·미확인을 구분해 보고합니다.

## 설치

```bash
codex plugin add workflow@sonsu-marketplace
claude plugin install workflow@sonsu-marketplace
omp plugin install workflow@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `branch` | 브랜치 이름을 제안·검토하거나 새 branch 생성을 요청할 때 | 근거 있는 이름 또는 생성된 branch와 확인된 HEAD |
| `commit` | 메시지를 준비하거나 요청한 변경만 commit할 때 | Conventional Commit 메시지 또는 새 commit과 남은 변경 |
| `push` | 현재 commit을 정확한 remote ref로 보낼 때 | 실제 원격 SHA 또는 미확인 상태 |
| `review-commit` | commit 후보나 기존 commit을 읽기 전용으로 검토할 때 | 근거 위치가 있는 문제 목록 또는 문제 없음 |
| `to-ticket` | Linear·GitHub Issues 티켓을 작성·게시하거나 제목·본문을 수정할 때 | 티켓 초안 또는 필드별 실제 반영 상태 |
| `ticket-lifecycle` | 기존 티켓의 상태·담당자·관계를 바꿀 때 | operation별 applied·unapplied·unknown·no-op |
| `to-pr` | 새 PR 초안을 준비하거나 게시할 때 | PR payload 또는 게시 단계별 결과 |
| `inspect-prs` | 열린 PR이나 지정 PR의 CI·리뷰·병합 상태를 볼 때 | head와 조회 시점이 연결된 상태 보고 |
| `repair-pr` | PR 충돌·리뷰 지적·실패 CI를 복구할 때 | 해결·기각·추가 확인 필요와 원격 반영 결과 |

“열린 PR 상태 정리해 줘”처럼 자연어로 요청하거나 `$inspect-prs`처럼 이름으로 호출합니다. 이름 지정은 commit·push·댓글·대화 해결 권한을 추가하지 않습니다. branch·commit·push가 함께 요청되면 각 결과를 확인하며 순서대로 수행하고, commit만 요청되면 commit에서 끝냅니다. 조회·복구 평가 사례는 [skill-expansion](../../evals/skill-expansion/README.md)에 있습니다.

## 사용 예시

요청: “현재 branch의 PR 초안만 준비해 줘. 게시는 하지 마.”

`to-pr`가 [`scripts/pr_context.py`](scripts/pr_context.py)로 base·head·commit 범위와 양식 후보를 읽고, 원격 쓰기 없이 제목·본문과 미확인 항목을 보고합니다. 결과의 `templates.status`가 `local-only`이면 양식을 미확인으로 둡니다.

## 구성

- 공통 기준: [Git 안전 규칙](references/git-safety.md), [전달 권한](references/delivery-authority.md), [커밋 메시지 기준](references/commit-message.md), [문장 형식 기준](references/tracker-prose.md), [PR 조회](references/pr-inspection.md)
- 티켓은 [티켓 작성 지침](skills/to-ticket/references/ticket-writing.md)으로 현재 문제·영향, 원하는 결과, 지켜야 할 기존 동작·제약·합의된 선택 기준을 설명하고 결과와 수용 조건은 본문에 한 번 남깁니다. 대상 양식이 없다고 확인되면 일반·버그·조사 기본형으로 필요한 정보를 구성하되 제목이나 분량을 강제하지 않습니다.
- PR은 [주제·의존 관계 기준](skills/to-pr/references/stacked-prs.md), [PR 템플릿 규칙](skills/to-pr/references/pr-template.md), [PR 작성 지침](skills/to-pr/references/pr-writing.md)으로 왜 바꿨는지, 동작과 처리 방식이 어떻게 달라졌는지, 검토·배포에 필요한 제약을 설명합니다. 정적 세부사항은 마킹 이미지, 상호작용·시간 흐름은 실제 영상으로 보여 주며 서로 다른 판단에 필요할 때만 두 매체를 함께 씁니다.
- 티켓 연결은 브랜치명에 ID를 넣지 않고 PR 본문에서 합니다. Linear는 [공식 magic word와 확인된 URL](skills/to-pr/references/ticket-linking.md#linear)로 일부 기여·전체 해결·단순 관련을 구분합니다. AI attribution과 도구 서명은 [AI 사용 표기](references/tracker-prose.md#ai-사용-표기)에 따라 자동으로 넣지 않으며, 사용자의 제외 요청과 외부 필수 규칙이 충돌하면 메시지 밖에서 알립니다.
- 함께 설치된 Writing과 Fluent Languages 스킬은 [결합 기준](references/writing-composition.md)에 따라 한 초안에 적용합니다. 설치되지 않은 플러그인은 그대로 둡니다.
- 도구: [`pr_context.py`](scripts/pr_context.py)는 PR 게시 입력을, [`validate_attachment_manifest.py`](scripts/validate_attachment_manifest.py)는 첨부 manifest를, [`inspect_prs.py`](scripts/inspect_prs.py)는 PR 상태를 읽기 전용으로 수집·판정합니다.
- [작업 연속성](references/continuity.md)은 여러 단계 작업의 계약·진행·근거 위치를 `.sonsu/continuity/`에 기록합니다. 포함된 `SessionStart` hook은 활성 기록이 있을 때 경로만 전달하며 CLI의 `/hooks`에서 검토·신뢰해야 실행됩니다. helper는 Python 3.9+와 POSIX(macOS/Linux)를 사용합니다. [기록 형식](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
- 작성 지침·양식의 출처 고지는 [MIT 고지](WRITING_LICENSE.md)에, 설계 참고는 [UPSTREAM.md](UPSTREAM.md)에 있습니다.

## 검증

```bash
python3 -B -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
python3 scripts/validate_refactor_inventory.py check --plugin workflow
```
