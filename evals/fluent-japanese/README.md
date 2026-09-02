# Fluent Japanese 행동 평가

[`cases.json`](cases.json)은 `fluent-japanese`의 라우팅, 의미 보존과 일본어 표현을 이후 실제
모델로 확인하기 위한 고정 입력이다. 이 fixture는 특정 정답 문장을 요구하지 않고, 바뀌면
안 되는 literal과 구조, 의미 계약, 과잉 교정 반례와 사람이 볼 항목을 분리한다.

모델에는 각 case의 `prompt`와 `evidence`만 전달한다. `expectations`와 `review_points`는
실행 모델에 노출하지 않고 평가자가 사용한다.

## 판정 경계

- JSON parsing, renderer 일치와 skill frontmatter 검증은 실제 모델 행동 평가가 아니다.
- 결과 artifact가 없으면 전체 행동 평가 상태는 `not_run`이다.
- timeout, 빈 출력과 trace 누락은 `not_run`, 다른 언어·문체 skill이 섞인 실행은
  `inconclusive`로 기록한다.
- `protected_literals`, 제목, marker 순서, literal 횟수와 code block은 자동 검사할 수 있다.
- 귀속, 조건, 인과, 불확실성과 modality 보존은 의미 검사와 사람 검토가 필요하다.
- 자연스러운 생략, 경어, 조사, 수식 관계와 전반적인 일본어 품질은 일본어 화자가 확인한다.
- raw output, trace와 판정 결과는 repository 밖에 둔다.

이 평가는 위험한 회귀를 찾는 smoke test다. fixture 통과만으로 일본어 자연스러움이나 일본어
사용자 전체의 선호를 입증하지 않는다.

## 정적 검증

```sh
python3 -m json.tool evals/fluent-japanese/cases.json >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/fluent-languages/skills/fluent-japanese
```

실제 모델 smoke test를 수행한다면 먼저 `generation` case를 실행하고, `routing` case는 실제
Codex trace에서 선택된 skill을 별도로 확인한다. 자동 검사를 통과해도 귀속·조건·modality
위반이 있으면 실패다. 실제 실행을 하지 않았다면 정적 검증 결과와 섞어 `pass`로 쓰지 않는다.
