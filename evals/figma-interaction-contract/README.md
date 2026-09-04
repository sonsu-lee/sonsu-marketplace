# Figma interaction 계약 평가

`cases.json`은 `figma-workflow:figma-prototype-flow`가 설명용 화살표가 아니라 실제 Figma reaction과
검증 가능한 상태 동선을 요구하는지, 그리고 canvas write와 수동 companion의 경계를 지키는지 평가하는
behavior fixture입니다.

핵심 불변식은 다음과 같습니다.

- actual control의 connection, concise annotation과 named state topology를 각각 유지합니다.
- `Trigger → Action → Destination/Next state → Condition → Visible result → Back/close → Edge case`를
  중요한 transition에서 추적합니다.
- Figma canvas의 agent write는 official MCP만 수행하고, `use_figma` 전에 `figma:figma-use` prerequisite를
  적용합니다.
- exact rename 또는 icon swap처럼 allowlisted companion mutation은 explicit target, same-plan preview
  receipt, apply-time re-read와 readback을 요구합니다.
- write response, structure/readback과 playback은 서로 다른 evidence이며 capability가 없거나 실행하지
  않은 경우 `blocked`, `inconclusive` 또는 `not_run`으로 남깁니다.

이 fixture는 live canvas를 수정하지 않습니다. 실제 model routing, Figma MCP exposure, prototype 동작과
Figma Desktop companion 실행 평가는 별도 승인된 target, mutation 범위와 비용이 있어야 하며, 그 전에는
`not_run`입니다.
