# Design decision and quality contract

화면 품질은 시각 취향의 평균 점수가 아니라 `사용자·맥락 → 판단과 과업 → 필요한 정보 → 표현 → 상태와 상호작용 → 관찰 결과`의 연결로 판정한다. 원칙 이름이나 사례 수만으로 합격시키지 않는다.

원칙의 출처 수준과 흔한 일반론을 실제 계약으로 바꾸는 방법은 [evidence map](sources.md)을 따른다.

## 작업 흐름

1. `primary_question`, `intended_outcome`, 잘못 판단했을 때의 비용을 먼저 고정한다.
2. 각 task scenario에 필요한 `must_know`, `supporting`, `on_demand` 정보를 연결한다.
3. 정보마다 표현 종류, semantic role, 선택 이유와 `non_color_signals`를 기록한다. 색상만으로 상태나 위험을 전달하지 않는다.
4. 대상 locale, writing mode, viewport, input method와 accessibility profile을 environment로 선언한다.
5. 적용 가능한 상태와 복구·안전 동작을 정한 뒤, `outcome_plan`에 scenario·metric·참가자 기준·목표 인원·protocol을 결과 관찰 전에 고정한다.
6. 현재 산출물 범위의 DQ gate를 평가하고, 뒤 단계는 `not_run`으로 남긴다.

## 차원별 합격

필수 DQ gate는 각각 통과해야 한다. DQ1–DQ6의 주관적 rubric은 작성자가 아닌 독립 평가자 2명이 0–4점으로 평가하고, 두 점수의 최솟값이 3 이상이어야 한다. 점수 차이가 1보다 크면 평균하지 않고 `inconclusive`로 돌려 판정을 조정한다. hard check 실패와 열린 critical finding은 높은 점수로 상쇄할 수 없다.

| 점수 | 관찰 가능한 기준 |
| --- | --- |
| 0 | 사용할 수 있는 근거가 없거나 산출물이 잠긴 계약과 모순된다. |
| 1 | 사용자 과업·정보·상태·환경의 중대한 누락 때문에 산출물을 신뢰할 수 없다. |
| 2 | 의도는 보이지만 잘못된 사용자 판단을 만들 수 있는 실질적 공백이 하나 이상 남아 있다. |
| 3 | 실질 요구가 모두 근거로 확인되고 남은 문제는 사용자 판단을 바꾸지 않는 경미한 수준이다. |
| 4 | 3점을 충족하며 독립 근거가 의미 있는 edge case까지 다루고 실질적 미결정이 없다. |

| Gate | 질문 |
| --- | --- |
| DQ0 | 범위, 추적 관계와 평가 기준이 결과를 보기 전에 고정됐는가 |
| DQ1 | 사용자, 과업, 올바른 판단과 오판 비용이 명확한가 |
| DQ2 | must-know 정보와 표현이 모든 주요 과업에 연결되는가 |
| DQ3 | 시각 강조가 의미·우선순위·선언된 디자인 시스템을 따르는가 |
| DQ4 | 적용 상태와 긴 콘텐츠·현지화·극단값을 다루는가 |
| DQ5 | 피드백, 권한, 오류·부분 실패·취소·복구가 과업 비용에 맞는가 |
| DQ6 | 계약된 환경과 접근성 프로필에서 판단과 조작이 유지되는가 |
| DQ7 | 제안·Figma·구현에 맞는 구조·readback·runtime 증거가 있는가 |
| DQ8 | 사전 등록 outcome metric과 위험도에 맞는 사용자 증거가 있는가 |

Proposal은 DQ0–DQ6, Figma와 implementation은 DQ0–DQ7, live end-to-end 평가는 DQ0–DQ8을 요구한다. 앞 단계의 `scope_status=passed`는 허용하지만 DQ8이 없으면 `end_to_end_status=passed`로 올리지 않는다.
`figma-workflow` profile은 artifact scope와 무관하게 Figma native receipt를 유지한다. 다른 profile도
Figma scope를 주장하면 같은 receipt로 node·capability·resize·prototype readback을 입증해야 한다.

## 위험과 사용자 증거

- low: 독립 task-based walkthrough 2건 또는 더 강한 대표 사용자·production 증거
- medium: 대표 사용자 task test 또는 production behavior
- high: 대표 사용자 task test와 별도 domain/safety review

법률·금융·건강·안전·개인정보·권리, 비가역 결과, 대량 외부 영향이나 복구 비용이 큰 작업을 낮은 위험으로 분류하지 않는다. 참가자 수와 outcome 목표는 제품 맥락에서 사전 등록하며 전역 성공률을 강제하지 않는다. 관찰된 critical harm 목표는 0이다.

## 근거와 상태

`passed`, `failed`, `blocked`, `inconclusive`, `not_run`, `not_applicable`, `accepted_risk`를 구분한다. 증거가 없으면 점수를 추정하지 않는다. `accepted_risk`는 사람이 현재 revision의 위험을 명시적으로 수용한 별도 상태이며 통과가 아니다. Contract digest가 다르면 결과를 본 뒤 기준을 바꾼 것으로 취급하고 report를 거부한다.

Report의 evidence와 artifact locator는 report 디렉터리 안의 실제 비어 있지 않은 파일이어야 한다.
평가·metric·outcome에는 잠긴 contract 이후의 시각과 평가한 artifact revision을 남긴다. 각
outcome receipt는 잠긴 `outcome_plan`의 ID, scenario·metric 범위, 참가자 기준·목표 인원과
protocol을 그대로 참조해야 한다. DQ8이
`not_run` 또는 `blocked`이면 아직 수집하지 않은 outcome을 만들지 않고 빈 배열로 둘 수 있지만,
DQ8을 통과시키려면 등록한 모든 scenario와 metric, 목표 인원을 덮는 위험도에 맞는 사용자 근거가
필요하다. 실패한 실행의 실제 관찰값은 없애지 않고 `failed` receipt로 보존할 수 있다.

`not_applicable`은 정책이 명시한 제한된 check에만 사용할 수 있고, traceability·사전등록·artifact
provenance·outcome 같은 mandatory check는 exclusion으로 우회하지 못한다. 필수 gate를 통과시키려면
적어도 하나의 실제 실행 check가 `passed`여야 한다.
