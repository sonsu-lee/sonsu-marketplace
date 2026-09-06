# Engineering quality gate 평가

`cases.json`은 Engineering workflow가 quality gate 실패를 가장 가까운 소유 단계로 되돌리고,
동일 입력을 무한 재시도하거나 실제 finding을 자동 통과시키지 않는지 확인하는 behavior fixture입니다.

각 case는 초기 상태와 사건, 해당 stage의 기대 outcome, return target, retry 조건과 금지된 결론을 선언합니다.
평가자는 해당 Engineering plugin만 설치한 격리된 읽기 전용 fixture에서 prompt를 실행하고 실제
응답과 tool trace를 기대값에 대조해야 합니다. Quality Engineering, Workflow 또는 다른
플러그인의 존재를 가정하지 않습니다.

`retry_requires_changed_input`은 workflow가 다시 진행될 때 artifact, evidence, context,
evaluator, capability 또는 human decision이 달라져야 하는지를 뜻합니다.
`automatic_retry_allowed`는 현재 controller가 human/external change 없이 다음 retry를 시작할
수 있는지를 별도로 나타냅니다. retry가 적용되지 않는 passed case의 `false`와, retry 전에
변화가 필요하다는 조건을 혼동하지 않습니다.

JSON 파싱과 schema field 검사는 fixture의 구조만 확인합니다. 실제 model behavior를 입증하지
않습니다. 모델 기반 실행에는 별도의 model·비용·반복 횟수 승인이 필요하며 평가 결과를 `pass`,
`fail`, `blocked`, `inconclusive`, `not_run`으로 구분합니다. quality gate가 실제로 실행된 case의
`expected.status`는 평가 결과가 아니라 예상되는 Engineering gate status입니다. 실행 전
classification과 정상 escalation은 `quality_status`, `classification_outcome`,
`execution_outcome`처럼 해당 stage의 outcome field를 사용하며 `passed`나 `failed`를 억지로
부여하지 않습니다. 실행하지 않은 case는 `not_run`으로 보고합니다.

검토할 핵심 불변식은 다음과 같습니다.

- artifact 변경 뒤 이전 판정을 그대로 복사하지 않습니다. bounded fix는 영향받지 않은 이전 근거,
  현재 delta, scoped checks/review와 impact rationale를 합쳐 현재 gate를 갱신할 수 있습니다.
- deterministic failure는 전체 workflow가 아니라 실패를 고칠 수 있는 stage로 돌아갑니다.
- retry에는 artifact, hypothesis, evidence, context, evaluator 또는 capability 변화가 필요합니다.
- 자동 task review/fix, design/plan review, whole-change review와 red-team은 정확히 최대 5회이며,
  상한은 변경 없는 입력이나 같은 evaluator를 반복할 권한이 아닙니다. session·owner·handoff로
  초기화되지 않고 nested loop도 상위 gate의 남은 budget을 소비합니다.
- tool·permission·external state 부재는 `blocked`이며 동일 명령을 반복하지 않습니다.
- retry cap의 valid required finding은 human `accepted_risk` 없이 `passed`나 `complete`가 아닙니다.
- quality gate와 Git·PR·publish authorization은 독립적으로 판정합니다.
- subagent capability가 있어도 task commit 승인이 없으면 plan 실행은 `executing-plans`에 남고
  `subagent-driven-development`로 순환하지 않습니다.
- Fast Path controller는 target discovery 전에 stable task ID를 고정하고 실제 현재 파일을 최대 2회
  targeted search로 확인합니다. classifier subagent는 필수가 아니며 persisted `eligible`이나
  `HEAD` 일치를 승인으로 replay하지 않습니다.
- persistent state는 stable task ID의 search·execution consumption과 `disqualified`를 보존합니다.
  resumption·context loss·handoff·unexplained drift는 일반 workflow로 올리고 budget을 초기화하지 않습니다.
- Fast Path 최초 구현과 한 번의 집중 수정은 중단 없는 같은 실행에서만 허용합니다. false·unknown
  predicate와 실행 중 숨은 복잡성은 `disqualified`를 기록한 뒤 가장 가까운 일반 workflow로 routing합니다.
- Fast Path의 숨은 복잡성 upgrade와 red-team의 변경 입력 기반 재시도는 flow diagram에서도 실제로 도달 가능해야 합니다.
- Fast Path eligibility와 실행 전 classification은 quality `passed`가 아니며 정상 escalation도 quality failure가 아닙니다.
- Code Mode는 결정론적 실행 수단이며 Fast Path 적합성이나 품질 통과의 증거가 아닙니다.
- plan-backed 완료에는 일반 최종 리뷰와 별개의 fresh-context red-team 판정이 필요합니다.
- task fix 1~3회차는 원래 implementer가 직접 이어서 수행하고 4~5회차는 fresh context와 충분한
  capability를 사용합니다. handoff는 task, current artifact, 원래 finding, 실패한 시도와 test evidence를
  간결하게 보존하며 사실과 가설을 구분합니다. 이전 대화 전체·자기 정당화·칭찬·verdict는 제외하고
  strict JSON, tar 또는 전용 helper protocol을 필수화하지 않습니다.
- 최초 ordinary whole-change review와 최초 independent whole-goal red-team은 필수입니다. bounded fix는
  영향 기반 근거 합성으로 current gate를 갱신하고 material goal·contract·design·dependency 변경이나
  unknown impact에서만 full review를 다시 엽니다.
- red-team의 목표·요구사항·설계·plan·전체 diff·검증·관찰 결과·review provenance는 source 경로가
  아니라 하나의 content-digested bundle 안에 고정되어야 합니다.
- SDD review package는 binary patch를 포함하고 같은 range를 다시 생성해도 기존 package를
  덮어쓰지 않아야 합니다.
- red-team이 원래 문제 정의나 사용자 목표를 무효화하면 brainstorming만으로 닫지 않고 사용자 재승인으로 돌아갑니다.
- bounded fix의 fresh red-team은 현재 full bundle을 사용할 수 있지만 이전 challenge와 fix regression을
  scoped recheck합니다. 결함 수를 강제하지 않고 새로운 scope 아이디어만으로 차단하지 않습니다.
- red-team 직전에는 현재 HEAD의 전체 변경 package를 다시 고정하고, 잘못된 기존 review finding은
  verdict·칭찬이 제거된 finding-to-fix provenance로 반증한 뒤 근거와 함께 무효화하여 영향 task를
  다시 엽니다.
- SDD workspace는 local merge와 merge 결과 검증 전까지 보존합니다.
- 모델과 reasoning effort는 uncertainty·risk와 예상 총 시간·비용을 함께 보고 선택합니다. goal은
  명시적으로 요청된 plan에 최대 하나이며 test totals가 아니라 관찰 가능한 사용자 결과를 추적합니다.

이 fixture는 선언된 입력·출력과 금지 경로를 평가하기 위한 data contract입니다. JSON parser, shell test,
native loading과 model 실행 결과를 구분합니다. 특히 fixture 통과는 runtime model compliance나 실제
품질·비용 효과를 주장하지 않습니다.

## Codex 모델·prompt 변경 비교

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

### 2026-09-06 구현자 decision probe

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
