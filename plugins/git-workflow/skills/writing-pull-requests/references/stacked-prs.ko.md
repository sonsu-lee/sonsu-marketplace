# 스택 풀 리퀘스트

> 영문 정본: [stacked-prs.md](stacked-prs.md) (`fed67c3` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

스택은 같은 저장소의 머지되지 않은 PR에 의존하는 PR에만 사용한다. 지원되는 스택은
단일 선형 체인이다. 각 브랜치는 아래 브랜치를 포함하고 각 PR은 그 브랜치를
대상으로 하며, 맨 아래 PR은 사용자의 대상이나 프로젝트 대상을, 없으면 기본
브랜치를 대상으로 한다. 포크의 head는 포함할 수 없다. 호스트나 저장소가 스택을
지원하지 않거나 제약을 충족하지 못하면 trunk를 대상으로 하고 본문에 의존 관계와
머지 순서를 명시한다.

각 PR을 [게시 절차](publishing.md)에 따라 만든 뒤 지원되는 스택 도구로 체인을
연결한다. GitHub 웹사이트에서는 스택을 만들거나 base가 연결된 기존 PR을 연결할 수
있다. 선택 사항인 `gh stack` 확장으로 브랜치나 PR을 아래에서 위 순서로 연결할 수
있으며 의도한 trunk를 명시해야 한다. 연결 과정에서 브랜치가 push되거나 PR base가
바뀔 수 있다. 기존 스택을 확장할 때는 기존 trunk가 유지된다.

스택 도구는 상태를 바꿀 수 있다. 확장의 `submit` 편집기는 새 PR을 기본적으로 ready로
만들며 `submit`이나 `link`의 `--open`은 PR을 ready로 바꾼다. 작업 후 각 PR의 base,
제목, 본문, Draft 상태를 확인하고 의도한 상태로 되돌린다.

rebase는 브랜치 이력을 다시 쓴다. 사용자가 스택 업데이트를 요청한 경우에만 rebase한다.
웹사이트에서 만들거나 연결한 스택은 로컬 추적이 자동으로 설정되지 않는다. 로컬 스택
rebase 명령을 쓰기 전에 원격 스택을 checkout한다.

## 머지와 이슈 닫기

스택은 아래에서 위로 머지된다. PR을 머지하면 그 아래의 머지되지 않은 모든 PR도 함께
머지된다. 중간 PR을 머지하기 전에 이 범위를 확인한다. 이후 GitHub는 다음 PR의
대상을 스택 base로 바꾼다.

스택에서 맨 아래를 제외한 PR은 모두 다른 PR의 브랜치를 대상으로 하므로, GitHub는
그 PR의 닫기 키워드를 처리하지 않는다([이슈 닫기](publishing.md#edge-cases)).
스택 문서는 그런 PR이 스택 base로 대상이 바뀐 뒤에도 키워드가 효력을 갖는지
밝히지 않는다. 이슈를 완료하는 PR이 반영된 뒤 이슈를 확인한다.

## 참고 자료

- [스택 제약][stacks], 스택 [생성][create], [관리][manage], [머지][merge].
- [스택 CLI 명령][cli]과 [다른 도구][other].
- [PR과 이슈 연결][issues].

[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
