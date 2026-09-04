---
name: finishing-a-development-branch
description: 검증된 구현이 완료되어 기존 commit을 통합하거나 보존하는 방법을 선택해야 할 때 사용한다. branch, commit, push, ticket 또는 PR artifact를 직접 만들어 달라는 요청에는 사용하지 않는다.
---

# finishing-a-development-branch: 개발 브랜치 완료

## 개요

**핵심 원칙:** 완료된 변경 검증 → 환경 감지 → 선택지 제시 → 선택 실행 → 정리.

**시작할 때 알린다:** "finishing-a-development-branch 스킬을 사용해 이 작업을 마무리하겠습니다."

## 책임 경계

이 스킬은 commit이 이미 존재하는 완료된 개발 작업을 마무리할 방법을 결정한다. 독립적으로
동작하며 다른 플러그인의 Git, ticket 또는 PR 스킬을 요구하거나 호출하지 않는다.

branch, commit, push, ticket 또는 PR artifact를 직접 생성하거나 리뷰해 달라는 요청은 해당
artifact의 사용 가능한 전문 스킬이 담당하며 이 통합 선택 menu를 열지 않는다. 구현과 이후의
전달을 포함하는 더 넓은 요청에는 별도 스킬을 순서대로 사용할 수 있지만, 이런 runtime 조합이
스킬 사이의 dependency를 만들지는 않는다.

<HARD-GATE>
이 스킬은 이미 존재하는 commit을 통합한다. commit되지 않은 구현을 commit으로 만들지 않는다. worktree에 요청받았지만 commit되지 않은 변경이 있으면 실행 workflow로 돌아가 `diff`를 보고하고, 사용자의 명시적인 commit 결정을 받거나 적용한 뒤 계속한다.
</HARD-GATE>

## 1단계: 완료된 변경 검증

먼저 구현 worktree가 명시적으로 보존한 unrelated 변경을 제외하고 깨끗한지, 통합할 commit이 존재하는지 확인한다. 이 스킬에서는 파일을 stage하거나 commit하지 않는다.

공통 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽는다.
최종 게이트가 통합할 정확한 commit 리비전을 가리키는지 확인한다. 이전 working tree 또는 commit에 대한 결과는 오래된 것이다.

plan artifact가 있는 작업이면 같은 전체 변경 리비전에 대해 다음 두 게이트를 별도로 확인한다.

- 일반 final review가 `passed`이거나 사람이 해당 리비전의 명시된 위험을 `accepted_risk`로 수용했다.
- red-team verdict가 `survives_challenge`이거나 사람이 해당 리비전의 명시된 red-team 위험을
  `accepted_risk`로 수용했다.

red-team이 `not_run`, `blocked`, `inconclusive`, `invalidated`이거나 이전 리비전만 다뤘다면 일반
final review의 `passed`로 대신하지 않고 2단계로 진행하지 않는다. plan이 없는 Fast Path에는
red-team을 새로 요구하지 않는다.

승인된 plan과 변경 유형에 필요한 최종 검증을 실행한다.

- Production 동작 또는 통합 변경에는 일반적으로 관련 전체 test suite(`npm test` / `cargo test` / `pytest` / `go test ./...`)가 필요하다.
- 문서, metadata, 정적 데이터와 단순 configuration 변경에는 지정된 link, syntax, 경로, loader 또는 실제 소비 명령 검사를 대신 사용한다.
- 저장소 지침이나 구체적인 cross-cutting 위험 때문에 더 넓은 suite가 필요할 수 있으며, 적용 이유를 기록한다.

**최종 게이트가 `failed`, `blocked`, `inconclusive`이거나 필수 검사가 `not_run`으로 표시됐다면** 실제 상태를 보고하고 중단한다. 현재 근거가 진행을 뒷받침한 뒤에만 menu를 제시한다.

```
검증에 실패했습니다. 완료하기 전에 수정해야 합니다.

[실패 내용]
```

**최종 게이트가 `passed`이면:** 2단계로 진행한다.

