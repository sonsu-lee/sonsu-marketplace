# Figma interaction 계약 평가

`cases.json`은 `design:figma-prototype-flow`가 화면 사이의 설명용 화살표가 아니라 실제 Figma
reaction과 검증 가능한 상태 동선을 만드는지 평가하는 behavior fixture입니다.

핵심 불변식은 다음과 같습니다.

- actual control의 connection, concise annotation과 named state topology를 각각 유지합니다.
- `Trigger → Action → Destination/Next state → Condition → Visible result → Back/close → Edge case`를
  중요한 transition에서 추적합니다.
- local reusable state는 component variant·variable, meaningful screen state는 별도 frame으로 구분합니다.
- primary, failure와 recovery path를 starting point에서 playback합니다.
- reaction write 성공, readback과 playback 성공을 서로 다른 evidence로 기록합니다.
- 같은 prototype graph와 연결된 state frame은 하나의 writer가 수정합니다.

이 fixture는 live canvas를 수정하지 않습니다. 실제 model routing과 prototype 동작 평가는 model,
반복 횟수, 폐기 가능한 target file, mutation 범위와 비용을 별도로 승인받은 뒤 수행하며 그 전에는
`not_run`입니다.
