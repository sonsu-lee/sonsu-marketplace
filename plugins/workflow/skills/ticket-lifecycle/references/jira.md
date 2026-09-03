# Jira work item lifecycle

기존 Jira work item의 transition, assignee 또는 issue link를 변경할 때 읽는다. 현재 site가 이전 용어를 사용하면 issue·project·issue type을 그대로 보존한다.

## 현재 workflow를 조회한다

- 정확한 site 또는 `cloudId`, project key, work item key와 URL을 읽는다.
- 현재 status와 available transition을 조회한다. status field edit로 전이를 흉내 내거나 transition 이름·ID를 추정하지 않는다.
- `start`, `review`, `ready`, `complete`, `reopen`과 `cancel`은 site workflow에 실제 대응 transition이 있을 때만 매핑한다.
- assignee 변경에는 현재 interface가 요구하는 account ID와 assignable user 여부를 확인한다. 해제할 때에도 현재 assignee를 target으로 보존하며, 사용자 지정 대상과 일치하거나 모든 담당자 해제 의도가 명시된 경우에만 assignee field를 비운다.

## issue link의 방향을 보존한다

현재 site의 issue link type, inward·outward description과 양쪽 work item을 조회한다. `blocked by`, `blocks`, `related`와 `duplicate`를 이름이 비슷한 link type에 임의로 매핑하지 않는다. 제거할 때에는 정확한 기존 link ID 또는 current interface가 요구하는 식별자를 확인한다. Waiting·Blocked status 전이는 link와 별도 operation이다.

연결된 source control의 branch created, pull request created·declined·merged, deployment와 release automation이 확인되면 해당 event의 status effect를 직접 중복 실행하지 않는다. key가 branch·commit·PR title에 있다는 사실만으로 automation 성공이나 completion을 주장하지 않는다.

## mutation 후 다시 읽는다

Atlassian MCP가 도구를 지연 공개하면 필요한 transition, assign, issue-link와 get 기능을 현재 discovery interface에서 찾는다. 각 operation을 한 번 적용하고 work item을 다시 읽어 status, assignee와 issue link를 확인한다. transition 성공과 issue-link 성공을 따로 기록하고, 불명확한 응답은 반복하지 않는다. 연결되지 않은 site, 권한 부족과 unsupported transition/link는 구분해 보고한다.

공식 참고: [Jira issue transition API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-post), [Jira issue link API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/), [Jira automation trigger](https://support.atlassian.com/cloud-automation/docs/jira-automation-triggers/), [Jira workflow trigger](https://support.atlassian.com/jira-cloud-administration/docs/understand-workflow-triggers/)
