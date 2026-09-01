---
name: to-pr
description: Use when 현재 Git branch를 새 GitHub Pull Request 초안이나 게시 payload로 만들고, GitHub Issues·Linear·Jira 티켓 연결 또는 필요한 시각 증거를 포함해야 할 때. branch·commit 생성, 기존 PR 수정, code review와 merge에는 사용하지 않는다.
---

# PR로 변환하기

현재 branch의 실제 변경을 검토 가능한 새 GitHub Pull Request로 표현한다. 티켓 연결은 PR metadata를 우선하고, 화면 변경에는 필요한 시각 증거와 게시 가능한 이미지 계획을 포함한다.

## 책임 경계를 지킨다

이 스킬은 새 PR의 초안과 게시를 담당한다. branch·worktree·commit 생성, branch rename, commit rewrite, rebase·squash, force push, merge와 기존 PR 수정은 담당하지 않는다. 코드 구현, 일반적인 작업 완료, 티켓 작성, code review 또는 push 요청만으로 자동 실행하지 않는다.

`to-ticket`, Superpowers 또는 별도 planning·Git workflow가 먼저 실행되었다고 가정하지 않는다. 다른 스킬이 없어도 현재 대화, repository와 검증 가능한 티켓 정보만으로 동작한다.

## 모드를 정한다

- `draft`: repository를 읽고 PR title, body, 티켓 연결, validation 상태와 필요한 시각 자료 계획을 완성한다. push, 이미지 업로드와 PR 생성은 하지 않는다.
- `publish`: 사용자가 현재 대화에서 새 PR 생성을 명시적으로 요청한 경우에만 검증된 current branch를 일반 push하고 새 PR을 만든다.

단순한 작성 요청은 `draft`로 처리한다. 명시적인 publish 요청은 정확한 기존 remote로 current branch를 일반 push하는 데 필요한 권한을 포함하지만, fork·remote 생성, force push, 기존 PR 변경 또는 merge로 확대하지 않는다. 같은 권한을 반복해서 묻지 않는다.

## repository와 변경을 고정한다

다음 내용을 읽기 전용으로 확인한다.

- repository root, current branch, detached HEAD와 linked worktree 여부
- 진행 중인 Git 작업, staged·unstaged·untracked 변경
- remote, upstream, repository default branch와 요청된 base
- merge base, base부터 head까지의 commit과 전체 diff
- current branch의 기존 PR
- PR template, contribution 지침, semantic title·Conventional Commit 관례
- 관련 validation 명령과 현재 결과

`gh pr create --fill`이나 commit 제목만으로 변경 내용을 추론하지 않는다. working tree의 미커밋 변경은 PR commit range에 포함되지 않으므로 별도로 보고한다. 기존 PR이 있으면 새 PR을 만들거나 기존 PR을 수정하지 않고 현재 상태와 필요한 다음 행동을 알린다.

PR을 작성할 때에는 [PR 품질 기준](references/pr-quality-bar.md)을 읽는다.

## 티켓을 연결한다

티켓 ID나 URL이 있거나 사용자가 연동을 요청하면 [티켓 연결 규칙](references/ticket-linking.md)을 읽는다.

PR body의 공식 reference를 먼저 사용하고, provider가 필요로 할 때에만 PR title을 사용한다. 이미 존재하는 branch 이름의 ID는 가장 낮은 신뢰도의 hint로만 취급한다. branch에 ID가 없다는 이유로 PR을 막거나 branch를 만들고 rename하지 않는다.

GitHub Issues, Linear와 Jira 중 provider를 문자열 모양만으로 추측하지 않는다. 같은 작업이 여러 tracker에 동기화되어 있으면 canonical ticket을 확인하여 의도하지 않은 중복 completion을 만들지 않는다.

## 시각 증거를 준비한다

사용자가 screenshot을 요청했거나 diff가 사용자에게 보이는 UI를 바꾸거나 repository 규칙이 요구할 때만 [시각 증거 규칙](references/visual-evidence.md)을 읽는다. UI와 무관한 변경에는 빈 screenshot 섹션을 만들지 않는다.

capture와 비교에는 repository에 이미 있는 도구를 우선한다. 새 dependency를 설치하지 않는다. 안전하고 동일한 baseline을 얻지 못하면 after만 제시하고 before/after 비교나 visual regression 성공을 주장하지 않는다.

이미지를 PR에 넣어야 하면 [이미지 게시 규칙](references/image-publishing.md)을 읽는다. 별도 설정이 없는 기본 provider는 GitHub native attachment다. 외부 object storage와 repository asset은 사용자가 명시적으로 선택한 경우에만 사용한다.

## 새 PR을 게시한다

GitHub용 payload를 작성하거나 publish할 때 [GitHub PR 규칙](references/github.md)을 읽는다. publish 직전에는 다음 내용을 다시 확인한다.

- 정확한 repository, 인증 주체, base, head와 remote ref
- current head SHA와 전체 commit range
- final title, body, template, ticket link와 validation 상태
- screenshot이 필수이면 최종 이미지와 게시 경로
- 같은 head의 기존 PR 부재

browser를 통한 GitHub attachment가 필요하면 PR payload와 이미지를 먼저 완성하고 첨부를 마지막에 수행한다. 자동 첨부가 불가능하면 비공식 upload endpoint를 사용하지 않고, PR 작성 화면과 이미지 폴더를 준비하여 사용자가 마지막 drag-and-drop과 제출만 수행하게 한다.

CLI로 게시할 때 본문은 임시 파일에 정확히 기록하고 `gh pr create --body-file`을 사용한다. 현재 `gh` 도움말과 repository 상태를 확인하며, push할 수 있는 `--dry-run`을 안전한 read-only 검증으로 취급하지 않는다.

## 결과를 확인한다

게시 후에는 PR을 다시 읽어 URL, number, title, body, base, head, draft 여부, head SHA, ticket reference와 visual evidence를 확인한다. 이미지가 있으면 저장된 Markdown과 접근 범위도 확인한다.

push, 이미지 업로드, PR 생성과 티켓 연결의 성공 여부를 각각 구분한다. 응답이 불명확하거나 일부만 성공하면 같은 작업을 반복하기 전에 원격 상태를 조회한다. 실행하지 않은 validation과 확인하지 못한 provider 상태를 성공으로 표현하지 않는다.
