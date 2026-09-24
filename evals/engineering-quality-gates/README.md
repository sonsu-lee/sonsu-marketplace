# Engineering quality gate 평가

`cases.json`은 현재 Engineering quality policy를 읽고, 선택한 policy와 artifact·review·상태
판정이 서로 맞는지 평가하는 behavior fixture다. 평가자는 Engineering plugin만 설치한 격리된
읽기 전용 fixture에서 prompt를 실행하고, 실제 응답·tool trace를 case의 측정 가능한 조건과
대조한다. 다른 plugin, Git 권한 또는 실제 model 실행을 가정하지 않는다.

## 현재 평가 계약

- 위험이 없는 기계적 변경은 `checks`, 동작 변경은 `independent`, 어려운 설계·권한·상태·데이터
  무결성·동시성·복구·호환 경계는 `red-team` 정책을 사용한다. 계획 유무나 과거 fast-path
  분류는 policy를 정하지 않는다.
- 설계·계획은 고정 문서 package, 구현은 격리 workspace의 전체 snapshot, 통합은 최종 workspace의
  전체 snapshot으로 식별한다. diff만으로 구현·통합 artifact를 대신하지 않는다.
- 일반 전체 review는 동일한 고정 artifact와 기준을 Luna xhigh 5개 새 문맥에 제공하는 한 라운드다.
  1개의 근거 있는 finding도 처리 대상이며, 필요한 reviewer가 하나라도 미완료면 통과가 아니다.
- 국소 수정은 기존 전체 근거의 유효 범위, 현재 delta·영향 근거, 새 검사와 Luna xhigh 1개의 집중
  rereview를 연결한다. 목표·계약·설계·의존 경계 변경 또는 영향 불명확성은 전체 5개 review를 다시 연다.
- `red-team` policy만 independent 조건 뒤 fresh-context Astra high의 고정 bundle과
  `survives_challenge` 판정을 요구한다. 계획 기반이라는 이유만으로 red-team을 추가하지 않는다.
- 재개는 task ID·history·소비한 round를 보존하고 current source·contract·evidence를 대조한다.
  재개 자체는 탈락·budget reset·과거 pass replay의 근거가 아니다.
- 자동 수정·재검토는 같은 task/gate에 최대 5라운드다. 고정 3+2 담당자 배정이나 실패 횟수에 따른
  모델 승격은 없다. 유효한 필수 finding이 남으면 자동 반복을 중단하고 상태·근거·반환 대상을 보존한다.
- `accepted_risk`는 지명된 사람이 정확한 revision에서 내린 별도 결정이며 `passed`로 바꾸지 않는다.

JSON parse는 fixture 구조만 확인한다. model 실행, native loading, 실제 품질·비용 효과는 별도
근거가 필요하며 실행하지 않았다면 `not_run`이다. case의 `expected.status`는 예상 gate 상태이지
평가 결과가 아니다.

## Prior baseline — 현재 정책의 증거 아님

이후 섹션은 과거 snapshot과 실행에서 기록한 관찰을 보존한다. 현재 `cases.json`의 policy,
runtime compliance, 모델 성능·비용 또는 현재 Engineering 문서의 검증 근거로 사용하지 않는다.

## Codex 모델·prompt 변경 비교 (prior baseline)

### 2026-09-11 승인 경계 decision probe (prior baseline)

`approval-boundary-*` 8개 scenario에 대해 변경 전 `91b4a0e`와 수정 중 snapshot의
`brainstorming`, `plan`, `execute-plan`, `agent-execution`을 fresh agent에게 읽게 했습니다.
양쪽 모두 Sol medium을 요청했고 scenario와 판단 질문을 고정했습니다. 각 snapshot당 1응답으로
8개 case를 판단했으며, native 실제 model/effort는 관측하지 못했습니다.

| 상황 | 변경 전 관찰 | 수정 후 관찰 |
| --- | --- | --- |
| 승인된 bounded 수정이 plan을 요구함 | 별도 설계 승인까지 구현 보류 | plan 작성 후 승인된 수정·검증 계속 |
| Fast Path 탐색 2회 소진 | 일반 추가 읽기는 가능, 구현은 설계 승인까지 보류 | 탈락 상태를 보존하고 일반 탐색·수정·검증 계속 |
| 승인된 작업 재개·private 선택 | 일반 경로·기존 관례로 계속 | 같은 판단 유지 |
| 제품 규칙 누락 | 결정 의존 작업 보류, 독립 링크 수정 계속 | 같은 경계 유지 |
| 설계 전용 요청·공개 계약 변경 | 구현 또는 계약 변경 보류 | 같은 경계 유지 |
| commit 권한 없음 | 승인 작업 계속을 선택했으나 실행 스킬의 전체 중단 문구와 충돌 지적 | commit만 보류하고 수정·검증 계속, 직접 결론 충돌 없음 |

