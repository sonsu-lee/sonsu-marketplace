# 스택 풀 리퀘스트

> 영문 정본: [stacked-prs.md](stacked-prs.md) (`PENDING` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

같은 저장소의 미병합 PR에 의존하는 PR만 스택으로 쌓는다. 각 브랜치는 아래
브랜치를 포함하고 각 PR은 그 브랜치를 대상으로 하며, 맨 아래 PR은 trunk를
대상으로 한다. 포크는 스택에 넣을 수 없다. 스택을 지원하지 않으면 trunk를
대상으로 하고 본문에 의존 관계와 머지 순서를 적는다.

1. 각 PR을 [게시 절차](publishing.md)로 만든다.
2. GitHub 웹사이트나 선택 사항인 `gh stack` 확장으로 체인을 연결하고 trunk를
   명시한다.
3. 각 PR의 base, 제목, 본문, Draft 상태를 확인하고 도구가 바꾼 것을 되돌린다.

## 주의할 점

- `gh stack submit`은 새 PR을 기본적으로 ready로 열고, `submit`이나 `link`의
  `--open`은 PR을 ready로 바꾼다.
- 연결하면서 브랜치가 push되거나 PR base가 바뀔 수 있다.
- rebase는 브랜치를 다시 쓴다. 사용자가 요청할 때만 스택을 rebase한다. 웹사이트에서
  만든 스택은 checkout하기 전까지 로컬 추적이 없다.
- PR을 머지하면 그 아래의 미병합 PR도 모두 머지된다. 중간 PR을 머지하기 전에 이
  범위를 확인한다.
- 맨 아래 위의 PR은 다른 PR의 브랜치를 대상으로 하므로 GitHub가 closing 키워드를
  무시한다([이슈 닫기](publishing.md#edge-cases)). 완료하는 PR이 반영된 뒤 이슈를
  확인한다.

## 참고 자료

- [스택 제약][stacks], 스택 [생성][create], [관리][manage], [머지][merge].
- [스택 CLI 명령][cli]과 [다른 도구][other].

[stacks]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
[create]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests
[manage]: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests
[merge]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
[cli]: https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands
[other]: https://docs.github.com/en/pull-requests/reference/use-other-tools-with-stacked-pull-requests
