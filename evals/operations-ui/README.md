# Operations UI evaluation fixtures

`cases.json`은 operations-ui의 skill routing, 권한 경계와 evidence 판정 계약을 나타낸다. 구조 계약은 `cases.schema.json`에 있으며 semantic validator는 허용 expectation, 알려진 skill/check ID와 선택 모순을 함께 검사한다.

검증 범위:

- 신규 운영 화면과 기존 화면 재설계를 구분한다.
- 읽기 전용 감사에서는 mutation을 금지한다.
- WMS뿐 아니라 고객지원, 금융 운영, 콘텐츠 검수에도 같은 작업 구조를 적용한다.
- 마케팅·에디토리얼 UI에는 operations-ui를 자동 선택하지 않는다.
- Figma는 명시 요청에서만 선택하고 core dependency로 취급하지 않는다.
- 웹 구현 report는 browser evidence가 없으면 `overall: passed`를 금지한다.
- 제안/Figma-only는 실행용 report/schema와 구분한다. 관련 동작 사례는 [독립 스킬 평가](../skill-expansion/README.md)에 있다.
- 타입·입력 경계에서 배제한 상태의 분기를 만들지 않고, 선언한 실제 상태는 scenario coverage로 검증한다.
- 미결정 항목은 의존 작업과 G0·영향 gate·전체 통과만 막고 독립 작업과 유효 근거는 보존한다.
- 같은 작업의 자동 수정·재검증 누적 5회 상한은 에이전트·세션을 바꿔도 유지한다.

`must_decide`는 모델의 실제 행동·산출물을 대조할 기대 판단이며 fixture validator가 해당 행동을
실행하거나 강제하지 않는다. `plugins/operations-ui/tests/test_validate_contracts.py`는 선언 상태의
coverage, 모든 mode의 미결정 항목 구조, 전체·영향 gate의 허위 통과 거부와 무관한 gate 근거
보존을 CLI에서 검사한다. 의존성의 의미적 정확성과 재시도 횟수 준수는 별도 native 행동 평가다.

이 fixture의 JSON parse와 semantic validator는 실제 model routing, Codex native loader, Figma canvas 또는 target browser 동작을 증명하지 않는다. 실행하지 않은 검증은 `not_run`이다.
