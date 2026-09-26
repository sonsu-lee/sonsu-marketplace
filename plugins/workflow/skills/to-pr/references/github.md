# GitHub PR 규칙

GitHub PR payload를 작성하거나 새 PR을 게시할 때 읽는다. 여러 PR의 주제·의존 관계와 native stack 게시에는 [stacked PR 규칙](stacked-prs.md)을 함께 적용한다.

## 저장소 상태를 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY`, visibility와 인증 주체를 비밀값 없이 확인한다.
- 사용자가 지정한 base를 우선하고, 없으면 branch의 `gh-merge-base` 설정과 저장소 default branch를 확인한다.
- 대상 브랜치, upstream, remote ref와 head SHA를 확인한다.
- 단일 PR은 base의 merge base부터 head까지, stack은 각 층의 base부터 head까지 commit과 diff를 읽는다.
- [PR 템플릿 규칙](pr-template.md)으로 적용할 양식과 `CONTRIBUTING`·기존 PR 관례를 확인한다.
- 대상 head branch마다 open·draft PR을 조회한다.

필요한 객체가 로컬에 없더라도 사용자 요청 없이 fetch하거나 checkout을 바꾸지 않는다. 미커밋 변경은 원격 PR diff에 들어가지 않으므로 별도로 보고한다.

단일 PR 대상이 detached HEAD이거나, 어느 대상이든 head와 base가 같거나 PR commit range가 비어 있으면 그 PR을 만들지 않는다. stack의 모든 대상은 이름 있는 branch여야 한다. 정확한 현재 상태와 필요한 별도 Git workflow를 보고한다. PR을 위해 새 브랜치가 필요하더라도 이 스킬에서 생성·rename하지 않는다. 이름을 제안할 때는 [공통 이름 규칙](../../../references/branch-naming.md)을 읽는다.

## payload를 준비한다

title과 body를 명시적으로 완성한다. [PR 템플릿 규칙](pr-template.md)에 따라 저장소 template과 언어를 결정하고 `--fill`의 자동 생성 결과만 사용하지 않는다. ticket reference, validation과 visual evidence는 실제 근거가 있을 때만 넣는다.

`target_pr_state`는 [메인 스킬의 모드 규칙](../SKILL.md#모드를-정한다)으로 정한다. Draft 지원 여부를 확인하며, Draft 요청을 Ready로 대체하지 않는다.

CLI에서는 완성한 multiline body를 임시 파일에 기록하고 `gh pr create --body-file`로 전달한다. `--template`과 함께 사용하지 않는다. 실행 시점의 `gh pr create --help`, target host와 base 저장소 권한을 확인한다. `--dry-run`도 Git push를 수행할 수 있으므로 read-only 검사로 사용하지 않는다. 미디어가 있으면 생성 전에 [미디어 첨부 규칙](media-attachments.md)을 읽어 파일·지원 경로와 필수 검사를 확인한다.

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

같은 head의 기존 PR이 있으면 새 PR을 만들지 않는다. 이 스킬은 publish 시작 전에 이미 존재하던 PR을 업데이트하지 않으므로 URL과 현재 상태를 보고한다. 예외는 현재 publish 흐름에서 방금 만든 GitHub Draft PR에 검토한 manifest의 미디어를 첨부하고 사용자가 명시한 ready 상태로 전환하는 경우뿐이다.

## 생성하고 검증한다

1. 저장소·인증 주체·base·head SHA·remote ref와 같은 head의 기존 PR 부재를 재확인한다. 최종 제목·본문·티켓 연결·검증 근거·`target_pr_state`가 요청 범위에 맞는지 대조한다.
2. 필요한 일반 push를 한 번 수행하고 remote ref를 확인한다.
3. 미디어가 없으면 `draft`에 `--draft`를 사용하고 명시된 `ready`에만 non-draft로 생성한다. 미디어가 있으면 생성부터 [첨부 절차](media-attachments.md#draft-pr을-먼저-만들고-한-파일씩-첨부한다)에 맡긴다. CLI를 쓸 수 없을 때의 대안도 그 문서를 따른다.
4. 반환된 URL이나 number로 PR을 다시 읽어 정확한 저장소·URL·번호·제목·본문·base·head·Draft 상태·head SHA와 ticket reference를 확인한다. 미디어가 있으면 첨부 절차의 업로드·본문 배치·표시 순서·접근 범위 확인 결과도 대조한다.

응답이 불명확하면 같은 push·create·edit를 반복하지 않는다. stdout, remote ref, 같은 head의 기존 PR과 저장된 body를 먼저 조회하여 성공한 단계와 남은 단계를 구분한다. 첨부의 부분 성공과 결과 불명은 [미디어 복구 규칙](media-attachments.md#실패와-부분-성공을-복구한다)을 따른다.
