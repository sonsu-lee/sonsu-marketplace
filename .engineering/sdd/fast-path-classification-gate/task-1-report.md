# Task 1 report

## 구현 내용

F1/F2를 위한 `fast-path-routing.test.sh`와 F3를 위한 `fix-handoff.test.sh`를 RED 상태로 추가했다. routing 테스트는 독립 classifier 표식과 Fast Path 실행 순서, escalation에서 predicate/execution으로 돌아가는 금지 edge, 새 프로세스에서 persisted `disqualified`가 `eligible`로 바뀌지 않는 state helper 계약을 검사한다. handoff 테스트는 exact-key finding/verification evidence, round 2, revision, bundle digest와 tamper/forbidden-key 검사를 수행하도록 작성했다.

## F1/F2/F3 mapping

- F1: `fast-path-routing.test.sh`의 classifier-before-execution ordering 및 state-helper 호출
- F2: escalation의 Fast Path 재진입 금지 graph 검사와 별도 프로세스 latch 검사
- F3: `fix-handoff.test.sh`의 immutable bundle create/verify, digest, exact schema 및 금지 키 검사

## Material deviation

없음. production 파일과 문서는 수정하지 않았으며 plan Task 1의 두 테스트 파일과 이 report만 추가했다.

## RED 검증

실행 명령:

```text
bash plugins/engineering/skills/brainstorming/tests/fast-path-routing.test.sh
bash plugins/engineering/skills/executing-plans/tests/fix-handoff.test.sh
```

관찰 결과:

```text
routing_exit=1
FAIL: .../plugins/engineering/skills/brainstorming/SKILL.md does not contain: Fast Path classifier
handoff_exit=1
.../plugins/engineering/skills/executing-plans/scripts/fix-handoff: No such file or directory
```

두 실패 모두 Task 2/3 production helper 및 classifier 계약이 아직 없는 것이 원인이다. handoff는 brief가 지정한 exit 127 누락 경로를 직접 호출한다. routing은 helper 호출 전에 현재 routing graph에 classifier 표식이 없음을 결정론적으로 검출한다.

## 변경 파일

- `plugins/engineering/skills/brainstorming/tests/fast-path-routing.test.sh`
- `plugins/engineering/skills/executing-plans/tests/fix-handoff.test.sh`
- `.engineering/sdd/fast-path-classification-gate/task-1-report.md`

## 자체 리뷰

테스트는 `set -euo pipefail`, 임시 디렉터리 cleanup trap, 절대 helper 경로 계산을 사용한다. forbidden finding keys `suggested_fix`, `verdict`, `rationale`, `authority`, `unexpected`와 verification keys `conclusion`, `status`, `unexpected`를 각각 명시적으로 검사한다. 현재 RED가 assertion/파싱 결함이 아니라 의도한 누락에서 멈추는 것을 확인했다.

## 우려 사항

Task 2/3가 최종 helper CLI 이름과 출력 형식을 이 테스트의 계약(`fast-path-state`, `fix-handoff create/verify/validate-*`)에 맞춰 제공해야 한다. classifier 문구가 다른 표현으로 문서화되면 routing test의 의도는 유지하되 표식 assertion을 구현 계약에 맞춰 조정해야 한다.
