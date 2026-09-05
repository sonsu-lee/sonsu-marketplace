# Engineering

Engineering은 소프트웨어 변경을 계획하고, 구현하고, 디버깅하고, 검증하고, 리뷰할 때 문서 상태를 함께 고려하는 방법입니다. 제한적이고 표적화된 되돌아가기와 단계별 소유 품질 게이트를 사용합니다. 조합 가능한 Codex 스킬을 제공하되 Git 전달, 외부 조사와 출력 언어 지침은 별도 플러그인으로 분리합니다.

Engineering은 현재 독립 플러그인으로 관리하며 독립 semantic version을 사용합니다. 다른 플러그인의 기준선이나 호환 경로를 배포 계약으로 유지하지 않습니다.

## 책임

Engineering은 다음 개발 방법을 담당합니다.

- 변경 내용과 문서에 미치는 영향을 구체화합니다.
- 조건이 모두 확인된 국소·기계적 변경은 plan 없는 Fast Path로 제한된 비용 안에서 처리합니다.
- 결정론적 탐색·변환·검증은 가능한 Codex Code Mode orchestration으로 묶습니다.
- 필요하면 격리된 `worktree`를 재사용하거나 만듭니다.
- 날짜 기반 문서를 자동으로 만들지 않고, 계획이 필요한 작업의 전체 흐름을 의사코드로 먼저 정의합니다.
- 의사코드에서 파일·task별 구현 계획을 도출한 뒤 동작과 회귀 위험에 따라 TDD 또는 다른 검증을 선택합니다.
- 적용되는 커밋 권한 경계 안에서 계획을 직접 실행하거나 subagent와 함께 실행합니다.
- 체계적으로 디버깅하고, 리뷰를 요청하고, 정확한 artifact 리비전을 검증합니다.
- plan-backed 작업은 일반 최종 리뷰 뒤 fresh-context red-team으로 전체 문제 framing을 반증합니다.
- 실패한 게이트를 전체 workflow의 재귀적인 재시작 없이 가장 가까운 소유 단계로 돌려보냅니다.
- 개발 브랜치가 완료되면 통합 방법을 제시합니다.

이 플러그인은 다른 플러그인을 요구하지 않습니다. 직접적인 브랜치, 커밋, ticket, push와 PR 작업은 Workflow가 설치되어 있을 때 독립된 Workflow 플러그인이 담당합니다. 여러 출처를 사용하는 외부 조사는 Research가, 출력 언어 지침은 Fluent Languages가 담당합니다. 요청이 여러 책임에 걸쳐 있으면 Codex가 각 스킬 설명을 바탕으로 이 플러그인들을 함께 선택할 수 있습니다.

## 설치

이 저장소를 `sonsu-marketplace` marketplace로 등록한 뒤 Engineering을 설치합니다.

```sh
codex plugin marketplace add .
codex plugin add engineering@sonsu-marketplace
```

저장소 변경과 플러그인 설치는 서로 다른 작업입니다. 플러그인을 설치하거나 갱신한 뒤 새 Codex 작업을 시작해야 현재 스킬 catalog를 받을 수 있습니다.

## 개발 흐름

1. **brainstorming**은 bounded 진입에서 Local/Mechanical Fast Path 적합성을 먼저 판정합니다. controller는
   target discovery 전에 stable task ID를 고정하고 소비한 예산과 `disqualified` 기록을 확인합니다.
   현재 파일·consumer를 총 2회 이내로 직접 탐색하며 별도 classifier를 기본으로 만들지 않습니다.
   긍정 판정은 현재 연속 실행에서만 사용합니다. 재개·context 손실·설명되지 않는 변경이나
   false·unknown 조건에서는 일반 workflow로 올립니다. 과거 `eligible`이나 `HEAD` 일치로 자격을
   복원하지 않으며, task ID·예산·탈락 기록은 session이 바뀌어도 유지합니다.
