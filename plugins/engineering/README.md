# Engineering

Engineering은 소프트웨어 변경을 계획하고, 구현하고, 디버깅하고, 검증하고, 리뷰할 때 문서 상태를 함께 고려하는 방법입니다. 제한적이고 표적화된 되돌아가기와 단계별 소유 품질 게이트를 사용합니다. 조합 가능한 Codex 스킬을 제공하되 Git 전달, 외부 조사와 출력 언어 지침은 별도 플러그인으로 분리합니다.

이 로컬 플러그인은 [obra/superpowers](https://github.com/obra/superpowers) v6.3.0을 기반으로 하며 공식 Superpowers 배포본이 아닙니다. 고정한 원본, 가져온 파일, 로컬 변경과 호환성을 위해 유지하는 이름은 [UPSTREAM.md](UPSTREAM.md)를 참고하세요.

## 책임

Engineering은 다음 개발 방법을 담당합니다.

- 변경 내용과 문서에 미치는 영향을 구체화합니다.
- 필요하면 격리된 `worktree`를 재사용하거나 만듭니다.
- 날짜 기반 문서를 자동으로 만들지 않고 구현 계획을 작성합니다.
- production 동작 변경에는 TDD를 적용하고, 그 외 변경에는 성격에 비례한 검증을 적용합니다.
- 적용되는 커밋 권한 경계 안에서 계획을 직접 실행하거나 subagent와 함께 실행합니다.
- 체계적으로 디버깅하고, 리뷰를 요청하고, 정확한 artifact 리비전을 검증합니다.
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
`engineering`을 설치하기 전에 기존 `superpowers` 플러그인을 제거하세요. 두 버전을 함께 유지하면 같은 스킬의 중복 복사본이 노출될 수 있습니다.

## 개발 흐름

1. **brainstorming**은 문제, 대안, 설계와 문서 영향을 구체화하고, 계획 전에 아키텍처 또는 고위험 영속 문서의 게이트를 처리합니다.
2. **using-git-worktrees**는 기존 linked `worktree`를 재사용하거나 격리가 필요할 때 새로 만듭니다.
3. **writing-plans**는 기본적으로 대화 안에 계획을 작성하고, 문서·검증·Git 권한 경계를 보존하면서 계획 준비 상태를 판정합니다.
4. **executing-plans**는 task 및 전체 변경 게이트와 함께 계획을 직접 실행합니다. **subagent-driven-development**는 파일 기반 계획과 task 커밋이 명시적으로 승인된 경우 task별 정밀 리뷰 게이트를 추가합니다.
5. **test-driven-development**는 production 동작 변경에 RED–GREEN–REFACTOR를 적용합니다. 문서, metadata와 단순 설정에는 변경에 적합한 검사를 사용합니다.
6. **requesting-code-review**와 **receiving-code-review**는 검증되지 않은 피드백을 사실로 취급하지 않으면서 리뷰를 처리합니다.
7. **verification-before-completion**은 성공을 주장하기 전에 정확한 리비전의 현재 근거를 요구합니다.
8. **finishing-a-development-branch**는 최종 게이트가 통과하거나 사람이 문서화된 위험을 명시적으로 수용한 뒤에만 통합 방법을 제시합니다.

공통 [품질 게이트 계약](skills/using-engineering-skills/references/quality-gates.md)은 근거 기록, 상태, 오래된 리비전 처리, 반환 대상, 재시도 변경과 시도 횟수 상한에서의 동작을 정의합니다. 품질 판정은 문서, Git, PR, merge, 배포 또는 게시 권한을 부여하지 않습니다.

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
- 설계 승인, 문서 작성, 구현, commit, push, PR, merge와 배포를 서로 다른 권한 경계로 취급합니다.
- production 동작 변경과 결함에는 TDD를 사용합니다. 문서, metadata와 단순 설정에는 변경에 비례한 구조 검사 또는 실제 소비 명령을 사용합니다.
- 추론 기반 리뷰보다 결정론적인 검사를 먼저 실행하고, 모든 게이트를 정확한 artifact 리비전에 연결하고, 정보가 달라졌을 때에만 재시도합니다.
- 시도 횟수 상한에 도달했다는 이유로 유효한 미해결 finding을 pass로 바꾸지 않습니다. 식별된 사람인 의사결정자만 `accepted_risk`를 기록할 수 있습니다.
- Engineering, Workflow, Research와 Fluent Languages를 서로 독립적으로 설치할 수 있게 유지합니다.

저장소 정책은 [문서 가이드](../../docs/README.md), [스킬 라우팅 아키텍처](../../docs/architecture/skill-routing.md), [품질 게이트 결정](../../docs/decisions/0007-use-stage-owned-quality-gates.md)과 관련 결정 기록에 남깁니다.

## 호환성과 visual companion

Scratch plan, subagent ledger와 지속형 brainstorming session은 계속 `.superpowers/`를 사용합니다. 이 legacy 경로는 기존 로컬 artifact와 스크립트 호환성을 보존하기 위한 것이며 현재 플러그인 이름이 아닙니다.

선택 사항인 brainstorming visual companion은 telemetry가 활성화되어 있으면 upstream Prime Radiant 이미지를 계속 사용합니다. 이 요청을 막으려면 `ENGINEERING_DISABLE_TELEMETRY`를 true 값으로 설정하세요. 기존 `SUPERPOWERS_DISABLE_TELEMETRY`, `DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 변수도 계속 지원합니다.

## Upstream과 라이선스

Engineering에는 Superpowers v6.3.0에서 파생된 작업이 포함되어 있습니다. 원본, 고정한 커밋, 가져온 범위와 로컬 변경은 [UPSTREAM.md](UPSTREAM.md)에 기록했습니다. 원본 MIT 저작권 고지는 [LICENSE](LICENSE)에 유지합니다.
