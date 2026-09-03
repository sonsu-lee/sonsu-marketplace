# Design 품질 계약 평가

`cases.json`은 Design 스킬이 Figma와 Paper의 native 구조를 실제 품질 근거로 다루는지 검토하기
위한 behavior fixture입니다. 표현의 특정 문구보다 다음 관찰 가능한 불변식을 평가합니다.

- Auto Layout은 구조적 관계에 적용하고 장식·overlay 같은 좌표 기반 예외를 구분합니다.
- `HUG`, `FILL`, `FIXED`를 content와 parent 관계에 맞춰 사용하고 실제 resize·content extreme을
  검증합니다.
- component, property, variable와 exact icon asset을 기존 source of truth부터 재사용합니다.
- Figma interaction은 executable reaction, annotation과 state topology를 서로 다른 계약으로
  검증합니다.
- Paper는 flex/DOM/code roundtrip을 기준으로 검증하며 native prototype을 지원한다고 가정하지
  않습니다.
- screenshot, metadata/tree readback과 실제 prototype preview를 서로 대신할 수 있는 근거로
  취급하지 않습니다.
- 부분 성공, tool failure와 unsupported capability를 `passed`로 바꾸어 보고하지 않습니다.

이 JSON은 실제 Figma·Paper 파일을 변경할 권한을 부여하지 않습니다. Live evaluation은 폐기 가능한
대상 파일, 허용된 mutation 범위, model·도구 비용과 cleanup 책임을 별도로 승인받은 뒤 실행합니다.
