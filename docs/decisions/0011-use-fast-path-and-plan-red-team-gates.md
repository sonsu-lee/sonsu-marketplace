# 0011 Use Fast Paths and Plan-Backed Red-Team Gates

- Status: Accepted
- Date: 2026-09-04
- Last amended: 2026-09-05
- Supersedes: None
- Superseded by: None
- Related: [0012](0012-use-role-routing-and-execution-evidence.md) refines role routing, early fresh handoff and execution evidence; other gates remain unchanged.
- Approval: 사용자가 2026-09-04 현재 대화에서 Fast Path, Code Mode, plan 기반 fresh-context red-team, Codex model·reasoning effort와 goal lifecycle 방향을 승인했고, 2026-09-05에 최대 5회 상한과 research 기반 단순화를 승인했습니다.

## Context

Engineering의 단계별 품질 게이트는 실패를 가장 가까운 소유 단계로 되돌리지만, 단순한 변경에도
별도 설계 승인과 넓은 탐색이 필요했고 `subagent-driven-development`의 task fix loop는 최대
5회였습니다. 반대로 일반적인 최종 리뷰는 승인된 요구사항과 코드 품질을 중심으로 판정해,
문제 정의·설계·계획·리뷰 방향 자체가 잘못됐는지 전체 구조를 반증하는 독립 단계는 없었습니다.

파일 수나 diff 크기만으로 단순성을 판단하면 한 줄의 public contract 변경을 과소평가하거나,
여러 파일의 결정론적 rename을 과대평가할 수 있습니다. 위험도를 먼저 정확히 분류해야만
red-team을 실행하는 방식도 분류 오류가 검토 누락으로 이어질 수 있습니다.

Codex는 역할별 model과 reasoning effort, 격리된 subagent context, Code Mode와 goal 도구를
제공할 수 있지만 Engineering의 generic 계약과 Codex 전용 mapping이 분리돼 있지 않았습니다.