**사람인 의사결정자가 정확히 이 리비전에 `accepted_risk`를 명시적으로 기록했다면:** 2단계로 진행하기 전에 finding, 결과, 범위와 결정 근거를 다시 제시한다. 수용한 위험을 통과한 게이트라고 표현하지 않는다.

## 2단계: 환경 감지

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 6) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

이 정보로 제시할 menu와 정리 방법을 결정한다.

| 상태 | Menu | 정리 |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`(일반 저장소) | 표준 선택지 3개 | 정리할 worktree 없음 |
| `GIT_DIR != GIT_COMMON`, 이름이 있는 브랜치 | 표준 선택지 3개 | provenance 기준(6단계 참고) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | merge를 제외한 선택지 2개 | 외부 관리 대상이므로 그대로 유지 |

## 3단계: Base 브랜치 결정

base 브랜치는 이 작업이 fork된 브랜치다. 일반적으로 plan, 대화 또는 브랜치 upstream에
기록되어 있다. 아직 알 수 없다면 "이 브랜치는 <가장 가능성 높은 브랜치>에서 분기된 것으로
보입니다. 맞나요?"라고 질문한다. 잘못된 base에 merge하면 되돌리는 비용이 크므로 merge 전에
확인한다.

## 4단계: 선택지 제시

**일반 저장소와 이름 있는 브랜치의 worktree에서는 다음 선택지 3개를 정확히 제시한다.**

```
구현이 완료되었습니다. 어떻게 진행할까요?

1. 로컬에서 <base-branch>에 merge
2. Push하고 Pull Request 생성
3. 브랜치를 현재 상태로 유지(나중에 직접 처리)

어떤 방법을 선택할까요?
```

**Detached HEAD에서는 다음 선택지 2개를 정확히 제시한다.**

```
구현이 완료되었습니다. 현재 detached HEAD 상태입니다(외부에서 관리하는 workspace).

1. 새 브랜치로 push하고 Pull Request 생성
2. 현재 상태로 유지(나중에 직접 처리)

어떤 방법을 선택할까요?
```

위에 작성된 menu를 그대로 간결하게 제시하며, 모든 선택지는 위 목록에서 가져온다. 작업
폐기는 사용자가 명시적으로 요청한 경우에만 수행한다(아래 "사용자가 작업 폐기를 요청하는
경우" 참고). 통합 결정은 사용자의 몫이므로 답변을 기다린다.

## 5단계: 선택 실행

### 선택지 1: 로컬 merge

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Re-run the applicable final verification on the merged result
<verification command>
```

merge된 결과의 검증이 실패하면 중단하고 worktree와 브랜치를 그대로 둔 채 조사한다. 아직
push한 것이 없으므로 merge는 로컬에 있고 복구할 수 있다.

merge된 결과가 green이면 worktree를 정리하고(6단계) 브랜치를 삭제한다.

```bash
git branch -d <feature-branch>
```

### 선택지 2: Push하고 PR 생성

```bash
git push -u origin <feature-branch>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch>
```

그런 다음 forge 도구를 사용해 <base-branch>를 대상으로 pull/merge request를 만든다. 사용할
수 있으면 CLI를 사용하고, 그렇지 않으면 대부분의 forge가 push할 때 출력하는 생성 URL을
사용한다. 저장소에 PR template과 관례가 있으면 따르고 사용자에게 URL을 보고한다.

사용자가 그곳에서 PR 피드백을 반영할 수 있도록 worktree를 유지한다.

### 선택지 3: 현재 상태 유지

"브랜치 <name>을 유지합니다. Worktree는 <path>에 보존했습니다."라고 보고한다.

### 사용자가 작업 폐기를 요청하는 경우

이 경로는 작업을 폐기하라는 명시적인 요청에 대한 응답으로만 사용할 수 있다. 먼저 다음과
같이 확인한다.

```
다음 항목을 영구적으로 삭제합니다.
- 브랜치 <name>
- 모든 commit: <commit-list>
- <path>의 worktree

확인하려면 'discard'를 입력하세요.
```

정확히 이 확인을 기다린다. 사용자가 입력하면 다음을 실행한다.

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

