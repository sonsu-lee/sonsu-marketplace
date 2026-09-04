# Engineering quality gate 평가

`cases.json`은 Engineering workflow가 quality gate 실패를 가장 가까운 소유 단계로 되돌리고,
동일 입력을 무한 재시도하거나 실제 finding을 자동 통과시키지 않는지 확인하는 behavior fixture입니다.

각 case는 초기 상태와 사건, 기대 status, return target, retry 조건과 금지된 결론을 선언합니다.
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
`fail`, `blocked`, `inconclusive`, `not_run`으로 구분합니다. case 안의 `expected.status`는
평가 결과가 아니라 예상되는 Engineering gate status입니다. 실행하지 않은 case는
`not_run`으로 보고합니다.

검토할 핵심 불변식은 다음과 같습니다.

- gate는 exact artifact revision에 묶이고 변경 후 이전 결과는 stale입니다.
- deterministic failure는 전체 workflow가 아니라 실패를 고칠 수 있는 stage로 돌아갑니다.
- retry에는 artifact, hypothesis, evidence, context, evaluator 또는 capability 변화가 필요합니다.
- tool·permission·external state 부재는 `blocked`이며 동일 명령을 반복하지 않습니다.
- retry cap의 valid required finding은 human `accepted_risk` 없이 `passed`나 `complete`가 아닙니다.
- quality gate와 Git·PR·publish authorization은 독립적으로 판정합니다.
- Fast Path는 모든 predicate가 확인된 plan 없는 작업에만 적용되고 숨은 복잡성이 나오면 즉시 일반 workflow로 올라갑니다.
- Code Mode는 결정론적 실행 수단이며 Fast Path 적합성이나 품질 통과의 증거가 아닙니다.
- plan-backed 완료에는 일반 최종 리뷰와 별개의 fresh-context red-team 판정이 필요합니다.
- 모델과 reasoning effort는 역할별로 함께 선택하며 goal은 명시적으로 요청된 plan에 최대 하나입니다.
