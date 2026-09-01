# Jira 게시 규칙

Jira용 payload를 작성하거나 게시하라는 요청이 있을 때만 읽는다.

## 대상과 schema를 확인한다

- 정확한 site 또는 `cloudId`, project key와 issue type을 확인한다.
- summary와 description을 준비한다.
- assignee, parent, label, priority, component, fix version, sprint와 custom field는 사용자 요청이나 project 근거가 있을 때만 사용한다.
- dependency 등 issue link는 현재 site가 지원하는 정확한 link type을 조회한다.

Jira의 생성 가능 field는 project와 issue type마다 다르다. project의 issue type 목록과 create-field metadata를 먼저 읽고 실제로 지원되는 필드와 필수값만 보낸다. 사용자에게 보이는 이름을 임의의 account ID, option ID, custom field ID 또는 transition ID로 바꾸지 않는다.

## 현재 interface에 맞춘다

Atlassian MCP의 현재 tool schema를 먼저 확인한다. Rovo MCP v2는 도구를 지연 공개할 수 있으므로 필요한 경우 `discover`로 검색하고 해당 read·write 실행 interface를 사용한다. 공식 v2 명칭과 일부 connector의 직접 노출 명칭은 `list...`와 `get...`처럼 다를 수 있다. 일반적인 흐름은 다음 기능에 해당하는 현재 도구를 사용한다.

- site 탐색: `getAccessibleAtlassianResources`
- issue type과 필드: `listJiraProjectIssueTypesMetadata` 또는 `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`
- 중복 검색: `searchJiraIssuesUsingJql`
- 생성과 검증: `createJiraIssue`, `getJiraIssue`
- 관계: `listJiraIssueLinkTypes` 또는 `getIssueLinkTypes`, `createJiraIssueLink` 또는 `createIssueLink`

connector가 `description`에 Markdown을 받더라도 직접 REST API를 사용할 때에는 multi-line rich text field가 Atlassian Document Format을 요구할 수 있다. 항상 실제 tool 또는 endpoint schema를 따른다. 상태 transition과 sprint 배치는 생성과 별도 작업이며 명시적인 요청이 있을 때만 수행한다.

## 게시하고 검증한다

1. 연결된 site와 `cloudId`, project와 issue type을 확인한다.
2. create-field metadata와 같은 목적의 기존 issue를 조회한다.
3. 최종 summary, description과 지원되는 field payload를 확정한다.
4. parent와 무관한 티켓을 먼저 생성하여 `client_key`와 원격 key를 매핑한다.
5. subtask처럼 생성 시 parent가 필요한 티켓은 확인된 parent key를 생성 payload에 넣는다. 모든 대상 티켓이 존재한 뒤 나머지 승인된 issue link를 연결한다.
6. key로 티켓을 다시 읽어 URL, summary, status, 실제 field와 관계를 확인한다.

필수 field를 확인할 수 없거나 연결되지 않았으면 게시하지 않는다. 일부 생성 결과가 불명확하면 같은 payload를 반복하지 말고 JQL이나 정확한 key 조회로 실제 상태를 먼저 확인한다.

공식 interface 참고: [Atlassian Rovo MCP supported tools](https://support.atlassian.com/atlassian-ai-gateway/docs/supported-tools/), [Jira Cloud issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)
