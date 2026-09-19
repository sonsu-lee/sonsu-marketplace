# Screen patterns

화면 이름이 아니라 primary decision과 작업 단위로 패턴을 선택한다. 한 화면에 모든 패턴을 넣지 않는다.

## Operations Dashboard

여러 운영 영역에서 지금 주의할 곳을 고른다. summary card는 해당 상태로 이동하거나 필터를 적용해야 하며, 행동과 연결되지 않는 숫자는 보조 KPI로 표시한다.

## List Workspace

많은 엔터티를 검색, 필터, 정렬, 선택하고 처리한다. status summary, filter bar, batch action, table, detail drawer 또는 detail route의 관계를 유지한다.

## Detail Workspace

한 엔터티의 현재 상태, 이력, 관련 객체와 가능한 행동을 판단한다. summary와 timeline을 분리하고 위험 행동은 권한, 영향, confirmation을 갖는다.

## Queue / Inbox

우선순위 또는 SLA에 따라 다음 작업을 선택한다. unread보다 actionability, ownership, due state와 exception reason을 강조한다.

## Exception Center

정상 흐름에서 벗어난 항목을 원인과 해결 가능성으로 묶는다. severity만 보여주지 말고 owner, next action, blocking dependency와 resolution state를 제공한다.

## Form Workflow

운영 객체를 생성하거나 단계적으로 수정한다. 단순 필드는 한 화면, 의존성·검토·위험이 큰 작업은 step flow를 사용한다. validation은 발생 지점 가까이에 둔다.

## Settings

영향 범위, 권한과 적용 시점을 먼저 보여준다. save 결과, unsaved state, inherited/default value와 rollback 가능성을 명확히 한다.

## Map / Control Tower

위치와 경로가 primary decision일 때만 선택한다. map과 list selection을 양방향으로 연결하고, dark content surface는 지도 가독성에 필요한 범위에만 사용한다.

## 조합 규칙

상위 shell에는 primary pattern 하나만 둔다. dashboard에서 list로 drill down하거나 list에서 detail drawer를 여는 식으로 패턴 간 전이를 설계한다. 모든 전이는 Design Decision Contract의 task scenario ID를 가져야 한다.