그런 다음 worktree를 정리하고(6단계) 브랜치를 강제로 삭제한다.

```bash
git branch -D <feature-branch>
```

## 6단계: Workspace 정리

**선택지 1과 확인된 폐기에서 실행한다.** 선택지 2와 3은 항상 worktree를 보존한다. 두 호출
경로는 이미 main 저장소 root로 디렉터리를 바꿨다. worktree 삭제는 worktree 밖에서 실행해야
하며 디렉터리를 바꾸기 전 2단계에서 얻은 `GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` 값을 사용한다.

**`GIT_DIR == GIT_COMMON`이면:** 일반 저장소이므로 정리할 worktree가 없다. 종료한다.

**`WORKTREE_PATH`가 `.worktrees/` 또는 `worktrees/` 아래에 있으면:** Engineering이 만든
worktree이므로 정리를 담당한다.

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**삭제가 거부되면**(`contains modified or untracked files`) worktree에 다른 곳에는 없는 파일,
즉 commit되지 않은 plan, 메모 또는 scratch 작업이 있다는 뜻이다. 임의로 `--force`를 사용하지
않는다. 삭제 위험이 있는 항목을 사용자에게 보여 주고 질문한다.

```bash
git -C "$WORKTREE_PATH" status --porcelain -uall
```

```
Worktree를 삭제할 수 없습니다. 다음 파일은 commit된 적이 없습니다.

<파일 목록>

1. 정리하기 전에 <branch>에 commit
2. <main repo root>로 이동
3. 복구할 수 없도록 삭제

어떤 방법을 선택할까요?
```

선택한 작업을 수행한 뒤 worktree를 삭제한다.

**그 외의 경우:** host 환경이 이 workspace를 소유하므로 그대로 둔다. 플랫폼에서 workspace
종료 도구를 제공하면 사용한다.

## 빠른 참고

| 선택지 | Merge | Push | Worktree 유지 | 브랜치 정리 |
|--------|-------|------|---------------|----------------|
| 1. 로컬 merge | 예 | - | - | 예 |
| 2. PR 생성 | - | 예 | 예 | - |
| 3. 현재 상태 유지 | - | - | 예 | - |
| 폐기(명시적인 요청만) | - | - | - | 예(force) |

## 자주 하는 합리화

| 변명 | 실제 |
|--------|---------|
| "Verification passed earlier this session" | 통합하려는 tree에서 해당 최종 검증을 다시 실행한다. 이전 근거는 당시 검사한 tree만 증명한다. |
| "They obviously want it merged" | 통합은 사용자의 결정이다. menu를 제시하고 기다린다. |
| "They seem done with this feature — I'll offer to discard it" | 위 menu가 완전한 선택지다. 사용자가 명시적으로 요청한 경우에만 폐기한다. |
| "'Yeah, get rid of it' counts as confirmation" | 정확히 `discard`를 입력한 경우에만 삭제가 승인된다. |
| "The PR is up, so the worktree is clutter now" | 해당 worktree에서 PR 피드백을 수정한다. 작업이 반영될 때까지 유지한다. |
| "This other worktree looks stale — I'll clean it too" | `.worktrees/` 또는 `worktrees/` 아래의 worktree만 정리한다. 그 외의 것은 host 소유다. |
| "Removal refused — `--force` is just finishing the cleanup" | 거부됐다는 것은 해당 worktree에만 존재하는 파일이 있다는 뜻이다. `--force`는 이를 영구적으로 파괴한다. 사용자에게 보여 주고 질문한다. |
| "The merged-result failure is probably flaky" | merge 결과가 실패하면 모든 작업을 중단한다. 조사하는 동안 브랜치와 worktree를 그대로 둔다. |
| "The base branch is obviously main" | fork 지점을 확인하거나 질문한다. 잘못된 base에 merge하면 되돌리는 비용이 크다. |
| "The push was rejected — force-push will fix it" | push가 거부되면 remote가 바뀌었다는 뜻이다. 조사하며, force-push는 사용자가 명시적으로 요청한 경우에만 실행한다. |
