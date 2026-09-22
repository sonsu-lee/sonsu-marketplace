# Figma Workflow

Figma product screen, responsive Auto Layout, component/variable, exact asset와 clickable prototype을
제작·감사하는 `1.0.0` capability pack이다. Codex manifest의 `.app.json` connector metadata와 사용자가
직접 실행하는 deterministic Desktop companion을 유지한다. 설치만으로 canvas access가 생기지 않는다.

## Skills

- `figma-product-design`: native screen structure, responsive layout, component/variable와 handoff
- `figma-prototype-flow`: control reaction, overlay/back/dismiss, state branch와 playback evidence
- `figma-design-audit`: structure, reuse, provenance, interaction과 handoff의 read-only audit

## Host-adaptive capability

current host가 실제 노출한 Figma provider와 prerequisite만 사용한다. Codex 전용
`figma:figma-use` ID는 노출된 경우에만 적용한다. OMP에서는 현재 노출된 Figma MCP/plugin
capability와 schema를 사용한다. 어느 host에서도 실제 Figma read/write capability가 없으면 API를
추정하거나 raw MCP, local bridge 또는 두 번째 writer를 만들지 않고 `blocked` 또는 `not_run`으로
끝낸다.

판단형 canvas 작업은 현재 provider 하나가 수행하며 conflict domain write를 직렬화한다. Desktop
companion은 agent writer가 아니라 사용자가 Figma Desktop에서 직접 실행하는 version 1 allowlisted
JSON tool이다. `inspect-selection`, `audit-auto-layout`, `audit-prototype-links`, `rename-exact`,
`replace-icon-instance-exact`만 지원하며 mutation은 preview, apply 직전 re-read와 readback을 요구한다.

Figma scope는 DQ0–DQ7이다. DQ1–DQ6 판정에는 같은 artifact/contract evaluator run이 최소 하나
필요하다. relationship은 evidence metadata이며 independent reviewer spawn을 강제하지 않는다. 여러
run이면 최솟값과 divergence를 보존한다. Figma 통과를 live runtime/user outcome으로 확대하지 않는다.

```sh
python3 scripts/validate_design_quality.py contract <contract.json>
python3 scripts/validate_design_quality.py report <report.json> <contract.json>
```
