# Jira 게시 규칙

Jira용 payload를 작성하거나 게시하라는 요청이 있을 때만 읽는다.

Jira Cloud의 현재 UI 문서에서는 `work item`, `work type`, `space`, `Title`을 사용하지만 REST API, JQL과 이전 UI에서는 `issue`, `issue type`, `project`, `summary`가 계속 나타날 수 있다. 사용자에게 보이는 설명은 대상 site의 용어를 따르고 tool payload는 실제 schema의 field 이름을 그대로 사용한다.

## 대상과 schema를 확인한다

- 정확한 site 또는 `cloudId`, space의 project key와 work type(`issue type`)을 확인한다.
- summary와 description을 준비한다.
- assignee, parent, label, priority, component, fix version, sprint, due date와 custom field는 사용자 요청이나 project 근거가 있을 때만 사용한다.
- dependency 등 issue link는 현재 site가 지원하는 정확한 link type을 조회한다.

Jira의 생성 가능 field는 project와 issue type마다 다르다. project의 issue type 목록과 create-field metadata를 먼저 읽고 실제로 지원되는 필드와 필수값만 보낸다. 사용자에게 보이는 이름을 임의의 account ID, option ID, custom field ID 또는 transition ID로 바꾸지 않는다.

중립 `kind`는 실제 work type과 space 관례에 맞춰 매핑한다. `defect`는 보통 `Bug`, 사용자 결과를 제공하는 `delivery`는 `Story` 또는 `Task`, `maintenance`는 `Task`와 대응할 수 있다. `investigation`은 확인된 custom work type이 없으면 `Task`와 label 등 기존 관례를 사용할 수 있지만 근거 없이 type이나 field를 만들지 않는다.

Jira의 실제 work type은 hierarchy level에 배치된다. 예를 들어 `Epic`은 상위 level에, `Story`, `Task`, `Bug` 등은 standard level에, `Subtask`는 하위 level에 있을 수 있지만 site 설정이 우선한다. `standard work item` 같은 level 명칭을 실제 work type으로 만들거나 중립 `kind`와 자동으로 동일시하지 않는다. Jira Service Management의 customer-facing request type도 내부 work type과 별개이므로 대상이 service space일 때 실제 request type과 연결 관계를 따로 확인한다.

## 현재 interface에 맞춘다

Atlassian MCP의 현재 tool schema를 먼저 확인한다. Rovo MCP v2는 도구를 지연 공개할 수 있으므로 필요한 경우 `discover`로 검색하고 해당 read·write 실행 interface를 사용한다. 공식 v2 명칭과 일부 connector의 직접 노출 명칭은 `list...`와 `get...`처럼 다를 수 있다. 일반적인 흐름은 다음 기능에 해당하는 현재 도구를 사용한다.

- site 탐색: `getAccessibleAtlassianResources`
- issue type과 필드: `listJiraProjectIssueTypesMetadata` 또는 `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`
- 중복 검색: `searchJiraIssuesUsingJql`
- 생성과 검증: `createJiraIssue`, `getJiraIssue`
- 관계: `listJiraIssueLinkTypes` 또는 `getIssueLinkTypes`, `createJiraIssueLink` 또는 `createIssueLink`

connector가 `description`에 Markdown을 받더라도 직접 REST API를 사용할 때에는 multi-line rich text field가 Atlassian Document Format을 요구할 수 있다. 항상 실제 tool 또는 endpoint schema를 따른다. 생성만 요청받으면 workflow의 초기 status를 유지한다. 상태 transition과 sprint 배치는 생성과 별도 작업이며 명시적인 요청이 있을 때만 수행한다.

## 게시하고 검증한다

1. 연결된 site와 `cloudId`, project와 issue type을 확인한다.
2. create-field metadata와 같은 목적의 기존 issue를 조회한다.
3. 최종 summary, description과 지원되는 field payload를 확정한다.
4. parent와 무관한 단일 티켓은 한 번 생성하고 반환된 원격 key를 기록한다. 여러 티켓 또는 hierarchy·relation 매핑이 있으면 parent와 무관한 대상을 한 번씩 생성하여 `client_key`와 원격 key를 매핑한다.
5. subtask처럼 생성 시 parent가 필요한 티켓은 확인된 parent key를 생성 payload에 넣는다. 모든 대상 티켓이 존재한 뒤 나머지 승인된 issue link를 연결한다.
6. 생성 payload에 포함되지 않은 metadata와 issue link를 하나씩 적용하고 매번 key로 티켓을 다시 읽어 URL, summary, status, 실제 field와 관계를 확인한다.

필수 field를 확인할 수 없거나 연결되지 않았으면 게시하지 않는다. 생성 결과가 불명확하면 같은 payload를 반복하지 말고 JQL이나 정확한 key 조회로 실제 상태를 먼저 확인하며, 확인되지 않으면 `unknown`으로 남긴다. 후속 operation은 재조회에서 미적용이 확인된 경우에만 재시도한다.

공식 interface와 개념 참고: [Atlassian Rovo MCP supported tools](https://support.atlassian.com/atlassian-ai-gateway/docs/supported-tools/), [Jira Cloud issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/), [Jira work types](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/), [Jira work item 생성](https://support.atlassian.com/jira-software-cloud/docs/create-a-work-item-and-a-subtask/), [Jira Service Management request type과 work type](https://support.atlassian.com/jira-service-management-cloud/docs/whats-the-difference-between-request-types-and-issue-types/)
