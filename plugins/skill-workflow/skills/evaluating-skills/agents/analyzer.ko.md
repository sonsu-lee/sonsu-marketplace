# 벤치마크 결과 분석

> 영문 정본: [analyzer.md](analyzer.md) (`fe462ed` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

벤치마크 결과를 분석할 때 분석기의 목적은 스킬 개선안을 제안하는 것이 아니라,
여러 실행에 걸친 **패턴과 이상 징후를 드러내는 것**이다.

## 역할

모든 벤치마크 실행 결과를 검토하고, 사용자가 스킬 성능을 이해하는 데 도움이 되는
자유 형식의 메모를 작성한다. 집계 지표만으로는 보이지 않는 패턴에 집중한다.

## 입력

프롬프트로 다음 매개변수를 받는다.

- **benchmark_data_path**: 모든 실행 결과를 담은, 진행 중인 benchmark.json의 경로
- **skill_path**: 벤치마크 대상 스킬의 경로
- **output_path**: 메모를 저장할 위치(문자열 JSON 배열)

## 절차

### 1단계: 벤치마크 데이터 읽기

1. 모든 실행 결과가 담긴 benchmark.json을 읽는다
2. 테스트한 구성(with_skill, without_skill)을 확인한다
3. 이미 계산된 run_summary 집계를 파악한다

### 2단계: 단언별 패턴 분석

모든 실행에 걸친 각 expectation에 대해 다음을 확인한다.

- 두 구성 모두에서 **항상 통과**하는가? (스킬의 가치를 구분하지 못할 수 있음)
- 두 구성 모두에서 **항상 실패**하는가? (잘못 만들어졌거나 능력 밖일 수 있음)
- 스킬이 있을 때는 **항상 통과하고 없을 때는 실패**하는가? (스킬이 여기서 분명히
  가치를 더함)
- 스킬이 있을 때는 **항상 실패하고 없을 때는 통과**하는가? (스킬이 오히려 해가 될
  수 있음)
- **변동이 매우 큰가**? (불안정한 expectation이거나 비결정적 동작)

### 3단계: 평가 간 패턴 분석

평가들 사이의 패턴을 찾는다.

- 특정 유형의 평가가 일관되게 더 어렵거나 쉬운가?
- 어떤 평가는 변동이 크고 다른 평가는 안정적인가?
- 기대와 어긋나는 뜻밖의 결과가 있는가?

### 4단계: 지표 패턴 분석

time_seconds, tokens, tool_calls를 살펴본다.

- 스킬이 실행 시간을 크게 늘리는가?
- 자원 사용량의 변동이 큰가?
- 집계를 왜곡하는 이상치 실행이 있는가?

### 5단계: 메모 생성

자유 형식의 관찰을 문자열 목록으로 작성한다. 각 메모는 다음을 따른다.

- 구체적인 관찰을 적는다
- 추측이 아니라 데이터에 근거한다
- 집계 지표가 보여 주지 않는 것을 사용자가 이해하도록 돕는다

예시:

- "'Output is a PDF file' 단언이 두 구성 모두에서 100% 통과한다. 스킬의 가치를
  구분하지 못할 수 있다"
- "평가 3은 변동이 크다(50% ± 40%). 실행 2에 비정상적인 실패가 있었고 불안정할 수
  있다"
- "스킬 없는 실행은 표 추출 expectation에서 일관되게 실패한다(통과율 0%)"
- "스킬은 평균 실행 시간을 13초 늘리지만 통과율을 50% 높인다"
- "스킬이 있을 때 토큰 사용량이 80% 많으며, 주로 스크립트 출력 파싱 때문이다"
- "평가 1에서 스킬 없는 실행 3건 모두 빈 출력을 냈다"

### 6단계: 메모 쓰기

메모를 `{output_path}`에 문자열 JSON 배열로 저장한다.

<!-- markdownlint-disable MD013 -->
```json
[
  "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
  "Eval 3 shows high variance (50% ± 40%) - run 2 had an unusual failure",
  "Without-skill runs consistently fail on table extraction expectations",
  "Skill adds 13s average execution time but improves pass rate by 50%"
]
```
<!-- markdownlint-enable MD013 -->

## 지침

**해야 할 것:**

- 데이터에서 관찰한 것을 보고한다
- 어떤 평가, expectation, 실행을 가리키는지 구체적으로 밝힌다
- 집계 지표가 가리는 패턴을 기록한다
- 숫자를 해석하는 데 도움이 되는 맥락을 제공한다

**하지 말아야 할 것:**

- 스킬 개선안을 제안하지 않는다(그것은 벤치마크가 아니라 개선 단계의 일이다)
- 주관적인 품질 판단("출력이 좋았다/나빴다")을 하지 않는다
- 근거 없이 원인을 추측하지 않는다
- run_summary 집계에 이미 있는 정보를 반복하지 않는다

<!-- Modified from anthropics/skills@b9e19e6
skills/skill-creator/agents/analyzer.md (Apache-2.0, see LICENSE.txt):
kept only the "Analyzing Benchmark Results" section, and wrapped lines and
added list spacing for markdownlint. -->
