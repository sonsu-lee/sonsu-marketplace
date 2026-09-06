# Fluent Japanese 행동 평가

[`cases.json`](cases.json)은 `fluent-japanese`의 라우팅, 의미 보존과 일본어 표현을 실제
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

## 문어·한일 번역 확장 평가

[`writing-cases.json`](writing-cases.json)은 신규 40문항(8개 family별 5문항)과 위 fixture의
generation 10문항을 합친 50문항이다. 신규 문항 중 유지 16개와 모호성 보존 8개를 포함한다.
문항은 [연구 목록](../../docs/research/fluent-japanese-writing-catalog.md)에 있는 조건부
규칙을 바탕으로 별도 작성했다. 원문 사례 수와 평가 문항 수를 합산하지 않으며, 공개된
고정 세트이므로 held-out이라고 부르지 않는다. hidden target은 의미가 같은 대안을 허용한다.

실행 전에 [protocol.md](protocol.md)를 고정하고 [`eval.py`](eval.py)로 manifest를 만든다.
두 arm에는 렌더링한 독립 SKILL snapshot을 사용한다. `sources/languages/japanese.md`처럼
include marker가 남은 원본을 baseline으로 사용하지 않는다. 다음 인자의 두 파일은
저장소 밖에 미리 복사한 컴파일된 snapshot이다.

```sh
python3 evals/fluent-japanese/eval.py plan \
  --baseline-skill /absolute/experiment/snapshots/baseline.md \
  --candidate-skill /absolute/experiment/snapshots/candidate.md \
  --output /absolute/experiment/run/manifest.json --seed 20260906
python3 evals/fluent-japanese/eval.py preflight --manifest /absolute/experiment/run/manifest.json
python3 evals/fluent-japanese/eval.py run --manifest /absolute/experiment/run/manifest.json --workers 4
python3 evals/fluent-japanese/eval.py grade --manifest /absolute/experiment/run/manifest.json --workers 4
python3 evals/fluent-japanese/eval.py summarize --manifest /absolute/experiment/run/manifest.json
```

호스트가 넣는 공통 AGENTS·기본 스킬 설명은 두 arm의 hash가 같은지 검사한다. 생성 중
tool call이나 다른 Fluent 본문이 발견되면 비교 대상에서 제외한다. debug prompt 검사와
실제 exec 서비스 입력이 byte 단위로 같다는 보증은 없으며, 순수 격리 실험이라고 주장하지 않는다.

50문항 × 2개 arm × 2회 생성은 200회다. 이어서 동일한 고정 LLM rubric으로 blind 판정을
3회 수행한다. 두 반복을 문항 수준으로 합산하며, LLM 반복 판정과 원어민 평가를 구분한다.
실행 실패·미판정·동률을 분리하고, 정확한 문구의 보존과 대상 용례를 별도로 보고한다.

러너의 상태·순서·구조 판정은 다음으로 검사한다.

계획 단계에서 두 snapshot의 `fluent-japanese` frontmatter와 미해결 include 부재를
확인한다. 실행 전 preflight와 재사용하는 생성 기록은 현재 manifest/run 식별자와
일치해야 한다. 다른 실험의 기록이 있으면 새 실험 디렉터리에서 다시 계획한다.
`--timeout`은 30–600초이며 실제 값과 프로세스 시작·종료 시각을 기록한다.
알 수 없는 Codex item은 성공으로 간주하지 않는다. 제목·절차 marker는 fenced code를
제외한 본문에서 검사하고, 코드·보호 문자열은 원출력에서 검사한다.

```sh
python3 -B -m unittest evals/fluent-japanese/test_eval.py -v
```

실제 실행 결과와 채점 계약 수정·로컬 복귀 상태는
[2026-09-06 결과](results-2026-09-06.md)에 기록했다. 이 실행은 수정 분석이며, 현재 후보의
일반 채택이나 원어민 품질 검증을 통과한 결과가 아니다.
