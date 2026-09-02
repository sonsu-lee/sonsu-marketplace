# GitHub PR 규칙

GitHub PR payload를 작성하거나 새 PR을 게시할 때 읽는다.

## repository 상태를 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY`, visibility와 인증 주체를 비밀값 없이 확인한다.
- 사용자가 지정한 base를 우선하고, 없으면 branch의 `gh-merge-base` 설정과 repository default branch를 확인한다.
- current branch, upstream, remote ref와 head SHA를 확인한다.
- base의 merge base부터 head까지 commit과 전체 diff를 읽는다.
- target default branch의 `.github`, repository root, `docs` 순서로 `pull_request_template.*`와 각 위치의 `PULL_REQUEST_TEMPLATE/**`를 확인한다. target repository에 유효한 template이 없으면 owner의 public `.github` repository default branch에서 같은 위치와 순서로 account-level default template을 확인한다. `CONTRIBUTING`과 기존 PR 관례도 확인한다.
- 같은 head branch의 open·draft PR을 조회한다.

필요한 객체가 로컬에 없더라도 사용자 요청 없이 fetch하거나 checkout을 바꾸지 않는다. 미커밋 변경은 원격 PR diff에 들어가지 않으므로 별도로 보고한다.

detached HEAD, head와 base가 같은 상태 또는 비어 있는 PR commit range에서는 새 PR을 만들지 않는다. 정확한 현재 상태와 필요한 별도 Git workflow를 보고한다.

## payload를 준비한다

title과 body를 명시적으로 완성한다. [PR 템플릿 규칙](pr-template.md)에 따라 repository template과 언어를 결정하고 `--fill`의 자동 생성 결과만 사용하지 않는다. ticket reference, validation과 visual evidence는 실제 근거가 있을 때만 넣는다.

CLI를 사용할 때에는 선택한 template을 채운 multiline body를 임시 파일에 기록하고 `gh pr create --body-file`로 전달한다. `--template`과 `--body-file`을 함께 사용하지 않는다. 실행 시점의 `gh pr create --help`, target host와 base repository 권한을 확인한다. 로컬 미디어가 있으면 `gh pr edit --help`의 `--attach` 지원도 확인하고 [미디어 첨부 규칙](media-attachments.md)에 따라 방금 만든 Draft PR에 각 파일을 하나씩 전달한다. `gh pr create --attach`는 `--web`, `--dry-run`과 함께 사용할 수 없으며, `--dry-run` 자체도 Git push를 수행할 수 있으므로 read-only 검사로 사용하지 않는다.

공식 참고: [GitHub CLI `gh pr create`](https://cli.github.com/manual/gh_pr_create), [`gh pr edit`](https://cli.github.com/manual/gh_pr_edit)

## publish 권한을 적용한다

명시적인 새 PR publish 요청이 있고 current branch가 아직 승인된 기존 remote에 게시되지 않았다면 필요한 일반 push를 수행할 수 있다. 정확한 refspec을 사용하고 결과를 다시 읽는다.

다음이 필요하면 중단한다.

- force push
- 새 fork 또는 remote
- branch 생성·rename
- commit 수정
- Git 설정 변경
- 기존 PR 수정
- 로그인, 계정 전환 또는 scope 확대

같은 head의 기존 PR이 있으면 새 PR을 만들지 않는다. 이 스킬은 publish 시작 전에 이미 존재하던 PR을 업데이트하지 않으므로 URL과 현재 상태를 보고한다. 예외는 현재 publish 흐름에서 방금 만든 GitHub Draft PR에 검토한 manifest의 미디어를 첨부하고 원래 요청한 ready 상태로 전환하는 경우뿐이다.

GitHub native attachment가 필요한 PR은 [미디어 첨부 규칙](media-attachments.md)에 따라 지원되는 GitHub CLI를 우선하고 browser를 fallback으로 사용한다. screenshot이 필수인데 마킹된 이미지를 첨부할 수 없으면 이미지가 빠진 non-draft PR을 임의로 만들지 않는다.

## 생성하고 검증한다

1. final repository, base, head SHA와 payload를 확정한다.
2. 필요한 일반 push를 한 번 수행하고 remote ref를 확인한다.
3. 미디어가 없다면 `gh pr create` 같은 현재 공식 interface로 목표 상태의 새 PR을 만든다. 미디어가 있으면 attachment 없이 GitHub Draft PR을 먼저 만든다.
4. 반환된 URL이나 number로 PR을 다시 읽어 title, body, base, head, Draft 상태와 head SHA를 확인한다.
5. 검토한 미디어를 필수 항목부터 `gh pr edit --attach` 한 파일씩 전달하고, 매번 같은 PR의 body와 manifest 상태를 다시 확인한다.
6. ticket reference와 visual evidence, 로컬 경로 부재, 저장된 URL, 순서와 접근 범위를 대조한다.
7. 필수 첨부가 모두 저장됐고 원래 요청이 ready PR 게시였다면 방금 만든 PR만 ready로 전환한 뒤 다시 읽는다. 하나라도 누락됐거나 확인할 수 없으면 Draft 상태로 유지한다.

`gh pr create --attach`와 여러 파일을 한 번에 전달하는 `gh pr edit --attach`는 앞선 파일을 업로드한 뒤 다음 파일에서 실패해도 성공한 첨부를 body에 반영하고 non-zero로 끝날 수 있다. 기본 흐름에서 둘을 사용하지 않고 Draft PR에 한 파일씩 첨부한다. 그래도 upload 뒤 body update 실패는 orphan attachment를 남길 수 있다. 일부 결과가 불명확하면 같은 push, attachment, create 또는 edit를 반복하지 않는다. stdout, remote ref, 같은 head의 기존 PR과 저장된 body를 먼저 조회하여 성공한 단계와 남은 단계를 구분한다.
