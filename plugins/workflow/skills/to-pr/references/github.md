# GitHub PR 규칙

GitHub PR payload를 작성하거나 새 PR을 게시할 때 읽는다. 여러 PR의 주제·의존 관계와 native stack 게시에는 [stacked PR 규칙](stacked-prs.md)을 함께 적용한다.

## 상태를 수집한다

[`pr_context.py`](../../../scripts/pr_context.py)가 저장소 상태를 읽기 전용으로 수집한다. fetch, checkout, Git 설정 변경 없이 로컬 객체만 읽고, 네트워크 조회는 `--offline`이 없을 때만 한다. 원격 조회가 인증 입력을 요구하거나 30초 안에 끝나지 않으면 실패로 `errors`에 남기고 해당 항목을 `unverified`로 둔다. 각 확인 항목은 다음 필드로 판단한다.

| 확인 항목 | 필드 |
|---|---|
| 정확한 `[HOST/]OWNER/REPOSITORY`, visibility, fork의 상위 저장소, 인증 주체 | `repository` (`remote`, `github`, `github.parent`, `auth_login`) |
| base 결정 순서: 사용자 지정, branch의 `gh-merge-base`, 저장소 default branch | `base.source` |
| 대상 branch, upstream, remote ref, head SHA | `head` |
| merge base부터 head까지의 commit과 diff | `range` |
| 저장소 root, linked worktree, 진행 중인 Git 작업과 staged·unstaged·untracked 변경 | `repository.worktree`, `working_tree` |
| 적용할 PR 양식 | `templates` ([PR 템플릿 규칙](pr-template.md)) |
| 같은 저장소 head branch의 open·draft PR. fork의 같은 이름 branch PR은 `items`에 `is_cross_repository: true`로만 남는다. | `existing_prs` |

`range`에 관련 없는 commit이나 파일이 있으면 포함 범위를 그대로 두고 보고한다. `working_tree`의 미커밋 변경은 원격 PR diff에 들어가지 않으므로 별도로 보고한다. `CONTRIBUTING`·기존 PR 관례는 직접 읽는다. `repository.remote.url`은 https URL의 자격 증명을 뺀 값이다.

`repository.github`는 push remote의 저장소다. 온라인 조회에서 이 저장소가 fork로 확인되면 `github.parent`에 상위 저장소 `owner`·`name`이 들어가고, PR이 parent에 있을 수 있으므로 기존 PR은 조회하지 않는다. 이때 `unverified`에 `github-repository`와 `existing-prs`가 들어간다. PR 대상 저장소와 그 저장소 기준의 base·양식·기존 PR을 사용자에게 확인하고, 확인 전에는 게시하지 않는다. fork가 아니거나 확인하지 못했으면 `github.parent`는 `null`이다.

stack의 위층은 `--base refs/heads/<아래 branch>`로 실행한다. 이때 `range`는 바로 아래 branch의 head부터 위층 head까지이며, `base-not-ancestor`가 있으면 선형 ancestry가 아니므로 멈춘다.

`blockers`에 값이 있으면 그 PR을 만들지 않고 정확한 현재 상태와 필요한 별도 Git workflow를 보고한다.

| blocker | 의미 |
|---|---|
| `detached-head` | 대상이 이름 있는 branch가 아니다. stack의 모든 대상도 이름 있는 branch여야 한다. |
| `operation-in-progress` | merge·rebase·cherry-pick·revert·bisect가 진행 중이다. |
| `base-unresolved`, `no-merge-base` | base를 해석하지 못했거나 head와 공통 조상이 없다. |
| `base-not-ancestor` | stack 위층이 아래 branch의 현재 head를 포함하지 않는다. |
| `head-equals-base` | head와 base가 같은 branch(로컬 branch와 그 remote-tracking ref 포함)이거나 같은 commit이다. base branch에 직접 만든 미push commit도 PR로 보내지 않는다. |
| `empty-range` | PR로 보낼 commit이 없다. |
| `existing-pr` | push 대상 저장소의 같은 branch에서 열린 PR이 이미 있다. 다른 fork에서 이름이 같은 branch로 연 PR은 `items`에만 남고 blocker가 되지 않는다. |

