# GitHub Issue lifecycle

기존 GitHub Issue의 state, Project status, assignee 또는 relation을 변경할 때 읽는다.

## 대상과 표현을 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY#NUMBER`, URL과 open·closed state를 읽는다.
- `start`, `review`와 `ready`는 GitHub Issue state가 아니다. 실제 GitHub Project의 Status field나 repository automation에 대응값이 확인된 경우에만 사용한다.
- `complete`, `reopen`과 `cancel`도 현재 CLI·API가 지원하는 state·reason과 repository 정책을 확인한다. close와 Project Status를 같은 결과로 간주하지 않는다.
- GitHub Issue는 여러 assignee를 가질 수 있다. 특정 담당자를 해제할 때에는 현재 assignee에서 검증한 login 또는 ID를 target으로 사용하고 다른 담당자는 유지한다. `all`은 사용자가 모든 담당자 해제를 명시한 경우에만 현재 assignee 전체를 조회해 적용한다. 대상 또는 전체 해제 의도가 모호하면 mutation하지 않는다.

## 현재 interface만 사용한다

전용 GitHub MCP가 있으면 현재 schema를 먼저 확인한다. CLI를 사용하면 실행 시점의 `gh issue view`, `gh issue edit`, `gh issue close`, `gh issue reopen`과 필요한 `gh project` 도움말을 읽는다. 존재하지 않는 flag나 GraphQL mutation을 추정하지 않는다.

Project Status를 바꿀 때에는 대상 project item, Status field ID와 option ID를 모두 조회한다. 필요한 project scope가 없으면 `gh auth refresh`나 권한 확대를 실행하지 않고 해당 operation만 `unapplied`로 보고한다.

blocked-by·blocks는 현재 interface가 existing issue dependency를 구조적으로 지원할 때만 적용한다. `related`와 `duplicate`가 구조화된 relation으로 노출되지 않으면 지원된 것처럼 body나 comment를 자동 수정하지 않는다. PR closing keyword와 Development sidebar 연결은 PR 작성 책임이며 여기에서 만들지 않는다.

## mutation 후 다시 읽는다

각 state, Project field, assignee와 relation 변경 뒤 issue와 필요한 project item을 다시 읽는다. 특정 assignee 해제 뒤에는 그 사용자만 제거되고 나머지 assignee가 유지됐는지 확인한다. 이미 같은 state·option·assignee·relation이면 `no-op`이다. Issue state만 바뀌고 Project Status가 실패한 경우처럼 부분 결과를 분리하고, 확인 불가 응답을 반복하지 않는다.

공식 참고: [GitHub issue 관리](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues), [GitHub Projects field 변경](https://cli.github.com/manual/gh_project_item-edit), [GitHub PR과 issue 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