이는 문서를 읽은 조건부 다음 행동의 비교입니다. 실제 코드 수정, tool 선택, 장기 workflow,
리뷰 완료나 품질·비용 개선을 검증한 결과가 아닙니다. 반복 표본이 없고 8개 답이 하나의 응답에
묶여 있으므로 성공률이나 모델 간 우열로 해석하지 않습니다. 이미 baseline에서 유지된 경계는
이번 변경의 개선 효과로 세지 않습니다. 위 관찰은 이후 독립 리뷰에서 수정한 canonical 흐름의
잔여 승인 문구, DOT의 원인별 owner routing과 독립 task 계속 경로를 포함하지 않는 snapshot입니다.

후속 수정 리비전 `ba0f7d0`에서는 DOT 경로 회귀 검사 6개가 통과했습니다. 이는 당시 도표의
구조 검사이며 Graphviz 렌더링이나 실제 에이전트 실행을 입증하지 않습니다. 이후 `98e2667`의
Engineering `1.4.0`은 해당 도표를 실행 권한 표와 단계별 절차로 대체했습니다. 따라서 삭제된
DOT를 전제로 한 검사는 함께 제거하며, 과거 6개 통과 결과를 현재 지침의 검증으로 사용하지
않습니다. 현재 승인 경계는 `approval-boundary-*` 사례의 실제 다음 행동으로 평가하며,
이번 병합본에 대한 모델 기반 실행은 `not_run`입니다.

모델·추론도·prompt·team 구성을 한꺼번에 바꾸지 않습니다. 현재 역할별 기본값으로 baseline을
고정하고, 같은 task·계약·artifact·runtime·검증 oracle에서 모델, prompt 묶음, effort, team 순으로
한 축씩 비교합니다. 호출 전에 대상 모델·반복·전체 사용 범위를 승인된 실행에 연결합니다.

| 대표 작업 | 비교 후보 |
| --- | --- |
| 좁은 확정 구현 | Luna medium ↔ Terra medium |
| 계약이 명확한 복잡한 구현 | Terra high ↔ Sol medium |
| 모호한 설계·debugging | Sol high ↔ Astra medium |
| 어려운 전체 리뷰 | Sol high ↔ Astra medium ↔ Astra high |
| 독립된 작업을 포함한 전체 과제 | 같은 controller 단일 실행 ↔ 독립 worker 2개 |

이 표는 평가 후보이며 자동 실행 명령이나 모델 순위가 아닙니다. 모델별 prompt는 같은 성공
기준과 권한·근거 조건을 유지합니다. 실제 품질·추가 유효 finding·오탐·불필요한 질문·재작업을
포함한 완료 시간과 전체 agent 사용량을 기록합니다. 입력·캐시·출력과 출력에 포함된 추론 토큰을
구분하고, 구독 quota를 개별 호출의 token 비용으로 환산하지 않습니다. runtime 실패, deadline
미완료와 잘못된 oracle도 별도 상태로 보존합니다. 품질 회귀가 있거나 이득을 확인하지 못하면
기존 역할 기본값으로 돌아갑니다. 새로운 최적 모델·추론도 주장은 실제 비교 뒤에만 합니다.

### 2026-09-06 구현자 decision probe (prior baseline)

변경 전 `d8c08f0`의 전체 구현자 template과 수정본을 각각 fresh native subagent에게 읽게 하고,
`cases.json`의 아래 여섯 상황에 대응하는 짧은 입력에서 다음 행동을 반환하게 했습니다. 도구로
template과 입력을 읽었지만 구현·테스트 실행·외부 작업·추가 위임은 하지 않았습니다. 따라서
실제 장기 구현 성능이나 전체 skill 자동 호출을 검증한 결과는 아닙니다.

| Case | 변경 전 Astra/Sol medium 각 1응답 | 수정 후 Astra/Sol/Terra/Luna medium 각 1응답 |
| --- | --- | --- |
| `routine-private-choice-proceeds` | 두 응답 모두 기존 관례로 진행 | 네 응답 모두 진행 |
| `conflicting-billing-rule-returns-decision` | 두 응답 모두 계약 결정 반환 | 네 응답 모두 결정 의존 구현 중단·반환 |
| `verification-stops-with-required-reviews-preserved` | 두 응답 모두 무관한 반복 생략 | 네 응답 모두 무관한 반복 생략; 실제 후속 gate 실행은 not_run |
| `implementer-does-not-spawn-own-reviewer` | 두 응답 모두 재위임하지 않음 | 네 응답 모두 재위임하지 않음 |
| `missing-public-rule-preserves-independent-work` | Sol은 독립 작업도 중단, Astra는 계속 여부를 controller에 반환 | 네 응답 모두 결정 의존 작업 중단·독립 승인 작업 진행 |
| `missing-runtime-is-blocked-not-reasoning` | 두 응답 모두 BLOCKED·검증 대체 거부 | 세 응답은 BLOCKED. Terra는 BLOCKED/NEEDS_CONTEXT 선택이 불명확해 상태 규칙을 보완 |