2. **using-git-worktrees**는 기존 linked `worktree`를 재사용하거나 격리가 필요할 때 새로 만듭니다.
3. **writing-plans**는 기본적으로 대화 안에 계획을 작성합니다. 의사코드로 전체 흐름을 정의하고 파일·task·dependency에 연결한 뒤, 이유가 있는 검증 방법을 선택하여 계획 준비 상태를 판정합니다.
4. **executing-plans**는 계획을 직접 실행하고, **subagent-driven-development**는 파일 기반 계획과 task 커밋이 승인된 경우 task별 구현·리뷰를 위임합니다. 수정은 최대 5회이며 기본적으로 1~3회차는 원래 구현자를 재사용하고 4~5회차는 새 context와 현재 finding에 적합한 모델·추론도를 사용합니다. 새 구현자에게 승인된 brief, 현재 artifact, 미해결 finding과 실제 실패·검증 기록을 전달하되 전체 대화와 자기 정당화는 제외합니다. 재리뷰는 기존 finding과 수정 회귀를 확인합니다. 최초 전체 일반 리뷰와 독립 red-team은 유지하고, 국소 수정은 유효한 이전 근거와 scoped 검증을 현재 리비전에 연결합니다. 목표·계약·설계·dependency 경계가 바뀌거나 영향이 불명확하면 전체 검토를 다시 엽니다.
5. **test-driven-development**는 기능, 결함, 로직, 상태 전이와 오류 처리처럼 동작·회귀 위험이 있는 변경에서 적합성을 판단한 뒤, 선택된 task에 RED–GREEN–REFACTOR를 적용합니다. 문서, metadata와 단순 설정에는 변경에 적합한 검사를 사용합니다.
6. **requesting-code-review**와 **receiving-code-review**는 검증되지 않은 피드백을 사실로 취급하지 않으면서 리뷰를 처리합니다.
7. **verification-before-completion**은 성공을 주장하기 전에 정확한 리비전의 현재 근거를 요구합니다.
8. **finishing-a-development-branch**는 최종 게이트가 통과하거나 사람이 문서화된 위험을 명시적으로 수용한 뒤에만 통합 방법을 제시합니다.

공통 [품질 게이트 계약](skills/using-engineering-skills/references/quality-gates.md)은 근거 기록, 상태, 오래된 리비전 처리, 반환 대상, 재시도 변경과 시도 횟수 상한에서의 동작을 정의합니다. 품질 판정은 문서, Git, PR, merge, 배포 또는 게시 권한을 부여하지 않습니다.

## 모델과 에이전트 실행

스킬은 routing·검증·예산·인계를 관리하고 별도 agent/session은 집중된 구현·조사·리뷰를 맡습니다.
[공통 실행 계약](skills/using-engineering-skills/references/agent-execution.md)은 요청한 모델·추론도와
관측된 적용값, task/gate ID, 현재 revision, session 관계, 검증 환경·scratch와 남은 예산을 연결합니다.

Codex의 잠정 기본값은 좁고 명확한 구현에 Luna medium, 보조 조사·일반 task review에 Terra medium,
계약·해법이 분명한 복잡한 구현에 Terra high입니다. 모호한 구현과 일반 전체 리뷰에는 Sol medium,
복잡한 논리·가정·경계 검토와 영향 큰 설계·fresh red-team에는 Sol high를 선택합니다. 여러 시스템·도구·단계를
아우르는 가장 어려운 작업은 Astra medium/high를 직접 선택합니다. 모델을 순서대로 거칠 필요는 없습니다.
결정론적 처리는 controller 도구로 실행하고 실제 allowlist와 사용자 선택을 우선합니다.
이 배치는 공식 역할 안내를 반영한 운영값이며 Sol을 포함한 전체 workflow의 최적 조합을 비교 검증한
결과는 아닙니다. 구체적인 대응은 [Codex reference](skills/using-engineering-skills/references/codex-tools.md)를 따릅니다.

모델·추론도·team 크기는 각각 선택합니다. Codex reference에는 단계별 인계, 선택적 low·xhigh·
max·ultra 조건과 GPT-5.6/Astra의 prompt 조정을 함께 둡니다. private 이름처럼 기존 관례로
정할 수 있는 선택은 진행하고, 계약·외부 동작·권한·쓰기 범위 변경이나 필수 규칙 누락·모순은
controller에 반환합니다. 그 결정과 독립적인 승인 작업은 계속합니다. 필수 검증이 충족되면
새 변경·실패·미해결 위험이 있을 때만 검사를 확대하며, 후속 필수 리뷰와 red-team은 유지합니다.

reviewer는 구현자 대화·자체 판정 대신 고정 artifact와 검증 사실을 받습니다. 병렬 구현은 독립된
쓰기 소유권이나 분리 worktree와 통합 소유자가 있을 때 사용하고 SDD의 기본 task loop는 직렬로
유지합니다. 3+2/max5는 같은 task의 수정 운영값입니다. 새 반례에도 잘못된 가정을 반복하면 조기
fresh 전환이 가능하지만 남은 예산은 유지하며, 무관한 세 작업 뒤 세션을 자동 폐기하지 않습니다.
실행 미완료·환경 오류·무효 oracle·미실행 검사를 코드 실패 또는 pass로 바꾸지 않습니다.

