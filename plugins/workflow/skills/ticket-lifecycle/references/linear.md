# Linear issue lifecycle

기존 Linear issue의 status, assignee 또는 relation을 변경할 때 읽는다.

## workspace 상태를 기준으로 매핑한다

- 정확한 workspace, team과 issue ID·identifier·URL을 읽는다.
- team의 현재 issue status와 type을 조회한다. `start`, `review`, `ready`, `complete`, `reopen`과 `cancel`을 고정된 status 이름이나 priority 숫자로 바꾸지 않는다.
- 이미 Started 계열 type이면 `start`는 `no-op`이다. Completed·Canceled 계열은 명시적인 `reopen`과 유효한 target status 없이 되돌리지 않는다.
- 사용자 지정이나 확인된 auto-assign 정책이 있을 때만 assignee를 바꾸고, 실제 workspace member ID를 조회한다. 해제할 때에도 현재 assignee를 target으로 보존하며, 사용자 지정 대상과 일치하거나 모든 담당자 해제 의도가 명시된 경우에만 assignee field를 비운다.

## native relation을 우선한다

`blockedBy`, `blocks`, `relatedTo`와 native duplicate operation은 현재 Linear interface가 노출하는 정확한 방향으로 적용한다. duplicate는 중복 issue를 canonical issue에 병합하고 중복 issue를 예약된 Duplicate status로 옮기는 하나의 operation이므로, 반대 방향으로 실행하거나 별도 status transition을 중복 적용하지 않는다. 주 issue와 target issue를 각각 조회하고, 이미 존재하거나 제거된 relation은 `no-op`으로 기록한다. Waiting 또는 Blocked status를 relation과 함께 바꾸려면 team에 별도 status 정책과 허용된 mapping이 있어야 한다.

Linear GitHub integration의 drafted, opened, review requested, ready for merge와 merged automation이 해당 repository에 구성되어 있으면 같은 status를 직접 전이하지 않는다. automation 부재 또는 해당 event 비적용과 direct fallback 조건이 전부 확인되지 않으면 `unknown`으로 남긴다.

## mutation 후 다시 읽는다

현재 MCP 또는 API schema를 확인하고 지원되는 update·relation operation만 한 번 실행한다. 매 operation 뒤 relation 포함 issue를 다시 읽어 status, assignee와 relation을 검증한다. 인증 만료, workspace 전환 필요와 권한 부족이 있으면 로그인·전환·권한 확대 없이 해당 operation을 중단한다.

공식 참고: [Linear issue status](https://linear.app/docs/configuring-workflows), [Linear issue relation](https://linear.app/docs/issue-relations), [Linear GitHub integration](https://linear.app/docs/github)
