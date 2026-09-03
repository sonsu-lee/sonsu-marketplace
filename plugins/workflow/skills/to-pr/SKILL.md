---
name: to-pr
description: 현재 Git branch를 새 GitHub Pull Request 초안이나 게시 payload로 만들고, GitHub Issues·Linear·Jira 티켓 연결, 변경 위치를 마킹한 이미지 또는 비디오 증거를 포함해야 할 때 사용한다. branch·commit 생성, 기존 PR 수정, code review와 merge에는 사용하지 않는다.
---

# to-pr: PR로 변환하기

현재 branch의 실제 변경을 검토 가능한 새 GitHub Pull Request로 표현한다. 티켓 연결은 PR metadata를 우선하고, 화면 변경에는 필요한 시각 증거와 게시 가능한 미디어 계획을 포함한다.

## 책임 경계를 지킨다

이 스킬은 새 PR의 초안과 게시를 담당한다. branch·worktree·commit 생성, branch rename, commit rewrite, rebase·squash, force push, merge와 기존 PR 수정은 담당하지 않는다. 다만 현재 publish 흐름에서 방금 만든 GitHub Draft PR에 검토한 미디어를 첨부하고, 필수 첨부를 모두 검증한 뒤 사용자가 명시한 ready 상태로 전환할 수 있다. 코드 구현, 일반적인 작업 완료, 티켓 작성, code review 또는 push 요청만으로 자동 실행하지 않는다.

이 스킬은 현재 대화, repository와 검증 가능한 티켓 정보를 바탕으로 독립적으로 동작한다. 다른 플러그인이나 스킬이 설치되었거나 먼저 실행되었다고 가정하지 않는다.

## 모드를 정한다

- `draft`: repository를 읽고 PR title, body, 티켓 연결, validation 상태와 필요한 시각 자료 계획을 완성한다. push, 미디어 업로드와 PR 생성은 하지 않는다.
- `publish`: 사용자가 현재 대화에서 새 PR 생성을 명시적으로 요청한 경우에만 검증된 current branch를 일반 push하고 새 PR을 만든다.

단순한 작성 요청은 `draft`로 처리한다. 여기서 `draft`는 원격 PR을 만들지 않는 준비 모드이며
GitHub Draft 상태와 다르다.

`publish`의 목표 GitHub 상태는 다음 순서로 정한다.

1. 사용자가 Ready, non-draft 또는 즉시 review 가능한 상태를 명시하면 `ready`로 정한다.
2. 사용자가 GitHub Draft를 명시하면 `draft`로 정한다.
3. 상태를 명시하지 않으면 `draft`로 정한다.

“PR을 만들어 줘”, “올려 줘”, “게시해 줘”와 `open a PR`은 publish 요청일 뿐 ready 요청이
아니다. 변경이 완성됐거나 validation이 통과했고 미디어가 없다는 이유로 기본 Draft를 Ready로
올리지 않는다. `target_pr_state`가 `draft`인데 target host가 Draft PR을 지원하지 않으면 Ready로
대체하지 않고 중단하여 제약을 보고한다. 게시 전 payload에 결정한 `target_pr_state`와 그 근거를
표시한다.

명시적인 publish 요청은 정확한 기존 remote로 current branch를 일반 push하는 데 필요한 권한을
포함하지만, fork·remote 생성, force push, publish 시작 전에 이미 존재하던 PR의 변경 또는
merge로 확대하지 않는다. 같은 publish 흐름에서 안전 게이트로 방금 만든 GitHub Draft PR에는
검토한 manifest의 미디어만 첨부하고, 모든 필수 첨부를 검증한 뒤 사용자가 명시적으로 요청한
ready 상태로만 전환할 수 있다. 같은 권한을 반복해서 묻지 않는다.

## repository와 변경을 고정한다

다음 내용을 읽기 전용으로 확인한다.

- repository root, current branch, detached HEAD와 linked worktree 여부
- 진행 중인 Git 작업, staged·unstaged·untracked 변경
- remote, upstream, repository default branch와 요청된 base
- merge base, base부터 head까지의 commit과 전체 diff
- current branch의 기존 PR
- target repository와 owner의 public `.github` repository default branch에 있는 PR template, contribution 지침, semantic title·Conventional Commit 관례와 PR 언어
- 관련 validation 명령과 현재 결과

`gh pr create --fill`이나 commit 제목만으로 변경 내용을 추론하지 않는다. working tree의 미커밋 변경은 PR commit range에 포함되지 않으므로 별도로 보고한다. 기존 PR이 있으면 새 PR을 만들거나 기존 PR을 수정하지 않고 현재 상태와 필요한 다음 행동을 알린다.

PR을 작성할 때에는 [PR 템플릿 규칙](references/pr-template.md)으로 repository template과 출력 언어를 먼저 결정하고, [PR 품질 기준](references/pr-quality-bar.md)을 읽는다. target repository template을 먼저 사용하고, 없으면 owner의 account-level default template을 사용한다. 둘 다 없다고 확인된 경우에만 스킬의 기본 템플릿을 사용한다.

## 티켓을 연결한다

티켓 ID나 URL이 있거나 사용자가 연동을 요청하면 [티켓 연결 규칙](references/ticket-linking.md)을 읽는다.

PR body의 공식 reference를 먼저 사용하고, provider가 필요로 할 때에만 PR title을 사용한다. 이미 존재하는 branch 이름의 ID는 가장 낮은 신뢰도의 hint로만 취급한다. branch에 ID가 없다는 이유로 PR을 막거나 branch를 만들고 rename하지 않는다.