설계 동기는 원본 [`subagent-driven-development`](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/subagent-driven-development/SKILL.md)의 implement-review 반복 구조와 [무한 review/test ratchet 사례](https://github.com/obra/superpowers/issues/2112), 반복 피드백을 다음 시도에 사용하는 [Reflexion](https://arxiv.org/abs/2303.11366), 요구사항이 여러 turn에 나뉠 때 premature assumption과 anchoring이 누적되는 현상을 다룬 [LLMs Get Lost In Multi-Turn Conversation](https://arxiv.org/html/2505.06120v1), agent system의 coordination과 성능 관계를 다룬 [scaling 연구](https://arxiv.org/abs/2512.08296v3)에서 얻었습니다. 이 자료는 bounded retry, fresh context와 비용 인식 routing의 방향을 뒷받침하는 참고 자료이며, 아래 계약이 Codex에서 더 높은 품질이나 성능을 낸다는 직접적인 경험적 검증은 아닙니다.

## Decision

Engineering은 기존 [0007 stage-owned quality gate](0007-use-stage-owned-quality-gates.md)와 권한
분리를 유지하면서 다음 계약을 추가하고 일부 실행 기준을 구체화합니다.

1. `bounded` 요청 중 명확한 결과, 닫힌 영향 범위, 결정론적 검증과 가역성을 모두 갖춘 작업은
   plan 없는 Fast Path로 실행할 수 있습니다. 효과가 국소적인 Local Fast Path와 동일 규칙을
   재현할 수 있는 Mechanical Fast Path를 구분합니다. controller는 target discovery 전에 stable
   task ID를 고정하고 실제 현재 파일과 consumer를 최대 2회의 targeted search로 확인합니다.
   별도 classifier subagent는 필수가 아니며, 과거 `eligible` 기록이나 `HEAD` 일치는 미커밋 변경을
   포함한 현재 상태의 승인으로 사용하지 않습니다.
2. 영속 Fast Path state에는 stable task ID별로 소비한 search·execution budget과 `disqualified`만
   기록합니다. 최초 구현과 한 번의 집중 수정은 같은 중단 없는 실행 안에서 허용합니다. resumption,
   context loss, handoff, 설명되지 않는 파일 drift 또는 추가 의미 판단이 발생하면 `disqualified`를
   기록하고 일반 workflow로 올립니다. task ID·session·owner를 바꾸어 예산을 초기화하지 않으며,
   legacy positive eligibility record는 replay하지 않습니다.
3. Code Mode는 결정론적 탐색·변환·검증의 실행 수단입니다. Code Mode를 사용할 수 있다는 사실은
   Fast Path 적합성이나 품질 통과의 근거가 아니며, 실제 consumer와 postcondition을 별도로
   검증합니다.
4. 자동 task review/fix, design/plan review, whole-change review와 red-team loop는 각각 최대 5회입니다.
   task fix 1~3회차는 원래 implementer가 직접 이어서 수정할 수 있고, 4~5회차는 fresh context와
   작업에 충분한 capability를 사용합니다. fresh handoff에는 task, 현재 artifact, 원래 finding,
   실패한 시도와 실제 test evidence를 간결하게 전달하며 사실과 가설을 구분합니다. 이전 대화 전체,
   자기 정당화, 칭찬, completion/reviewer verdict는 전달하지 않습니다. 특정 JSON key, tar layout이나
   helper command를 handoff의 필수 조건으로 만들지 않습니다. 5회 뒤 유효한 필수 finding은 자동
   통과하지 않으며 사람의 결정을 기다립니다.
5. 구현 plan이 존재하는 모든 작업은 현재 전체 변경의 결정론적 검증과 일반 whole-change review 뒤에
   별도의 fresh-context red-team gate를 최초 한 번 수행합니다. reviewer는 목표·요구사항·설계·의사코드·
   plan·전체 diff·검증 근거를 바탕으로 전제를 독립적으로 검토하며 구현에 참여하거나 코드를 수정하지
   않습니다. 목표는 결함 수를 채우는 것이 아니며 근거 있는 결함이 없으면 통과할 수 있습니다.
6. red-team verdict는 `survives_challenge`, `invalidated`, `inconclusive`, `blocked`를 사용합니다.
   첫 verdict만 quality gate의 `passed`로 연결합니다. bounded fix 뒤에는 현재 전체 bundle을 계속
   제공하되 fresh reviewer가 이전 challenge와 fix regression을 scoped recheck합니다. 일반 gate도
   영향받지 않은 이전 whole-review 근거, 실제 delta, scoped checks/review와 impact rationale을 합쳐
   현재 상태를 판정할 수 있습니다. material goal·contract·design·dependency 변경 또는 영향이
   불명확할 때에만 해당 whole review와 full challenge를 다시 엽니다. 새로운 scope 아이디어는
   승인 범위의 결함과 분리하며 자동으로 차단하지 않습니다.
7. 모든 자동 loop의 5회 상한은 session, owner 또는 소유 단계 반환으로 초기화하지 않습니다. nested
   호출은 상위 task/gate의 남은 예산 안에서만 수행합니다. generic skill은 capability tier를
   uncertainty, regression risk, 독립 판단 필요성 및 예상 총 시간·비용으로 선택하고, Codex 전용
   reference가 허용된 model과 `reasoning_effort`를 함께 mapping합니다. 파일 수만으로 tier를 정하거나
   `max`·`ultra`를 기본값으로 사용하지 않습니다.
8. Codex goal은 사용자가 명시적으로 요청한 plan-backed 작업에 최대 하나만 사용합니다. goal은
   test 개수나 gate 통과 수가 아니라 사용자가 요청한 관찰 가능한 결과를 추적합니다. 세부 task는
   todo와 ledger로 추적하고 필수 final review와 red-team gate까지 끝나야 완료할 수 있습니다.
   평범한 요청에서 goal이나 token budget을 추론하지 않습니다.

0007의 exact revision, 상태 구분, changed-input retry, nearest-owner return과 authorization 분리
원칙은 계속 적용합니다. 이번 결정은 독립 reviewer 적용 기준, retry cap과 Codex 실행 routing을
더 구체화합니다.

## Alternatives Considered

- 모든 변경에 같은 독립 red-team 적용: 누락은 줄지만 plan 없는 오탈자·metadata 변경에도 가장
  비싼 검토 비용을 부과합니다.
- 위험도 판정 뒤 고위험 작업만 red-team 적용: 비용은 낮지만 잘못된 초기 분류가 전체 구조
  검토의 누락으로 직결됩니다.
- plan artifact를 trigger로 red-team 적용하고 plan 없는 Fast Path를 제한: 관찰 가능한 경계로
  검토 비용을 제어하면서 계획된 작업의 전제를 항상 독립적으로 반증할 수 있어 선택했습니다.

## Consequences

명확하고 결정론적인 변경은 controller의 제한된 현재 상태 확인 뒤 끝낼 수 있습니다. 예상보다
범위가 커지거나 실행 연속성이 끊기면 `disqualified`를 기록하고 일반 workflow로 올라갑니다.
계획이 필요한 작업은 코드가 요구사항을 만족한다는 일반 리뷰 외에 요구사항과 접근 자체를
독립적으로 검토받습니다.

red-team은 별도 model과 새 context를 사용할 수 있어 plan-backed 작업의 비용이 증가합니다. 이를
plan 존재라는 고정 trigger, 영향 기반 재검토와 최대 5회 상한으로 제한합니다. Fast Path와
fresh-context review의 실제 runtime model compliance 및 품질·비용 효과는 deterministic fixture나
native loading만으로 입증되지 않으며 별도 승인된 behavior evaluation이 필요합니다.

## Revisit When

Fast Path의 false positive로 public contract나 숨은 dependency를 반복해서 놓칠 때, 단순 작업의
평균 turn이 줄지 않을 때, red-team finding이 일반 리뷰를 중복하거나 억지 반례를 반복할 때,
fresh-context 비용이 품질 개선보다 클 때 다시 검토합니다. Codex의 model allowlist, reasoning
effort, Code Mode 또는 goal tool 계약이 바뀔 때에는 Codex 전용 reference를 먼저 갱신합니다.
