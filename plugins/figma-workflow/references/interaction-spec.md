# Product interaction specification

## Figma interaction contract

PRD나 요구사항에서 새 flow를 시작하면 사용자 목표별로 진입점, 필요한 화면·상태, 접근 가능한 역할과 다음 행동을
대응시킨다. 기존 flow를 수정할 때에는 이 대응을 현재 starting point와 destination에서 확인한다. 이미 합의된
권한·제품 규칙을 재사용하고, 빠진 결정이 실제로 바꾸는 경로만 확인 대상으로 남긴다. 예를 들어 조회만 가능한
사용자는 목록에서 상세를 보고 돌아올 수 있지만 편집 action은 해당 권한 조건에 따라 달라진다. 메뉴에서 숨겼다는
사실만으로 직접 진입의 권한 처리까지 정의됐다고 보지 않는다. 이 대응은 아래 transition과 named state에 담으며
별도의 문서나 FigJam 작성 단계를 필수로 추가하지 않는다.

의미 있는 transition마다 다음 세 evidence layer를 동기화한다.

1. actual control의 executable reaction: trigger, action, destination/result, transition, condition
2. concise native annotation: `Trigger → Result [Condition]`
3. 한 user goal과 named flow starting point로 조직한 state frame

중요 transition에는 `Trigger`, `Action`, `Destination or next state`, `Condition`, `Visible result`, `Back or
close behavior`, `Edge case`를 기록한다. happy path는 left-to-right, error/alternative branch는 원인이 되는
state 가까이에 둔다. reusable local state는 component variant 또는 variable, screen-level empty/populated,
submit/loading/success/error/permission 결과는 별도 frame으로 표현한다.

primary action, visible loading/submission, success, meaningful error, cancel/back와 recovery를 다룬다. overlay
modal/drawer/popover/menu에는 dismissal·close와 Back behavior를 명시한다. fixed/sticky/scroll/overflow behavior도
visual state와 prototype에서 유지한다. arrow나 annotation은 documentation이지 clickable prototype의 pass 근거가
아니다.

official Figma MCP가 current schema에서 reaction write/readback capability를 제공할 때만 actual control의
native reaction을 작업한다. tool 전 required prerequisite가 설치되어 있으면 그 contract를 먼저 따른다.
예를 들어 schema가 Plugin API를 제공하고 `setReactionsAsync`를 지원할 때 navigation reaction은 trigger와
non-empty `actions`를 가진다.

```js
await control.setReactionsAsync([
  {
    trigger: { type: "ON_CLICK" },
    actions: [{ type: "NODE", navigation: "NAVIGATE", destinationId, transition: null }],
  },
]);
```

이 예시는 current schema가 다르면 적용하지 않는다. readback에서는 trigger type, action type, navigation과
destination ID를 각각 확인한다. overlay는 `OVERLAY`, component state는 적절할 때 `CHANGE_TO`, return/close는
`BACK`/`CLOSE`를 사용한다. existing convention이 없으면 motion timing을 임의로 채우지 않는다.

named starting point에서 primary·failure·recovery path playback, resolvable destination, orphan state, dead end,
닫히지 않는 overlay와 wrong Back을 검토한다. screenshot은 visible state, reaction readback은 graph를 증명하므로
둘을 함께 보고한다. playback이 unavailable이면 `not_run`, 전체 clickable claim은 `inconclusive`다.

수동 companion의 `audit-prototype-links`는 selection 내 empty action과 missing destination evidence만 보고한다.
reaction write, UX 판단, overlay behavior 검증을 대신하지 않으며 schema와 failure boundary는
[deterministic execution](deterministic-execution.md)을 따른다.
