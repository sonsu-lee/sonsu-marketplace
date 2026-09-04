# Deterministic execution boundary

## 실행 방식 선택

| 작업 성격 | 실행 경로 | writer와 경계 |
| --- | --- | --- |
| 문맥 판단이 필요한 Figma 구조·화면·reaction read/write | registered official Figma MCP | official MCP가 유일한 agent writer이며 current schema와 required prerequisite를 따른다 |
| explicit target과 unchanged area가 있는 작은 native 작업 | official MCP 안의 bounded code | 같은 official writer가 pre-read와 readback을 수행한다 |
| 반복적이고 결과가 명확한 allowlisted JSON 작업 | 사용자가 Figma Desktop에서 수동 실행하는 companion | agent-callable bridge가 아니며 arbitrary JavaScript를 실행하지 않는다 |

제품 화면, state, overlay와 interaction은 Figma Design에서 완결한다. FigJam은 탐색·워크숍, draw.io는
AWS·시스템 구조도에 사용한다. raw MCP 설치, 로컬 bridge, second writer 또는 companion으로 판단형
canvas 작업을 우회하는 경로는 없다.

official Figma tool 전에 required skill prerequisite가 설치되어 있으면 반드시 그 현재 계약을 따른다.
설치되지 않았거나 tool surface가 확인되지 않으면 API 이름을 발명하지 않고 `not_run`, `blocked` 또는
`inconclusive`를 보고한다.

## Companion operation plan

companion의 실제 package, build/import 경로와 host boundary는
[figma-plugin README](../figma-plugin/README.md) 및
[manifest](../figma-plugin/manifest.json)에 있다. UI는 version `1`의 strict JSON allowlist만 받으며 unknown
field, unknown operation, malformed JSON을 거부한다. network, storage, document persistence와 arbitrary
JavaScript evaluation은 하지 않는다.

```text
ReadOnlyPlan = {
  version: 1,
  mode: "preview",
  operation: "inspect-selection" | "audit-auto-layout" | "audit-prototype-links",
  scope: { kind: "selection" }
}

RenamePlan = {
  version: 1,
  mode: "preview" | "apply",
  operation: "rename-exact",
  targets: [{ nodeId, expectedName, newName }]
}

IconSwapPlan = {
  version: 1,
  mode: "preview" | "apply",
  operation: "replace-icon-instance-exact",
  targets: [{ nodeId, expectedMainComponentKey, replacementComponentKey }]
}
```

모든 문자열은 trim 뒤 비어 있으면 안 되고 targets는 비어 있거나 duplicate `nodeId`를 가질 수 없다.
`expectedName`/`newName`, `expectedMainComponentKey`/`replacementComponentKey`는 서로 달라야 한다. Read-only
operation은 current selection만 읽고 mutation target은 selection에서 추론하지 않는 explicit `nodeId`다.

## Preview, apply와 readback

mutation은 먼저 `mode: "preview"`로 exact target을 읽는다. 각 target은 `READY`, `MISSING_NODE`,
`WRONG_NODE_TYPE`, `STALE_EXPECTED_STATE`, `ALREADY_DESIRED` 또는 `LOOKUP_FAILED`로 분류된다. 독립 target의
lookup failure는 이후 target을 중단시키지 않는다.

preview receipt는 UI memory에만 존재하며 canonical fingerprint, exact target payload와 ID, observed expected
field, target별 disposition을 묶는다. 입력 변경이나 plugin 종료는 receipt를 폐기한다. Apply는 같은 intent를
`apply`로 정규화한 경우에만 receipt를 사용할 수 있다. receipt가 없으면 `PREVIEW_REQUIRED`, intent가 다르면
`PLAN_CHANGED`, preview에서 `READY`가 아닌 target이면 `PREVIEW_NOT_READY`이며 mutation하지 않는다.

`READY` target은 apply 직전에 다시 읽어 expected state를 확인하고 allowlisted mutation만 수행한 뒤 즉시
readback한다. 그 결과는 `applied`, skip 또는 failure로 target별 보고한다. earlier success를 rollback하지
않고 independent later target도 계속 처리한다. `IMPORT_FAILED`, `MUTATION_FAILED`, `READBACK_FAILED`,
`READBACK_MISMATCH`를 구분하며 `READBACK_FAILED`는 mutation이 발생했을 수 있으나 검증되지 않았다는 뜻이다.

## Read-only evidence와 결과 상태

`inspect-selection`은 selection subtree의 JSON-safe node fact를 반환한다. `audit-auto-layout`은 Auto Layout
parent가 없는데 `FILL` 또는 `ABSOLUTE` positioning을 쓰는 경우를 각각
`AUTO_LAYOUT_FILL_WITHOUT_AUTO_PARENT`, `AUTO_LAYOUT_ABSOLUTE_WITHOUT_AUTO_PARENT`로 보고한다.
`audit-prototype-links`는 action이 없거나 destination을 resolve할 수 없는 경우를
`PROTOTYPE_EMPTY_ACTIONS`, `PROTOTYPE_DESTINATION_MISSING`으로 보고한다. 이는 구조적 evidence이며 미적·UX
판단을 자동화하지 않는다.

validation failure는 `invalid`; mutation preview/apply의 failure-only는 `failed`; successful target과 skip/failure
혼재는 `partial`; clean preview는 `ready`; clean apply는 `applied`; mutation skip-only는 `no_changes`다. audit은
`findings` 또는 `clean`, non-empty inspection은 `inspected`다. 빈 selection은 `INVALID_FIELD`의 `invalid`다.
실제 Desktop import, companion execution과 live Figma read/write는 실행하지 않았으면 모두 `not_run`이다.
