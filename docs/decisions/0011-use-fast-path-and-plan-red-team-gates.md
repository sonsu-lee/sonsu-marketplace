# 0011 Use Fast Paths and Plan-Backed Red-Team Gates

- Status: Accepted
- Date: 2026-09-04
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-04 현재 대화에서 Fast Path, Code Mode, 최대 3회 retry, plan 기반 fresh-context red-team, Codex model·reasoning effort와 goal lifecycle 방향을 명시적으로 승인했습니다.

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

## Decision

Engineering은 기존 [0007 stage-owned quality gate](0007-use-stage-owned-quality-gates.md)와 권한
분리를 유지하면서 다음 계약을 추가하고 일부 실행 기준을 구체화합니다.

1. `bounded` 요청 중 명확한 결과, 닫힌 영향 범위, 결정론적 검증과 가역성을 모두 갖춘 작업은
   plan 없는 Fast Path로 실행할 수 있습니다. 효과가 국소적인 Local Fast Path와 동일 규칙을
   재현할 수 있는 Mechanical Fast Path를 구분합니다. controller는 target discovery 전에 stable
   todo ID를 고정하거나 UUID를 한 번만 만들고, 이를 target에서 다시 유도하지 않습니다.
   모든 Fast Path entry에서 `.engineering/fast-path/<task_id>.state`를 확인해 `disqualified`
   latch를 먼저 거부합니다. 조건이 하나라도 확인되지 않거나 classifier를 사용할 수 없으면
   일반 workflow로 올리고, 같은 task는 Fast Path에 다시 들어올 수 없습니다.
2. Fast Path 요청 자체에 대상·결과·완료 조건이 명확하면 이를 승인된 짧은 설계로 취급합니다.
   controller의 표적 탐색 1회와 fresh-context classifier의 독립 표적 탐색 1회만 허용하므로 전체
   search budget은 2회입니다. classifier는 controller의 자기 판정을 대신하지 않으며 `eligible`은
   controller가 capture한 exact candidate revision과 일치하는 revision 및 64-character lowercase
   SHA-256 evidence digest를 state에 기록할 때만 성립합니다. missing revision, revision mismatch,
   false 또는 unknown predicate는 fail closed합니다. 구현과 집중 수정은 각 1회로 제한하며, 예상 밖
   의존성이나 두 번째 의미 판단이 드러나면 `disqualified`를 영속 기록하고 Fast Path를 종료합니다.
3. Code Mode는 결정론적 탐색·변환·검증의 실행 수단입니다. Code Mode를 사용할 수 있다는 사실은
   Fast Path 적합성이나 품질 통과의 근거가 아니며, 실제 consumer와 postcondition을 별도로
   검증합니다.
4. 자동 review/fix loop는 최대 3회입니다. task fix는 1회차에 원래 implementer를 사용하고,
   2~3회차에는 exact task brief, exact-revision binary-safe artifact package, exact-key normalized
   finding-evidence JSON 및 verification-evidence JSON만 immutable bundle에 고정해 fresh-context
   implementer에게 전달합니다. 이 implementer는 이전 report, implementation narrative, rationale,
   self-review, completion verdict, reviewer verdict, agent identity와 session history를 받지 않습니다.
   읽기·추출·수정 전 canonical `fix-handoff verify BUNDLE DIGEST`를 실행하고, 성공한 뒤 stdout의
   verified `Extracted:` snapshot만 읽습니다. 3회차에는 해당 task에 적합한 상위 capability를
   적용하며 상한의 미해결 필수 finding은 자동 통과하지 않습니다.
5. 구현 plan이 존재하는 모든 작업은 현재 exact revision의 전체 결정론적 검증과 일반 final review 뒤에 별도의
   fresh-context red-team gate를 거칩니다. 이는 위험도 분류가 아니라 plan artifact 존재로
   trigger합니다. reviewer는 목표·요구사항·설계·의사코드·plan·전체 diff·검증 근거를 바탕으로
   지금까지의 전제를 반증하며 구현에 참여하거나 코드를 수정하지 않습니다. 이 모든 입력은
   경로 포인터가 아니라 하나의 immutable content bundle에 복사하고 bundle 전체 digest로 고정합니다.
6. red-team verdict는 `survives_challenge`, `invalidated`, `inconclusive`, `blocked`를 사용합니다.
   첫 verdict만 quality gate의 `passed`로 연결합니다. 나머지는 가장 가까운 소유 단계로
   반환하며, artifact가 바뀌면 현재 exact revision의 deterministic verification, ordinary whole-change
   review 및 immutable red-team bundle을 다시 고정합니다. 최대 3개의 서로 다른 fresh-context reviewer
   뒤에는 `decision_required`로 중단합니다.
7. generic skill은 capability tier만 정의하고, Codex 전용 reference가 허용된 model과
   `reasoning_effort`를 함께 mapping합니다. 사용할 수 없는 조합의 fallback은 기록하며
   `max`·`ultra`를 기본값으로 사용하지 않습니다.
8. Codex goal은 사용자가 명시적으로 요청한 plan-backed 작업에 최대 하나만 사용합니다. 세부
   task는 todo와 ledger로 추적하고, 필수 final review와 red-team gate까지 끝나야 goal을 완료할
   수 있습니다. 평범한 요청에서 goal이나 token budget을 추론하지 않습니다.

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

명확하고 결정론적인 변경은 독립 classifier의 확인 뒤 제한된 탐색 비용으로 끝낼 수 있습니다.
단순하다고 분류한 작업이 예상보다 커지거나 classifier가 non-eligible 또는 unavailable이면,
`disqualified` latch를 먼저 기록하고 남은 Fast Path budget을 소비하지 않은 채 일반 workflow로
올라갑니다. 계획이 필요한 작업은 코드가 요구사항을 만족한다는 일반 리뷰 외에 요구사항과
접근 자체를 부정하는 독립 검토를 받습니다.

red-team은 강한 model과 새 context를 사용하므로 plan-backed 작업의 비용이 증가합니다. 이를
plan 존재라는 고정 trigger, 최대 3회 상한, immutable artifact package와 역할별 model routing으로
제한합니다. Fast Path classifier와 evidence-only handoff의 실제 runtime model compliance, 그리고
품질·비용 효과는 deterministic fixture나 native loading만으로 입증되지 않으며 별도 승인된 behavior
evaluation이 필요합니다.

## Revisit When

Fast Path의 false positive로 public contract나 숨은 dependency를 반복해서 놓칠 때, 단순 작업의
평균 turn이 줄지 않을 때, red-team finding이 일반 리뷰를 중복하거나 억지 반례를 반복할 때,
fresh-context 비용이 품질 개선보다 클 때 다시 검토합니다. Codex의 model allowlist, reasoning
effort, Code Mode 또는 goal tool 계약이 바뀔 때에는 Codex 전용 reference를 먼저 갱신합니다.
