# Figma Workflow Companion

Figma Desktop에서 사용자가 직접 실행하는 결정적 companion plugin입니다. Codex가 Figma canvas를
수정하는 경로는 공식 Figma MCP `use_figma`이며, 이 plugin은 그 경로를 대체하거나 agent-callable
bridge를 만들지 않습니다.

## Build and import

```sh
npm install
npm run build
```

Figma Desktop에서 `Plugins` → `Development` → `Import plugin from manifest...`를 선택한 뒤 이
directory의 `manifest.json`을 지정합니다. `dist/code.js`와 `dist/ui.html`은 build 결과로 저장소에
포함되어 있어, build를 실행하지 않은 검토자도 manifest 경로를 정적으로 확인할 수 있습니다.

## Operation plans

UI에는 version 1 allowlist JSON만 입력합니다. unknown field와 operation은 engine이 거부하며,
arbitrary JavaScript를 평가하거나 network request를 만들지 않습니다. manifest는
`networkAccess.allowedDomains: ["none"]`로 모든 network access를 막습니다.

Read-only plan은 현재 selection만 읽습니다.

```json
{
  "version": 1,
  "mode": "preview",
  "operation": "inspect-selection",
  "scope": { "kind": "selection" }
}
```

Selection inventory는 선택한 root와 descendants를 재귀적으로 snapshot한다. 반면 exact target mutation의
precondition/readback과 prototype destination 존재 확인은 target node 자체만 shallow read하므로, 관계없는
descendant의 host read failure가 해당 target을 막지 않는다. Auto Layout audit는 `HORIZONTAL`, `VERTICAL`,
`GRID` parent를 Auto Layout parent로 취급한다.

Mutation plan은 반드시 explicit `nodeId`와 expected state를 사용합니다. 먼저 `mode: "preview"`로
Preview를 실행하고, 같은 입력을 유지한 채 Apply를 누릅니다. UI는 Apply 전에 내부적으로 mode만
`apply`로 정규화하며, matching preview receipt가 있을 때만 engine이 mutation을 허용합니다.

```json
{
  "version": 1,
  "mode": "preview",
  "operation": "rename-exact",
  "targets": [{
    "nodeId": "1:2",
    "expectedName": "Old name",
    "newName": "New name"
  }]
}
```

`replace-icon-instance-exact`는 `expectedMainComponentKey`와
`replacementComponentKey`를 사용합니다. Figma adapter는 `importComponentByKeyAsync()`로 component를
가져오고 `InstanceNode.swapComponent()`로 instance를 교체한 뒤 readback합니다.

입력 textarea를 수정하면 receipt를 즉시 폐기합니다. receipt는 UI process memory에만 있으며 storage,
plugin data, network 또는 document에 저장하지 않습니다. plugin을 닫으면 새 preview가 필요합니다.
각 UI request는 generation ID와 요청 당시 입력을 함께 전달한다. 이전 Preview 또는 Apply의 늦은
response는 현재 generation과 입력이 모두 일치할 때만 표시하거나 receipt로 채택한다.

Malformed UI message는 `{ status: "invalid", reason: "INVALID_FIELD" }`로, plan/receipt validation은
기존의 안정된 validation reason을 가진 `invalid` 결과로 응답한다. 반면 selection snapshot, prototype
destination, final conditional mutation lookup 같은 host
lookup exception은 `{ status: "failed", reason: "LOOKUP_FAILED" }`로 응답한다. 실제 name assignment나
`swapComponent()` failure는 `{ status: "failed", reason: "MUTATION_FAILED" }`다. raw error나 stack은 UI에
전달하지 않는다.

Selection snapshot의 `variableBindings`는 JSON-safe 사실만 보존한다. literal opacity는
`{ "kind": "literal", "value": 0.5 }`, 하나의 Figma variable alias는
`{ "kind": "binding", "variableId": "VariableID:…" }`, alias 배열은
`{ "kind": "binding-list", "variableIds": ["VariableID:…"] }`, component property map은
`{ "kind": "component-properties", "properties": { "Property": { "kind": "binding", "variableId": "…" } } }`로
정규화한다. variable binding이 있으면 해당 literal fact보다 우선하며, 알 수 없거나 비정상 값은 생략한다.

## Verification boundary

`npm test`, `npm run typecheck`, `npm run build`는 parser/engine, TypeScript, manifest path와 checked-in
bundle을 검증합니다. 실제 Figma Desktop import와 live canvas read/mutation은 이 환경에서 실행하지
않았으며 `not_run`입니다.