보완 후 fresh Terra medium 1응답으로 환경 부재와 필수 public 규칙 누락을 함께 재확인했습니다.
각각 `BLOCKED`와 `NEEDS_CONTEXT`를 구분했고 독립 승인 작업은 진행했습니다. 이 첫 보완은
template의 마지막 상태 정의에만 적용했습니다. 여기까지 7회 invocation이며 반복 표본은
없습니다. private 선택·반복 검증·재위임은 baseline에서도
문제가 없어 이번 변경의 개선 효과라고 주장하지 않습니다.

후속 검토에서는 후반의 포괄적인 중단 조건과 승인 부재·접근 거부의 상태 충돌을 확인해
보완했습니다. fresh Astra medium 1응답으로 다섯 상황을 재확인한 결과, 동등한 내부 접근의
불확실성에는 좁은 탐색·검증을 먼저 선택했고, commit 승인 부재와 public 규칙 누락은
`NEEDS_CONTEXT`, 실제 runtime 접근 거부와 runtime 부재는 `BLOCKED`로 구분했습니다.
독립 승인 작업은 계속했습니다.

추가 반례 검토 뒤에는 고정된 commit 승인 선언을 실제 사용자 승인 근거를 채우는
`COMMIT_AUTHORIZATION` 항목으로 바꿨습니다. fresh Astra medium 1응답은 전체 수정 template의
placeholder가 그대로인 경우 `NEEDS_CONTEXT`로 Git 변경 전 확인을 반환했고, 실제 승인 근거가
채워지고 작업·검증이 끝난 경우 승인된 commit을 선택했습니다. 이후 staging·commit 보류와
독립 source edit·검증 계속을 같은 절에 명시하고 fixture에도 계속 조건을 추가했습니다. fresh
Astra medium 1응답은 승인 값이 "없음"인 경우와 placeholder인 경우 모두 staging·commit만
보류하고 독립적인 승인 수정·검증은 계속했습니다. 총 10회 invocation, 동시 최대 2개이며
이 추가 응답도 반복 비교나 실제 Git·검증 실행을 포함하지 않습니다.

설정 안내는 CLI 0.152.1의 읽기 전용 `features list`로 두 키를 각각 단독 적용해 확인했습니다.
baseline과 `-c agents.enabled=true`, `-c agents.enabled=false`는 모두 `multi_agent=true`,
`-c features.multi_agent=true`는 true, `-c features.multi_agent=false`는 false였습니다.
5회 모두 exit 0이었고 사용자 설정 파일은 수정하지 않았습니다. 이 결과는 확인한 CLI 버전과
실행 환경의 설정 효과에 한정합니다. 앞선 `doctor --json` 실험은 feature flag를 함께 강제했으므로
두 키의 독립 효과를 판별하는 근거로 사용하지 않습니다. 그 진단의 `config.load`는 `ok`였지만
전체 진단은 `TERM=dumb` 때문에 exit 1이므로 전체 환경 검사 통과도 주장하지 않습니다.

위 모델·effort는 spawn **요청값**입니다. 현재 생성 응답은 task 이름만 반환해 native 실제
model/effort는 `unknown`으로 기록합니다. 자기보고나 요청값을 적용 확인으로 대체하지 않습니다.
나머지 fixture 전체의 모델 기반 실행, 위의 구현 성능·비용 비교표, native UI에서 전체 workflow
실행은 `not_run`입니다. decision probe의 조건부 응답을 실제 모델 routing·파일 수정·게이트
완료·비용 개선으로 일반화하지 않습니다.

## 간결한 리뷰와 기본 동작 (prior baseline)

`review-respects-confirmed-provider-default`부터 `review-allows-equivalent-simple-implementation`까지
일곱 사례는 확인된 기본 동작, 실제 override, 추측성 timeout 제안, 부족한 기본값, 판정에 필수인
불확실성, 잘못된 Important 지적과 불필요한 추상화를 구분합니다. 사례에 쓰인 숫자와 framework 동작은
합성 fixture에서 정한 계약이며, 실제 Terraform provider나 framework의 기본값을 주장하지 않습니다.
새 사례의 모델 기반 실행은 `not_run`입니다. JSON 구조 검사와 문서 리뷰를 오탐 감소나 실제
장기 workflow 개선의 증거로 취급하지 않습니다.

`review-reports-structural-cost-without-runtime-bug`부터 다섯 사례는 동작이 맞아도 구조 문제를
보고하는지, 비차단 개선과 명시된 아키텍처 계약 위반을 구분하는지, 파일 길이·호출자 수만으로
불필요한 분할·삭제를 요구하지 않는지 평가합니다. 이 사례도 합성 계약이며 모델 실행은
`not_run`입니다. 기존의 기본값·override·추측성 timeout 사례도 유지합니다.

## 승인 범위와 절차 전환 (prior baseline)

`approval-boundary-*` 사례는 기존 승인 유지, 설계 전용, 구현 전 확인, 미정 규칙과 독립 작업,
Git 권한을 구분한다. 현재 지침을 적용한 실제 다음 행동을 기대값과 대조한다. 문서의 특정
문구나 DOT 노드 유무만으로 이 동작을 검증하지 않는다. 단순 설명의 과도한 호출은
[스킬 선택 사례](../skill-routing/cases.json)의 `engineering-short-*`로 함께 확인한다.
