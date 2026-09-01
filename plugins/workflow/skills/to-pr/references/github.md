# GitHub PR 규칙

GitHub PR payload를 작성하거나 새 PR을 게시할 때 읽는다.

## repository 상태를 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY`, visibility와 인증 주체를 비밀값 없이 확인한다.
- 사용자가 지정한 base를 우선하고, 없으면 branch의 `gh-merge-base` 설정과 repository default branch를 확인한다.
- current branch, upstream, remote ref와 head SHA를 확인한다.
- base의 merge base부터 head까지 commit과 전체 diff를 읽는다.
- `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/**`, `docs/pull_request_template.md`, `CONTRIBUTING`과 기존 PR 관례를 확인한다.
- 같은 head branch의 open·draft PR을 조회한다.

필요한 객체가 로컬에 없더라도 사용자 요청 없이 fetch하거나 checkout을 바꾸지 않는다. 미커밋 변경은 원격 PR diff에 들어가지 않으므로 별도로 보고한다.

detached HEAD, head와 base가 같은 상태 또는 비어 있는 PR commit range에서는 새 PR을 만들지 않는다. 정확한 현재 상태와 필요한 별도 Git workflow를 보고한다.

## payload를 준비한다

title과 body를 명시적으로 완성한다. `--fill`의 자동 생성 결과만 사용하지 않는다. ticket reference, validation과 visual evidence는 실제 근거가 있을 때만 넣는다.

CLI를 사용할 때에는 multiline body를 임시 파일에 기록하고 `gh pr create --body-file`로 전달한다. 실행 시점의 `gh pr create --help`를 확인한다. `--dry-run`도 Git push를 수행할 수 있으므로 read-only 검사로 사용하지 않는다.

공식 참고: [GitHub CLI `gh pr create`](https://cli.github.com/manual/gh_pr_create)

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

같은 head의 기존 PR이 있으면 새 PR을 만들지 않는다. 이 스킬은 기존 PR을 업데이트하지 않으므로 URL과 현재 상태를 보고한다.

GitHub native attachment가 필요한 PR은 [이미지 게시 규칙](image-publishing.md)에 따라 browser 경로를 사용한다. screenshot이 필수인데 첨부할 수 없으면 이미지가 빠진 non-draft PR을 임의로 만들지 않는다.

## 생성하고 검증한다

1. final repository, base, head SHA와 payload를 확정한다.
2. 필요한 일반 push를 한 번 수행하고 remote ref를 확인한다.
3. 이미지가 없다면 `gh pr create` 같은 현재 공식 interface로 새 PR을 만든다. 이미지가 있으면 browser attachment 흐름을 따른다.
4. 반환된 URL이나 number로 PR을 다시 읽는다.
5. title, body, base, head, draft 상태, head SHA, ticket reference와 visual evidence를 대조한다.

일부 결과가 불명확하면 같은 push, attachment 또는 create를 반복하지 않는다. remote ref, 기존 PR과 저장된 body를 먼저 조회하여 성공한 단계와 남은 단계를 구분한다.
