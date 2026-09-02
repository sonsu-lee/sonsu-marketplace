# Fluent English 행동 평가

[`cases.json`](cases.json)은 `fluent-english`의 라우팅, 의미 보존과 영어 표현을 이후 실제
모델로 확인하기 위한 고정 입력이다. 이 fixture는 특정 정답 문장을 요구하지 않고, 바뀌면
안 되는 literal과 구조, 의미 계약, 과잉 교정 반례와 사람이 볼 항목을 분리한다.

모델에는 각 case의 `prompt`와 `evidence`만 전달한다. `expectations`와 `review_points`는
실행 모델에 노출하지 않고 평가자가 사용한다.

## 판정 경계

- JSON parsing, renderer 일치와 skill frontmatter 검증은 실제 모델 행동 평가가 아니다.
- 결과 artifact가 없으면 전체 행동 평가 상태는 `not_run`이다.
- timeout, 빈 출력과 trace 누락은 `not_run`, 다른 언어·문체 skill이 섞인 실행은
  `inconclusive`로 기록한다.
- `protected_literals`, `forbidden_literals`, 제목, marker 순서, literal 횟수와 code block은
  자동 검사할 수 있다.
  Markdown inline code 자체가 보호 대상이면 `protected_literals`에 backtick까지 포함한다. 특정
  철자나 승인 문구가 아닌 일반 산문은 exact 항목이 아니라 의미 계약으로 검사한다.
- 귀속, 조건, 인과, 불확실성과 modality 보존은 의미 검사와 사람 검토가 필요하다.
- 행위자와 대명사, 수식 범위, 영어 변이, register와 전반적인 영어 품질은 영어에 능숙한
  검토자가 확인한다.
- raw output, trace와 판정 결과는 repository 밖에 둔다.

이 평가는 위험한 회귀를 찾는 smoke test다. fixture 통과만으로 영어 자연스러움이나 영어
사용자 전체의 선호를 입증하지 않는다.

Generation prompt는 가능한 한 일반적인 산출물 요청으로 두고, 영어 스킬이 해결해야 할
세부 조건은 숨겨진 기대값에 기록한다. 다만 요구 형식, 독자, 영어 변이와 그대로 유지할
문자열처럼 사용자만 정할 수 있는 조건은 prompt에 명시한다. 이 구성도 단일 실행의 차이를
스킬 효과로 입증하지는 않으며, 그 판단에는 같은 입력의 격리된 baseline 비교가 필요하다.

## 정적 검증

```sh
python3 -m json.tool evals/fluent-english/cases.json >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  plugins/fluent-languages/skills/fluent-english
```

실제 모델 smoke test를 수행한다면 먼저 `generation` case를 실행하고, `routing` case는 실제
Codex trace에서 선택된 skill을 별도로 확인한다. 자동 검사를 통과해도 귀속·조건·modality
위반이 있으면 실패다. 실제 실행을 하지 않았다면 정적 검증 결과와 섞어 `pass`로 쓰지 않는다.