기본값의 근거와 실험 한계는 [0012 결정](../../docs/decisions/0012-use-role-routing-and-execution-evidence.md)에
기록합니다. 모델의 보편적인 순위, 최적 수정 횟수와 전체 workflow의 품질 향상을 보장하지 않습니다.

## 스킬

| 영역 | 스킬 |
| --- | --- |
| 진입점 | `using-engineering-skills` |
| 설계와 계획 | `brainstorming`, `writing-plans` |
| Workspace와 실행 | `using-git-worktrees`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents` |
| 품질 | `test-driven-development`, `systematic-debugging`, `verification-before-completion` |
| 리뷰와 완료 | `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch` |
| 스킬 개발 | `writing-skills` |

내부 참조는 `engineering:brainstorming`, `engineering:systematic-debugging`처럼 `engineering:*` namespace를 사용합니다.

## 로컬 정책

- 새 영속 문서를 제안하기 전에 기존 ADR, architecture, product, guide, reference와 runbook 문서를 확인합니다.
- 구현 계획은 기본적으로 대화 안에 유지합니다. 실행에 파일이 필요할 때에만 Git에서 무시하는 scratch 파일을 사용합니다.
- 구현 계획이 필요하면 `writing-plans`의 의사코드가 구현 세부사항보다 먼저 오며 각 흐름을 파일, task, dependency와 검증에 연결합니다. Fast Path에는 긴 의사코드나 red-team을 강제하지 않지만 stable task ID, 소비 예산·탈락 기록, 현재 범위와 결정론적 검증을 남깁니다.
- 구현이 계획에서 material하게 달라지면 `writing-plans`를 canonical source로 삼습니다. 승인된 설계나 관찰 가능한 계약을 바꾸는 차이는 사용자 재승인이 필요하고, 새 흐름의 영향을 받는 완료 task는 다시 열어 검증합니다.
- 설계 승인, 문서 작성, 구현, commit, push, PR, merge와 배포를 서로 다른 권한 경계로 취급합니다.
- 동작과 회귀 위험, 자동화 테스트의 실익을 기준으로 TDD 적합성을 판단하고 선택 이유를 기록합니다. TDD를 선택하면 RED–GREEN–REFACTOR를 유지하며, 문서, metadata와 단순 설정에는 변경에 비례한 구조 검사 또는 실제 소비 명령을 사용합니다.
- 추론 기반 리뷰보다 결정론적인 검사를 먼저 실행하고 모든 게이트를 현재 artifact 리비전에 연결합니다. 변경 영향에 맞게 근거를 갱신하며, 수정마다 전체 리뷰를 반복하지 않습니다. session 교체·owner 반환은 재시도 예산을 초기화하지 않습니다.
- 결정론적 작업에는 노출된 Code Mode를 우선 활용하되 실행 수단을 Fast Path나 품질 통과의 근거로 취급하지 않습니다.
- 역할마다 capability tier와 reasoning effort를 함께 선택하고, Codex의 구체적인 model mapping은 platform reference를 따릅니다. goal은 사용자가 명시적으로 요청한 plan-backed 작업에 최대 하나만 만들고 task는 ledger로 추적합니다.
- 시도 횟수 상한에 도달했다는 이유로 유효한 미해결 finding을 pass로 바꾸지 않습니다. 식별된 사람인 의사결정자만 `accepted_risk`를 기록할 수 있습니다.
- Engineering, Workflow, Research와 Fluent Languages를 서로 독립적으로 설치할 수 있게 유지합니다.

이 문서는 플러그인의 선언된 routing·handoff 계약을 설명합니다. fixture, native loading, shell 검증은
문서와 helper의 구조를 확인할 수 있지만 runtime model compliance나 실제 품질·비용 효과를 증명하지 않습니다.

저장소 정책은 [문서 가이드](../../docs/README.md), [스킬 라우팅 아키텍처](../../docs/architecture/skill-routing.md), [Fast Path와 red-team 결정](../../docs/decisions/0011-use-fast-path-and-plan-red-team-gates.md)과 관련 결정 기록에 남깁니다.

## 실행 artifact와 visual companion

Scratch plan, subagent ledger와 지속형 brainstorming session은 `.engineering/`에 저장합니다.

선택 사항인 brainstorming visual companion은 외부 브랜드 이미지나 원격 요청 없이 Engineering 버전을 텍스트로 표시합니다.

## 라이선스

Engineering에는 [MIT 라이선스](LICENSE)가 적용됩니다.
