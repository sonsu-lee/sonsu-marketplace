# 풀 리퀘스트 게시

> 영문 정본: [publishing.md](publishing.md) (`4f8dd21` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

제목이나 본문을 초안으로 쓰는 것은 push, PR 생성, 머지의 허가가 아니다. 사용자가
게시를 요청하면 사용자가 의도한 저장소, head, trunk를 사용한다. trunk를 base로
쓰고, 지원되는 스택이라면 아래쪽 PR의 head 브랜치를 base로 쓴다
([의존하는 풀 리퀘스트 스택하기](#의존하는-풀-리퀘스트-스택하기) 참고).
다른 PR을 만들기 전에 해당 head와 base에 이미 PR이 있는지 확인한다. 업데이트할
때는 그 PR의 내용과 단계를 유지하며, 이미 ready인 PR을 자동으로 Draft로 되돌리지
않는다.

셸 예시는 대상 저장소의 루트에서 실행한다. `repo`는 `OWNER/REPO`로, `base`와
`head`는 의도한 브랜치로, `title`은 검증된 제목으로, `body_file`은 완성된 UTF-8
본문 파일의 절대 경로로 설정한다. 업데이트라면 `pr`을 기존 PR 번호나 URL로
설정한다. 레이블이라면 `label`을 저장소 정책에서 고른 이름으로, 지정된 것이 없으면
`ai-assisted`로 설정한다. 미디어 경로는 스킬 디렉터리가 아니라 이 작업 디렉터리를
기준으로 해석하고, 다른 곳에 저장된 캡처는 절대 경로를 사용한다. 요청한 작업에
필요한 입력만 설정한다.

## Draft로 만들기

새 PR은 로컬 검사와 CI가 통과하더라도 기본적으로 Draft다. 환경에서 요구하는 게시
도구를 사용한다. GitHub CLI를 쓴다면:

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

구조화된 GitHub API 도구라면 `draft: true`를 명시적으로 설정한다. 필드를 생략하면
Draft가 만들어진다고 가정하지 않는다. CLI 컨텍스트가 모호하면 저장소를 명시적으로
선택한다. 정확하고 템플릿을 반영한 설명을 `--fill`로 대신하지 않는다. `--dry-run`은
부작용 없는 미리보기가 아니다. GitHub CLI 문서에 따르면 변경을 push할 수도 있다.

저장소의 워크플로에 따라 의도한 커밋만 의도한 원격과 브랜치에 push한다. Draft를
게시하려는 이유만으로 force-push, 머지, auto-merge 활성화, 리뷰어 요청, 저장소 설정
변경을 하지 않는다.

반환된 URL로 생성된 PR을 확인한다. head, base, 제목, 본문, Draft 상태를 확인하며,
종료 코드만으로 생성이나 단계를 추정하지 않는다. 사용자가 명시적으로
ready-for-review를 요청하고 저장소의 준비 요건이 충족될 때까지 PR을 draft로 둔다.
Draft를 만든 뒤 자동으로 ready로 전환해서는 안 된다. ready로 표시해 달라는 요청은
머지 허가가 아니다.

## 의존하는 풀 리퀘스트 스택하기

같은 저장소에서 아직 머지되지 않은 다른 PR에 의존하는 PR에만 [스택][stacks]을
사용한다. 그 base는 아래쪽 PR의 head 브랜치이며, 맨 아래 PR은 선택한 trunk를
대상으로 한다. trunk는 사용자가 지정한 대상이나 프로젝트 대상이고, 없으면 확인한
기본 브랜치다. 독립적인 PR은 그 trunk를 대상으로 따로 둔다. 스택은 브랜치가 하나의
선형 체인을 이루고 각 브랜치가 바로 아래 브랜치를 포함하는 구조이며, 포크의 head는
포함할 수 없다. 저장소나 호스트가 스택 옵션을 제공하지 않거나 제약을 충족하지
못하면 trunk를 base로 쓰고 본문에 의존 관계와 머지 순서를 밝힌다.

위와 같이 각 PR을 만들되 `base`를 아래쪽 브랜치로 설정한 다음 서로 연결한다.
웹사이트에서는 그 base로 다음 PR을 만들 때 **Create stack**을 선택한다. 또한
GitHub는 base가 이미 체인을 이루는 기존 PR을 스택으로 묶자는 배너도 제공한다
([스택 만들기][stack-create]). `gh stack` 확장을 쓴다면
`gh stack link --base "$trunk"`가 맨 아래부터 위로 브랜치나 PR 번호를 받는다.
`trunk`는 선택한 대상으로 설정한다. `--base`를 생략하면 저장소의 기본 브랜치가
기본값이며, 연결하면서 기존 PR의 base가 그 체인에 맞게 바뀔 수 있다. 기존 스택을
확장할 때는 `--base`가 무시되므로 그 trunk를 유지하고 확인한다
([명령][stack-cli]). 브랜치 인자는 push되고, 기존 PR은 재사용되며, 없는 PR은 draft로
만들어진다([기타 도구][stack-other]). 이 확장은 선택 사항이다. 게시하려고 설치하지
않으며 웹사이트에는 필요하지 않다.

확장 명령은 기본적으로 이 절차를 따르지 않는다. `submit` 편집기는 토글하지 않는 한
새 PR을 ready-for-review로 열고, `--auto`는 제목을 생성하며, `submit`이나 `link`의
`--open`은 PR을 ready로 표시한다([명령][stack-cli]). 각 PR의 제목, 본문, Draft
상태를 확인하고 위와 같이 바로잡는다.

아래쪽 브랜치나 trunk가 바뀌면 머지에 필요한 선형 이력이 깨질 수 있다. 머지 상자의
**Rebase stack**으로, 또는 로컬에서 추적하는 스택이라면 `gh stack rebase` 후
`gh stack push`로 복구한다([관리][stack-manage]). 웹사이트에서 만든 스택이나
`link`는 로컬 추적을 설정하지 않는다. 먼저 원격 스택 번호나 PR URL과 함께
`gh stack checkout`을 사용해 브랜치를 가져오고 로컬에 설정한다
([명령][stack-cli]). 리베이스는 브랜치를 다시 쓰므로 사용자가 스택 업데이트를
요청할 때만 한다.

스택은 아래에서부터 머지된다. PR을 머지하면 그 아래의 머지되지 않은 PR도 모두 함께
머지되며, 중간 PR을 혼자 머지할 수는 없다. 따라서 스택된 PR 하나를 머지해 달라는
요청은 그 아래 PR까지 포함하므로 그 범위를 확인한다. 이후 GitHub는 다음 PR이 스택의
base를 대상으로 하도록 리베이스한다([머지][stack-merge]).

### 스택에서 이슈 닫기

GitHub는 PR이 기본 브랜치를 대상으로 할 때만 closing 키워드를 해석한다. 다른 base에서는
무시되고, 링크가 만들어지지 않으며, 머지해도 이슈에 영향이 없다
([이슈 연결][issues]). 스택에서는 맨 아래를 제외한 모든 PR이 다른 PR의 브랜치를 대상으로
하며, 기본이 아닌 trunk 위의 스택에는 기본 브랜치를 대상으로 하는 PR이 없다. 그런
곳에서는 키워드 없이 이슈를 참조한다. 기본 브랜치 위의 맨 아래 PR은 그 PR만으로 이슈가
완료된다면 키워드를 달 수 있다.

스택 문서는 PR이 스택 base로 대상이 바뀐 뒤에도 키워드가 효력을 갖는지 밝히지
않는다. 이슈를 완료하는 PR이 반영된 뒤 이슈를 확인한다. 아직 열려 있으면 보고하고,
사용자가 요청했다면 닫는다.

## AI 지원 레이블 붙이기

저장소의 AI 정책과 기존 레이블을 살펴본다. 지정된 레이블을 재사용하고, 없으면 알려진
AI 사용에 `ai-assisted`를 선호한다. 레이블은 도구의 지원을 설명할 뿐, 모든 내용이
생성되었다거나 사람이 검토했다는 주장이 아니다.

환경에서 요구하는 GitHub 도구를 사용한다. GitHub CLI라면 관련 없는 레이블을 덮어쓰지
않고 기존 레이블을 적용한다.

```sh
gh pr edit "$pr" --repo "$repo" --add-label "$label"
```

이에 해당하는 생성 플래그는 다른 생성 인자와 함께 쓰는
`gh pr create --draft --label "$label"`이다. 사용하기 전에 레이블이 존재하는지
확인한다. 존재하지 않으면 사용자나 저장소가 명시적으로 허가한 경우에만 만든다.

```sh
gh label create "$label" --repo "$repo" \
  --description "AI tools assisted in preparing this pull request." \
  --color 8250df
```

기존 레이블의 메타데이터를 덮어쓰려고 `--force`를 쓰지 않는다. 생성이나 적용이
불가능하거나 허가되지 않았다면, 공개가 끝났다고 조용히 주장하지 말고 없는 레이블이나
권한을 보고하고 메인테이너의 도움을 요청한다. 저장소가 요구하는 본문 공개를 우회하지
않는다. 게시 후 PR의 레이블을 확인하고 다른 레이블과 Draft 상태를 유지한다.

## 미디어 첨부하고 확인하기

업로드하기 전에 [UI 증거](ui-evidence.md)에 따라 미디어를 준비하고 확인한다.
`gh --version`과 해당 명령의 `--help`로 `--attach` 지원 여부를 확인한다. 기본
첨부 기능에는 대상 저장소에 대한 push 권한이 필요하다. CLI 지원이나 권한이 없으면
가능한 곳에서 허가된 브라우저 업로드를 사용하거나 차단 요인을 보고한다. 가짜 URL을
게시하거나 필요한 증거를 조용히 건너뛰지 않는다. 업로드가 되게 하려고 권한을 바꾸지
않는다.

다음 Markdown은 완성된 본문 파일에서의 배치를 정한다. 예시 경로와 캡션을 실제로 확인한
미디어로 바꾼다.

```markdown
## UI evidence

Before: the old error overlaps the submit button; the box marks the overlap.

![Marked overlap in the old form](./before-marked.png)

After: the error is below the field, leaving the button usable.

![Marked error placement in the updated form](./after-marked.png)

Interaction: submit invalid input, correct it, and submit again.

![](./form-flow.mp4)
```

참조한 파일을 정확히 그대로 첨부한다. 이미 Draft로 만든 PR의 경우:

```sh
gh pr edit "$pr" --body-file "$body_file" \
  --attach ./before-marked.png \
  --attach ./after-marked.png \
  --attach ./form-flow.mp4
```

세 예시를 모두 쓸 필요 없이 변경에 필요한 미디어만 고른다. `--body-file`은 본문을
교체한다. 편집하기 전에 기존 내용을 불러와 보존한다. 본문 플래그가 없으면
`gh pr edit --attach`는 기존 본문을 유지하고 미디어를 덧붙인다. 해당 작업이 적절하고
허가된 경우 첨부는 `gh pr create --draft`나 `gh pr comment`와 함께 쓸 수도 있다.

GitHub CLI는 로컬 미디어를 업로드하고 일치하는 Markdown 참조를 에셋 URL로 다시 쓴다.
참조되지 않은 파일은 덧붙여진다. 기존 Markdown 이미지의 대체 텍스트는 유지된다.
덧붙이는 이미지에는 `--attach './image.png#Description'`을 사용한다. 동영상에는 대체
텍스트가 없다. 동영상 참조는 인라인 링크가 아니라 플레이어로 렌더링되도록 자기만의
문단에 두고, 그 앞에 설명하는 캡션을 넣는다.

GitHub가 현재 지원하는 형식과 크기 제한을 따른다. 모든 로컬 파일을 업로드할 수 있다고
가정하지 않는다. URL을 얻으려고 증거를 Git에 커밋하지 않는다.

일부 첨부만 성공하면 명령이 0이 아닌 값으로 종료되더라도 생성이나 편집은 반영될 수
있다. 다시 시도하기 전에 반환된 PR과 성공한 에셋을 확인한다. 기존 PR을 업데이트하고
빠진 미디어만 첨부한다. 생성 명령을 무작정 반복해 중복 PR을 만들지 않는다.

렌더링된 PR을 열어 이미지 배치, 읽을 수 있는 주석, 캡션, 동영상 재생을 확인한다.
재생이나 시각적 확인이 불가능하면 증거가 확인되었다고 선언하지 말고 그 한계를
보고한다. 더 이상 필요 없는 로컬 경로 자리표시자를 제거하고, UI가 추가로 바뀌면
증거를 동기화한다.

## 머지 메시지

squash가 GitHub이 PR 제목이나 본문을 사용한다는 것을 보장하지는 않는다. 기본 메시지는
저장소 설정과, 경우에 따라 커밋 수에 달려 있다. PR 본문은 Markdown과 미디어를 쓸 수
있으며 커밋 본문과 글자 그대로 같을 필요는 없다. 머지를 준비할 때는
[writing-commits](../../writing-commits/SKILL.md)로 최종 완성 커밋 메시지를 확인하고
검증하며, 중요한 근거, 호환성을 깨는 변경의 세부 사항, 귀속을 보존한다. PR을 쓰거나
열어 달라는 요청만으로 머지하지 않는다.

## 설계 출처

Google은 필수 PR 템플릿이 아니라 내용과 변경 크기에 대한 원칙을 제공한다.

- [좋은 CL 설명 쓰기][descriptions]: what, why, 결정 맥락, 단점, 관련 있을 때의
  benchmark 결과, 정보를 담은 제목, 설명을 최신으로 유지하기. "Fix bug"는 정보가
  부족한 예로 든다.
- [작은 CL][small]: 일관된 변경, 관련 테스트, 안전한 점진적 작업.
- [코드 리뷰에서 살펴볼 것][review]: 설계, 기능, 코드만 읽어서는 부족할 때 쓸모 있는
  증거.

다른 가이드도 증거에 관해 같은 원칙을 둔다.

- [Linux 커널: 패치 제출][kernel]: 한 줄 수정이라도 문제를 설명하고, 패치 하나에
  문제 하나만 풀고, 성능이나 크기 개선 주장에는 수치와 trade-off를 붙인다.
- [Rust의 LLM 기여 지침][rust]: CI가 어차피 돌리는 테스트는 보고하지 않고, 수동
  테스트와 benchmark, 아직 확실하지 않은 점은 보고한다.
- PR 템플릿이 없는 프로젝트의 [oxc #27816][oxc-example]: before/after 코드와 바뀌지
  않는 것을 담은 요약, 이어서 측정 방법, 환경, 결과를 담은 benchmark.

프로젝트는 자유 형식 설명과 필수 템플릿으로 나뉜다. [React의 템플릿][react]은
요약과 "How did you test this change?" 섹션을 요구하고, 이 섹션을 비우면 PR이 닫힐
가능성이 높다고 경고한다. 그래서 저장소 템플릿이 이 원칙보다 우선한다. 고정 구성이
없는 자유 형식 본문, AI 공개, Draft 기본값은 이 플러그인의 선택이며,
[LLVM의 사람 책임 정책][llvm]도 비교할 만하다. 다른 프로젝트의 제한이 여기서
보편적인 요건이 되지는 않는다.

## 참고 자료

- [GitHub CLI 첨부][attachments]: 권한, 배치, 동영상.
- [gh pr create][create]와 [gh pr edit][edit]: 플래그와 부분 성공.
- [저장소 템플릿][templates]과 [상속되는 기본값][defaults].
- [squash 메시지 설정][squash]: 제목과 본문이 항상 쓰이는 것은 아니다.
- [이슈 연결][issues]: closing 키워드는 기본 브랜치 PR에만 적용된다.
- [스택 풀 리퀘스트][stacks]: 같은 저장소, 선형 이력, trunk.
- 스택의 [만들기][stack-create], [관리][stack-manage], [머지][stack-merge]:
  웹사이트와 CLI 경로, 리베이스, 아래에서 위로의 머지.
- [스택 CLI 명령][stack-cli]과 [기타 도구][stack-other]: `submit`, `link`, draft와
  ready 기본값.

[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
[create]: https://cli.github.com/manual/gh_pr_create
[edit]: https://cli.github.com/manual/gh_pr_edit
[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[squash]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[stack-create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[stack-manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[stack-merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[stack-cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[stack-other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
[descriptions]: https://google.github.io/eng-practices/review/developer/cl-descriptions.html
[small]: https://google.github.io/eng-practices/review/developer/small-cls.html
[review]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[react]: https://github.com/facebook/react/blob/main/.github/PULL_REQUEST_TEMPLATE.md
[rust]: https://rustc-dev-guide.rust-lang.org/llm-guidance/writing.html
[llvm]: https://llvm.org/docs/AIToolPolicy.html
[kernel]: https://docs.kernel.org/process/submitting-patches.html
[oxc-example]: https://github.com/oxc-project/oxc/pull/27816
