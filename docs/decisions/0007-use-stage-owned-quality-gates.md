# 0007 Use Stage-Owned Quality Gates with Bounded Backtracking

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-02 현재 대화에서 검토한 설계 방향의 적용과 PR 작성을 명시적으로 승인했습니다.

## Context

Engineering에는 설계 승인, task verification, subagent task review,
completion verification처럼 부분적인 gate가 이미 있지만, gate 결과와 재시도·되돌림 규칙은
skill마다 달랐습니다. 특히 retry 한도에 도달한 실제 review finding을 `parked`로 남기고 task를
완료할 수 있어 `passed`와 미해결 위험을 구분하기 어려웠고, inline 실행은 subagent 실행보다
whole-change review 경계가 약했습니다.

외부 연구는 모델이 자기 출력만 보고 반복 수정하는 방식보다 정답 신호나 외부 verifier를 제공한
수정이 더 신뢰할 만하며, 오류 위치를 제공하면 수정 성능이 좋아질 수 있음을 보고합니다. 반복
검증은 개선을 만들 수 있지만 후반 round에서 regression이 늘 수 있어 상한과 early stop이
필요합니다.

- [When Can LLMs Actually Correct Their Own Mistakes?](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177/When-Can-LLMs-Actually-Correct-Their-Own-Mistakes)
- [LLMs Cannot Find Reasoning Errors, but Can Correct Them!](https://aclanthology.org/2024.findings-acl.826/)
- [DeepVerifier](https://aclanthology.org/2026.findings-acl.1243/)

Anthropic과 OpenAI의 engineering 글도 명확한 평가 기준, 환경에서 얻는 ground truth,
deterministic check, checkpoint, blocker와 최대 반복 횟수를 강조합니다. 이 자료는 실무 패턴의
근거지만 각 회사의 자체 시스템에 대한 자기보고이므로 독립적인 효과 증명으로 취급하지
않습니다.

- [Anthropic: Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)
- [OpenAI: Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)

## Decision

Engineering은 공통 gate 상태·증거 계약과 단계별 소유권을 결합합니다. 중앙
`quality-gate` skill이나 전체 workflow의 재귀 호출은 만들지 않습니다. `brainstorming`,
`writing-plans`, task execution/review, final verification과 branch completion이 각자 생성한
artifact의 gate, pass 조건과 가장 가까운 return target을 소유합니다.

gate는 exact artifact revision에 묶고 `passed`, `failed`, `blocked`, `inconclusive`,
`not_run`, `not_applicable`, `accepted_risk`를 구분합니다. artifact가 바뀌면 이전 결과는
stale입니다. deterministic check를 inferential review보다 먼저 실행하고, 독립 evaluator는
architectural/high-risk 문서, cross-component·long-running·high-risk plan, subagent task, major/high-risk inline
change와 whole change처럼 의미 있는 경계에 사용합니다.

실패는 전체 workflow를 다시 시작하지 않고 가장 가까운 소유 단계로 되돌립니다. 같은 artifact와
입력에 대한 동일 재시도는 금지하며, retry는 artifact, hypothesis, implementation, evidence,
context, evaluator 또는 capability가 달라져야 합니다. 각 loop에는 유한한 상한을 둡니다.
상한에 도달한 실제 필수 finding은 자동으로 `passed`나 `complete`가 되지 않습니다. 현재
revision의 위험을 명시적으로 수락할 권한은 사용자 또는 확인된 human decision-maker에게만
있으며, `accepted_risk`는 `passed`와 별도로 기록합니다.

quality gate와 authorization gate는 분리합니다. 품질 통과는 document write, implementation,
commit, push, PR, merge, deploy 또는 publish 권한을 부여하지 않습니다.

Engineering 내부 gate는 Quality Engineering 플러그인에 의존하지 않습니다. 사용자가 특정
quality lens를 요청하면 runtime에서 두 플러그인을 조합할 수 있지만 Engineering skill에서
Quality Engineering skill ID를 필수 호출하지 않습니다.

## Alternatives Considered

- skill마다 독립적인 gate 규칙 유지: 작은 변경은 단순하지만 상태 의미와 cap 이후 처리가 계속
  달라지고 `passed`와 미해결 위험을 합치기 쉽습니다.
- 중앙 `quality-gate` skill과 재귀 router 추가: 계약은 한곳에 모이지만 모든 artifact와
  authorization을 아는 대형 orchestrator가 되고 플러그인 독립성과 stage context를 약화시킵니다.
- 공통 계약과 stage-owned gate 결합: 공통 상태와 안전 규칙을 재사용하면서 실패를 실제로
  고칠 수 있는 가장 가까운 단계에 보냅니다. 이 대안을 선택합니다.

## Consequences

gate 결과, 실제 검증 증거, 미실행·판정 불가와 accepted risk가 구분됩니다. 변경된 revision은
다시 검증해야 하고, 실패는 전체 restart가 아니라 targeted backtracking으로 처리됩니다.
independent review와 반복은 위험한 artifact 경계에 제한되므로 모든 사소한 문서·metadata 변경에
같은 비용을 부과하지 않습니다.

반면 각 stage는 gate record와 return target을 유지해야 하므로 지침과 progress ledger가 조금
길어집니다. 고위험 gate에 필요한 evaluator나 도구가 없으면 예전처럼 묵시적으로 진행하지 않고
`blocked`, `not_run` 또는 human `accepted_risk`로 드러나므로 작업이 의도적으로 멈출 수
있습니다. 이 결정의 실제 품질·비용 효과는 아직 관찰되지 않았고 behavior evaluation이
필요합니다.

## Revisit When

실제 실행에서 stage 간 ping-pong, 동일 finding의 반복, 과도한 reviewer 비용, 낮은 false-positive
조정 품질 또는 gate record 누락이 반복될 때 재검토합니다. Codex가 안정적인 artifact revision,
evaluator calibration 또는 workflow state-machine 계약을 제공할 때도 현재 prose 기반 계약과
attempt cap을 다시 검토합니다.
