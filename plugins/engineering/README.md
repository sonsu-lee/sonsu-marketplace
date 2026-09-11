# Engineering

소프트웨어 변경의 설계·계획·구현·디버깅·검증·리뷰를 안내하는 Codex·Claude Code 플러그인이다.
요청에 필요한 스킬을 선택하고, 변경의 동작과 위험에 맞는 절차를 적용한다.

## 설치

이 저장소를 `sonsu-marketplace`로 등록한 뒤 설치한다.

```sh
# Codex
codex plugin marketplace add .
codex plugin add engineering@sonsu-marketplace

# Claude Code
claude plugin marketplace add .
claude plugin install engineering@sonsu-marketplace
```

설치·갱신 뒤 Codex에서는 새 작업을 시작하고, Claude Code에서는 `/reload-plugins`를 실행하거나
세션을 다시 시작해 최신 스킬 목록을 불러온다. 저장소 수정과 실제 설치본 갱신은 별도 작업이다.

## 작업 흐름

[스킬 선택](skills/using-engineering-skills/SKILL.md)에서 요청과 현재 승인 범위를 확인한다.
짧은 설명은 바로 답하고, 변경 작업은 설계·구현·디버깅 등 실제 목적에 필요한 지침을 적용한다.

1. `brainstorming`에서 범위와 판단할 내용을 정한다. 조건을 모두 확인한 국소·기계적 변경은
   Fast Path로 실행하고, 여러 흐름을 조정해야 하면 `writing-plans`로 계획한다.
2. 계획은 전체 동작을 의사코드로 정의한 뒤 파일·작업·의존성과 검증 방법·이유에 연결한다.
   기본 산출물은 대화이며 파일이 필요하면 Git에서 제외된 임시 계획을 사용한다.
3. `executing-plans`로 직접 실행한다. 파일 기반 계획과 작업별 commit이 승인됐다면
   `subagent-driven-development`를 사용할 수 있다. 병렬 구현은 파일 소유 범위와 통합 담당자를 정한다.
4. 동작·회귀 위험에 맞춰 검증한다. TDD를 선택한 작업은 RED–GREEN–REFACTOR를 적용하고,
   문서·설정·스킬은 해당 형식·소비 도구·실제 적용 결과를 확인한다.
5. 계획에 따른 작업은 결정론적 검증과 일반 전체 변경 리뷰 뒤 새 문맥의 red-team 검토를 받는다.
   현재 리비전의 근거로 완료 상태를 보고하고, 요청된 Git·외부 작업을 수행한다.

절차 선택은 실행 권한과 구분한다. 이미 승인된 구현은 Fast Path 탈락·계획 전환·재개 후에도
같은 범위에서 계속한다. 설계 전용 요청은 설계를 완성하고, 구현 전 확인이 요청됐다면 검토할
산출물을 완성한 뒤 그 의존 작업만 기다린다. 독립적으로 승인된 작업은 계속한다.

Fast Path는 고정 작업 ID, 표적 탐색 최대 2회, 최초 구현 1회와 집중 수정 1회로 운영한다.
탈락·재개 시 `disqualified`와 소비 예산을 유지하고 일반 경로로 전환한다. 상태 도구의 명령과
상세 조건은 [brainstorming](skills/brainstorming/SKILL.md)에 둔다.

## 검증과 리뷰

[품질 게이트 계약](skills/using-engineering-skills/references/quality-gates.md)은 현재 산출물과
리비전, 필요한 근거, 판정, 반환 단계와 시도 예산을 연결한다. 국소 수정은 기존 유효 근거와
집중 검증·재리뷰를 현재 리비전에 연결하고, 계약·경계가 바뀌거나 영향이 불명확하면 전체 검토를 갱신한다.

자동 리뷰·수정은 게이트별 최대 5회이며 세션·담당자 변경 후에도 소비 예산을 유지한다.
유효한 미해결 필수 지적은 수정하거나 사람이 해당 리비전의 위험을 명시적으로 수용해야 한다.
`accepted_risk`는 `passed`와 구분하고, red-team의 일반 통과는 `survives_challenge`다.

