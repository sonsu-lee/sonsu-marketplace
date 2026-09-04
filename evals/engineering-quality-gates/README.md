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

- gate는 exact artifact revision에 묶이고 변경 후 이전 결과는 stale입니다.
- deterministic failure는 전체 workflow가 아니라 실패를 고칠 수 있는 stage로 돌아갑니다.
- retry에는 artifact, hypothesis, evidence, context, evaluator 또는 capability 변화가 필요합니다.
- tool·permission·external state 부재는 `blocked`이며 동일 명령을 반복하지 않습니다.
- retry cap의 valid required finding은 human `accepted_risk` 없이 `passed`나 `complete`가 아닙니다.
- quality gate와 Git·PR·publish authorization은 독립적으로 판정합니다.
- subagent capability가 있어도 task commit 승인이 없으면 plan 실행은 `executing-plans`에 남고
  `subagent-driven-development`로 순환하지 않습니다.
- Fast Path는 모든 predicate가 확인된 plan 없는 작업에만 적용되고 숨은 복잡성이 나오면 즉시 일반 workflow로 올라갑니다.
- Fast Path의 숨은 복잡성 upgrade와 red-team의 변경 입력 기반 재시도는 flow diagram에서도 실제로 도달 가능해야 합니다.
- Fast Path eligibility와 실행 전 classification은 quality `passed`가 아니며 정상 escalation도 quality failure가 아닙니다.
- Code Mode는 결정론적 실행 수단이며 Fast Path 적합성이나 품질 통과의 증거가 아닙니다.
- plan-backed 완료에는 일반 최종 리뷰와 별개의 fresh-context red-team 판정이 필요합니다.
- red-team의 목표·요구사항·설계·plan·전체 diff·검증·관찰 결과·review provenance는 source 경로가
  아니라 하나의 content-digested bundle 안에 고정되어야 합니다.
- SDD review package는 binary patch를 포함하고 같은 range를 다시 생성해도 기존 package를
  덮어쓰지 않아야 합니다.
- red-team이 원래 문제 정의나 사용자 목표를 무효화하면 brainstorming만으로 닫지 않고 사용자 재승인으로 돌아갑니다.
- red-team 직전에는 현재 HEAD의 전체 변경 package를 다시 고정하고, 잘못된 기존 review finding은
  verdict·칭찬이 제거된 finding-to-fix provenance로 반증한 뒤 근거와 함께 무효화하여 영향 task를
  다시 엽니다.
- SDD workspace는 local merge와 merge 결과 검증 전까지 보존합니다.
- 모델과 reasoning effort는 역할별로 함께 선택하며 goal은 명시적으로 요청된 plan에 최대 하나입니다.
