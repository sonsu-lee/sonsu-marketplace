# Figma 품질 계약 평가

`cases.json`은 Figma Workflow가 native 구조와 실제 evidence를 품질 근거로 다루는지 검토하기 위한
behavior fixture입니다. 특정 문구가 아니라 관찰 가능한 불변식을 평가합니다.

- Auto Layout은 구조적 관계에 적용하고 decoration·overlay 같은 좌표 기반 예외를 구분합니다.
- `HUG`, `FILL`, `FIXED`를 content와 parent 관계에 맞춰 사용하고 실제 resize·content extreme을
  검증합니다.
- component, property, variable와 exact icon asset을 기존 source of truth부터 재사용합니다.
- screenshot, metadata/tree readback과 prototype playback을 서로 대신할 수 있는 근거로 취급하지
  않습니다.
- official MCP의 direct/bounded canvas execution과 사용자가 직접 실행하는 manual companion을 구분하며,
  companion mutation은 preview receipt와 exact target을 요구합니다.
- 부분 성공, tool failure와 실행하지 않은 capability를 `passed`로 바꾸어 보고하지 않습니다.

이 JSON은 실제 Figma file을 변경할 권한을 부여하지 않습니다. Live evaluation은 폐기 가능한 대상
file, 허용된 mutation 범위, model·도구 비용과 cleanup 책임을 별도로 승인받은 뒤 실행합니다.
