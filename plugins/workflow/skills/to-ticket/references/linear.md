# Linear 게시 규칙

Linear용 payload를 작성하거나 게시하라는 요청이 있을 때만 읽는다.

## 대상과 필드를 확인한다

- 연결된 workspace와 필수 team을 확인한다.
- 제목과 Markdown description을 준비한다.
- project, cycle, state, priority, estimate, assignee, delegate, label, milestone과 due date는 사용자 요청이나 workspace 근거가 있을 때만 사용한다.
- parent, `blockedBy`, `blocks`, `relatedTo`와 release는 사용자가 요청하고 현재 도구가 지원할 때만 사용한다.

team과 제목 이외의 값을 추정하지 않는다. 이름을 ID로 해석해야 하면 현재 workspace에서 정확히 조회한다. priority 숫자, state와 estimate 체계는 현재 tool schema와 team 설정을 확인하지 않고 만들지 않는다.

## 현재 interface에 맞춘다

Linear MCP의 현재 tool schema를 먼저 확인한다. Codex connector에서 일반적인 생성 도구는 `save_issue`이며, 새 티켓에는 `team`과 `title`을 사용하고 `description`, `project`, `cycle`, `state`, `priority`, `estimate`, `assignee`, `labels`, `milestone`, `parentId`, `blockedBy`, `blocks`, `relatedTo` 등을 선택적으로 받을 수 있다. 실제 이름과 인자는 connector 버전에 따라 달라질 수 있으므로 이 목록만 믿고 호출하지 않는다.

필요한 값만 `list_teams`, `list_issue_statuses`, `list_issue_labels`, project·cycle 조회 도구로 확인한다. 유사 티켓은 `list_issues`나 검색 도구에서 team, 제목, 설명과 범위를 함께 비교한다. 여러 workspace를 추정하여 전환하거나 새 인증 context를 만들지 않는다.

## 게시하고 검증한다

1. workspace 연결, team과 선택 metadata를 읽는다.
2. 최종 제목, description과 지원되는 metadata를 확정한다.
3. 관계를 제외한 티켓을 생성하여 `client_key`와 원격 ID를 매핑한다.
4. 모든 대상 티켓이 존재하는 것을 확인한 뒤 parent와 dependency 관계를 연결한다.
5. 각 ID를 관계 포함 옵션으로 다시 읽어 URL, 제목, team, state, metadata와 관계를 확인한다.

인증이 만료되었거나 연결되지 않았으면 로그인이나 계정 전환을 자동으로 수행하지 않는다. 생성 응답이 불명확하면 같은 payload를 반복하지 말고 먼저 제목, 설명과 team으로 검색한다.

공식 interface 참고: [Linear MCP server](https://linear.app/docs/mcp), [Linear issue 생성 규칙](https://linear.app/docs/creating-issues)