[공통 리뷰 기준](skills/requesting-code-review/review-criteria.md)은 확인된 동작과 구조를 검토한다.
동작 결함은 도달 가능한 실패 경로로, 구조 문제는 현재 이해·수정 비용과 대안으로 설명한다.
검사 실행, 로더의 스킬 발견, 모델의 지침 적용과 실제 품질·비용 효과는 각각 다른 근거로 보고한다.

## 스킬과 역할

| 역할 | 스킬 |
| --- | --- |
| 작업 진입 | `using-engineering-skills` |
| 설계·계획 | `brainstorming`, `writing-plans` |
| 작업 공간·실행 | `using-git-worktrees`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents` |
| 디버깅·검증 | `systematic-debugging`, `test-driven-development`, `verification-before-completion` |
| 리뷰·마무리 | `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch` |
| 스킬 작성 | `writing-skills` |
| 진행 기록·재개 | `task-continuity` |

호출명은 `engineering:brainstorming`처럼 유지하고, 설명·절차는 한국어로 작성한다.
코드·명령어·상태값·직접 인용과 도구가 읽는 필드는 원문을 유지한다. 작성 형식과 내용 선택 기준은
[writing-skills](skills/writing-skills/SKILL.md)에 둔다.

Engineering은 단독으로 설치할 수 있다. Git·티켓·PR을 직접 요청하면 설치된 Workflow가,
여러 출처의 조사는 Research가, 문장·문단 구성은 Writing이, 언어별 표현은 Fluent가 담당할 수 있다.
각 지침은 요청에 필요한 범위에서 함께 적용한다.

## 에이전트와 작업 재개

[실행 계약](skills/using-engineering-skills/references/agent-execution.md)에 따라 역할·자료·쓰기 범위·
환경·예산을 전달한다. 모델과 설정은 현재 도구의 지원 범위와 사용자 선택에 맞춘다. 플랫폼별
대응은 [Codex](skills/using-engineering-skills/references/codex-tools.md)와
[Claude Code](skills/using-engineering-skills/references/claude-code-tools.md)를 참고한다.

여러 단계의 작업은 [작업 연속성](skills/task-continuity/SKILL.md)으로 `.sonsu/continuity/`에
진행과 근거 위치를 기록한다. 재개 시 원문·현재 산출물과 대조하고 기존 승인 범위를 이어서 적용한다.
`SessionStart` hook은 활성 기록의 위치를 알려 준다. 사용자가 호스트에서 hook 정의를 검토해
신뢰 설정을 관리하며, hook을 사용할 수 없으면 스킬의 조회 절차부터 수동으로 재개한다.
저장 도구는 Python 3.9+와 POSIX 환경을 사용한다.

계획 기반 작업에는 선택적인 [완료 근거 관찰 도구](skills/using-engineering-skills/references/evidence-gates.md)를
제공한다. 등록한 검사 명령의 실제 결과와 일반 리뷰·red-team 근거를 현재 파일·정책의 digest에
연결하고, 누락·변경 후 오래된 결과·누적 시도를 검사한다. 등록한 root session의 `Stop` 훅은
관찰 결과와 알림만 남기며 작업을 차단하거나 계속 실행하지 않는다. 설치만으로 활성 작업이
등록되거나 훅이 신뢰되지는 않는다. 의미적 정확성과 실제 리뷰 독립성은 기존 검증으로 확인한다.

임시 계획·진행 원장·선택적 시각 보조 세션은 `.engineering/`에 저장한다. 자세한 근거는
[스킬 라우팅](../../docs/architecture/skill-routing.md),
[Fast Path·red-team 결정](../../docs/decisions/0011-use-fast-path-and-plan-red-team-gates.md),
[역할·실행 근거 결정](../../docs/decisions/0012-use-role-routing-and-execution-evidence.md),
[작업 연속성 계약](../../docs/reference/task-continuity.md)에 있다.

Engineering은 독립 버전을 사용하며 [MIT 라이선스](LICENSE)를 적용한다.