PR에 새 branch가 필요하면 이름을 제안만 하고 생성·rename은 사용자의 별도 Git 작업으로 넘긴다. 이름을 제안할 때는 [공통 이름 규칙](../../../references/branch-naming.md)을 읽는다. `unverified`에 있는 항목은 확인하지 못한 상태로 보고하고 그 항목에 기대는 결정을 확정하지 않는다.

## payload를 준비한다

title과 body를 명시적으로 완성한다. [PR 템플릿 규칙](pr-template.md)에 따라 저장소 template과 언어를 결정하고 `--fill`의 자동 생성 결과만 사용하지 않는다. ticket reference, validation과 visual evidence는 실제 근거가 있을 때만 넣는다.

`target_pr_state`는 [메인 스킬의 모드 규칙](../SKILL.md#모드를-정한다)으로 정한다. Draft 지원 여부를 확인하며, Draft 요청을 Ready로 대체하지 않는다.

CLI에서는 완성한 multiline body를 임시 파일에 기록하고 `gh pr create --body-file`로 전달한다. `--template`은 base 저장소가 노출한 양식 filename으로 시작 본문만 제공하고 `--body`·`--body-file`과 함께 쓸 수 없으므로 사용하지 않는다. 실행 시점의 `gh pr create --help`, target host와 base 저장소 권한을 확인한다. `--dry-run`도 Git push를 수행할 수 있으므로 read-only 검사로 사용하지 않는다. 미디어가 있으면 생성 전에 [미디어 첨부 규칙](media-attachments.md)을 읽어 파일·지원 경로와 필수 검사를 확인한다.

공식 참고: [GitHub CLI `gh pr create`](https://cli.github.com/manual/gh_pr_create), [`gh pr edit`](https://cli.github.com/manual/gh_pr_edit)

## publish 권한을 적용한다

명시적인 새 PR publish 요청이 있고 대상 branch가 아직 승인된 기존 remote에 게시되지 않았다면 필요한 일반 push를 수행할 수 있다. 정확한 refspec을 사용하고 결과를 다시 읽는다.

다음이 필요하면 중단한다.

- force push
- 새 fork 또는 remote
- branch 생성·rename
- commit 수정
- Git 설정 변경
- 기존 PR 수정
- 로그인, 계정 전환 또는 scope 확대

같은 head의 기존 PR이 있으면 새 PR을 만들지 않는다. publish 시작 전에 이미 존재하던 PR은 업데이트하지 않고 URL과 현재 상태를 보고한다. 방금 만든 PR에 대한 예외는 [경계](../SKILL.md#경계)를 따른다.

## 생성하고 검증한다

1. `pr_context.py`를 다시 실행해 `repository`·`auth_login`·`base`·`head.sha`·`head.remote_sha`가 준비한 payload의 값과 같고 `existing_prs.status`가 `checked`이며 `blockers`가 비어 있는지 확인한다. 최종 제목·본문·티켓 연결·검증 근거·`target_pr_state`가 요청 범위에 맞는지 대조한다.
2. 필요한 일반 push를 한 번 수행하고 remote ref를 확인한다.
3. 미디어가 없으면 `draft`에 `--draft`를 사용하고 명시된 `ready`에만 non-draft로 생성한다. 미디어가 있으면 생성부터 [첨부 절차](media-attachments.md#draft-pr을-먼저-만들고-한-파일씩-첨부한다)에 맡긴다. CLI를 쓸 수 없을 때의 대안도 그 문서를 따른다.
4. 반환된 URL이나 number로 PR을 다시 읽어 정확한 저장소·URL·번호·제목·본문·base·head·Draft 상태·head SHA와 ticket reference를 확인한다. 미디어가 있으면 첨부 절차의 업로드·본문 배치·표시 순서·접근 범위 확인 결과도 대조한다.

응답이 불명확하면 같은 push·create·edit를 반복하지 않는다. stdout, remote ref, 같은 head의 기존 PR과 저장된 body를 먼저 조회하여 성공한 단계와 남은 단계를 구분한다. 첨부의 부분 성공과 결과 불명은 [미디어 복구 규칙](media-attachments.md#실패와-부분-성공을-복구한다)을 따른다.
