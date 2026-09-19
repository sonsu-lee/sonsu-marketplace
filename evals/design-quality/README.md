# Design quality evaluation

`cases.json`은 디자인 일반론을 실제 판단 행동으로 바꾸는 behavior fixture다. 특정 문구보다
`primary_question`, 정보 역할·표현 추적, environment, 위험 분류, 사전 등록 metric과 차원별 floor가
산출물에 나타나는지를 평가한다.

자동 단위 테스트는 JSON 계약과 허위 통과를 검사한다. 실제 모델 행동, Figma canvas, browser runtime,
대표 사용자 결과는 별도 실행 근거가 없으면 `not_run`이다.

```bash
python3 -m unittest discover -s evals/design-quality -p 'test_*.py'
python3 scripts/validate_madia_design_catalog.py docs/research/madia-design-practice-catalog.json
```