GitHub Issues, Linear와 Jira 중 provider를 문자열 모양만으로 추측하지 않는다. 같은 작업이 여러 tracker에 동기화되어 있으면 canonical ticket을 확인하여 의도하지 않은 중복 completion을 만들지 않는다.

티켓 intent와 PR event의 status effect는 분리한다. 게시 전에 대상 repository·team·site의 integration과 automation 정책을 확인하고, native automation이 해당 event를 처리하면 직접 같은 transition을 실행하지 않는다. Draft PR 생성은 review 시작으로 간주하지 않는다. merge도 release·deployment가 완료 조건인 티켓을 곧바로 완료시키지 않는다.

직접 lifecycle fallback은 automation 부재 또는 해당 event 비적용, canonical ticket의 현재 상태, 정확한 목표 transition과 실행 권한이 확인되고, 전이 근거가 직접 사용자 의도 또는 확인된 repository·team lifecycle 정책일 때만 다음 runtime 책임으로 넘긴다. 비동기 automation 결과가 불명확하면 `status_effect: unknown`으로 남기고 직접 전이하지 않는다.

## 시각 증거를 준비한다

사용자가 screenshot을 요청했거나 diff가 사용자에게 보이는 UI를 바꾸거나 repository 규칙이 요구할 때만 [시각 증거 규칙](references/visual-evidence.md)을 읽는다. UI와 무관한 변경에는 빈 screenshot 섹션을 만들지 않는다.

capture와 비교에는 repository에 이미 있는 도구를 우선한다. 새 dependency를 설치하지 않는다. 안전하고 동일한 baseline을 얻지 못하면 after만 제시하고 before/after 비교나 visual regression 성공을 주장하지 않는다.

로컬 이미지나 비디오를 PR에 넣어야 하면 [media 첨부 규칙](references/media-attachments.md)을 읽는다. PR에 증거로 올리는 이미지에는 애니메이션 GIF를 포함하여 변경 위치를 마킹한 사본만 사용한다. 별도 설정이 없는 기본 provider는 GitHub native attachment이며, 현재 `gh pr edit --help`에 `--attach`가 있고 target host와 base repository 권한도 지원되면 CLI를 우선한다. 외부 object storage와 repository asset은 사용자가 명시적으로 선택한 경우에만 사용한다.

## 새 PR을 게시한다

GitHub용 payload를 작성하거나 publish할 때 [GitHub PR 규칙](references/github.md)을 읽는다. publish 직전에는 다음 내용을 다시 확인한다.

- 정확한 repository, 인증 주체, base, head와 remote ref
- current head SHA와 전체 commit range
- final title, body, 선택한 template source, PR 언어, ticket link와 validation 상태
- `target_pr_state`, 기본 Draft 또는 명시적인 Ready를 선택한 근거
- screenshot이 필수이면 마킹된 최종 이미지와 게시 경로
- 각 미디어의 ready 필수 여부, annotation, 실제 content type·MIME·decode, 전체 내용의 민감정보 검사와 embedded metadata 검사 결과
- 같은 head의 기존 PR 부재

GitHub CLI attachment가 가능하면 먼저 첨부 없이 GitHub Draft PR을 생성하여 Draft 지원과 정확한 대상 PR을 확인한다. 그 Draft PR에 로컬 경로를 body에 노출하지 않은 채 검토한 파일을 `gh pr edit --attach`로 하나씩 전달하고 매번 저장된 body를 다시 읽는다. 모든 필수 첨부가 확인되고 사용자가 ready를 명시한 경우에만 ready 상태로 전환한다. CLI attachment를 사용할 수 없으면 browser attachment로 전환한다. 플랫폼이 Draft PR 자체를 지원하지 않으면 기본 또는 명시적인 Draft PR 요청은 중단하고, 사용자가 ready를 명시한 요청에만 browser에서 모든 첨부를 확인한 뒤 게시하는 흐름을 사용할 수 있다. 어느 경로에서도 비공식 upload endpoint를 직접 사용하지 않는다. 자동 첨부가 불가능하면 PR 작성 화면과 미디어 폴더를 준비하여 사용자가 마지막 drag-and-drop과 제출만 수행하게 한다.

CLI로 게시할 때 본문은 임시 파일에 정확히 기록하고 `gh pr create --body-file`을 사용한다. 현재 `gh` 도움말과 repository 상태를 확인하며, push할 수 있는 `--dry-run`을 안전한 read-only 검증으로 취급하지 않는다.

## 결과를 확인한다

게시 후에는 PR을 다시 읽어 URL, number, title, body, base, head, draft 여부, head SHA, ticket reference와 visual evidence를 확인한다. 가능하면 canonical ticket도 다시 읽어 link가 적용됐는지와 status effect가 실제로 발생했는지를 별도로 확인한다. 미디어가 있으면 로컬 경로가 남지 않았는지, 저장된 URL, 표시 순서와 접근 범위도 확인한다.

push, Draft PR 생성, 미디어별 업로드·body 반영, ready 전환, 티켓 link와 status effect의 성공 여부를 각각 구분한다. `gh pr edit --attach`도 upload 뒤 body update가 실패하여 orphan attachment를 남길 수 있으므로, 실패 코드만 보고 다시 실행하지 않는다. 응답이 불명확하면 head의 기존 PR과 저장된 body를 먼저 조회한다. 실행하지 않은 validation과 확인하지 못한 provider 상태를 성공으로 표현하지 않는다.
