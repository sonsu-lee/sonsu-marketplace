# Operations UI evaluation fixtures

`cases.json`은 operations-ui의 skill routing, 권한 경계와 evidence 판정 계약을 나타낸다. 구조 계약은 `cases.schema.json`에 있으며 semantic validator는 허용 expectation, 알려진 skill/check ID와 선택 모순을 함께 검사한다.

검증 범위:

- 신규 운영 화면과 기존 화면 재설계를 구분한다.
- 읽기 전용 감사에서는 mutation을 금지한다.
- WMS뿐 아니라 고객지원, 금융 운영, 콘텐츠 검수에도 같은 작업 구조를 적용한다.
- 마케팅·에디토리얼 UI에는 operations-ui를 자동 선택하지 않는다.
- Figma는 명시 요청에서만 선택하고 core dependency로 취급하지 않는다.
- browser evidence가 없으면 `overall: passed`를 금지한다.

이 fixture의 JSON parse와 semantic validator는 실제 model routing, Codex native loader, Figma canvas 또는 target browser 동작을 증명하지 않는다. 실행하지 않은 검증은 `not_run`이다.
