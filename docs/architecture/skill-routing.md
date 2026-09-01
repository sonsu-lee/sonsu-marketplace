# 스킬 라우팅

- Status: Current
- Last reviewed: 2026-09-02

## 플러그인 경계

Superpowers와 Workflow는 각각 단독으로 설치하고 사용할 수 있는 독립 플러그인입니다.
한 플러그인이 다른 플러그인을 import하거나 설치·선행 실행·특정 skill ID를 전제로 하지
않습니다. 여러 영역을 포함한 요청은 Codex가 현재 설치된 스킬의 description과 요청의 직접
목적을 바탕으로 필요한 스킬을 순서대로 선택합니다.

| 직접 목적 | 담당 |
| --- | --- |
| 구현, 디버깅, 계획 실행과 개발 방법론 | `superpowers:*` |
| branch, staging, commit, 일반 push와 Git 변경 검토 | `workflow:git-workflow` |
| ticket·issue·backlog 초안 또는 게시 | `workflow:to-ticket` |
| 현재 branch의 새 GitHub PR 초안 또는 게시 | `workflow:to-pr` |

직접적인 산출물 요청을 우선하여 라우팅합니다. 예를 들어 현재 branch로 PR을 만들어 달라는
요청은 `workflow:to-pr`의 범위이며, 완료된 구현을 어떤 방식으로 통합할지 결정해 달라는
요청은 `superpowers:finishing-a-development-branch`의 범위입니다.

```text
구현하고 PR 초안까지 준비
  → Superpowers로 구현·검증
  → Workflow의 to-pr로 현재 branch를 다시 확인하고 PR 산출물 준비
```

이 순서는 runtime 조합이며 플러그인 dependency가 아닙니다. Workflow만 설치된 환경에서는
Git·ticket·PR 작업이 독립적으로 동작하고, Superpowers만 설치된 환경에서는 자체 개발 및
branch 완료 흐름이 동작해야 합니다. 공통 router는 실제 경쟁 트리거가 반복해서 확인되기
전에는 추가하지 않습니다.

## Superpowers 흐름

```text
요청
  → 작업 범위 판단과 기존 코드·문서 조사
  → 문서 영향 분류
  → 설계 제안과 사용자 검토
  → 구현 계획
  → worktree 확인 또는 생성
  → 구현
  → 변경 성격에 맞는 검증
  → diff 보고
  → 명시적인 커밋 승인
  → commit
```

`using-git-worktrees` 파일은 기존 linked worktree를 재사용하고 일반 checkout에서 필요할 때
worktree를 만드는 원본 정책을 유지합니다. 다만 스킬 안의 commit 문구를 포함한 모든 Git
변경에는 `using-superpowers`의 전역 승인 게이트를 먼저 적용합니다.

## 문서 라우팅

`brainstorming`은 날짜 기반 spec 파일을 자동 생성하지 않습니다. 먼저
[`docs/README.md`](../README.md)의 기준으로 기존 문서를 조사하고, 변경 없음·기존 문서
갱신·새 문서 생성·결정 대체 중 하나를 제안합니다. 새 문서나 큰 재구성은 경로와 목적을
사용자가 검토한 뒤 작성합니다.

`writing-plans`는 구현 계획을 기본적으로 대화에 작성합니다. 실행을 위해 파일이 필요하면
Git에서 제외된 `.superpowers/plans/<topic>.md`를 사용합니다. 저장소의 기존 이슈·티켓이나
사용자가 지정한 위치가 있으면 그 위치를 우선합니다.

## 커밋 라우팅

계획에는 `git commit`을 실행 단계로 자동 삽입하지 않습니다. inline 실행은 구현과 검증 후
diff를 보고하고 커밋 결정을 받습니다. task별 commit을 전제로 하는
`subagent-driven-development`는 현재 작업에서 사용자가 task commit을 명시적으로 승인한
경우에만 시작합니다. 플랫폼 참고 문서, worktree 상태와 다른 스킬의 commit 지시는 이
승인 게이트를 우회할 수 없습니다.

## 테스트 라우팅

| 변경 | 기본 검증 |
| --- | --- |
| 코드의 새 동작, 버그 수정, 동작을 건드리는 리팩터링 | TDD와 회귀 테스트 |
| 문서 | 링크, 경로, 예제와 문서 간 일관성 확인 |
| 스킬 지침 | frontmatter와 경로 검증, 위험할 때 실제 사용 시나리오 평가 |
| manifest와 metadata | 문법, 경로와 실제 Codex 로딩 확인 |
| 단순 설정 | 설정을 소비하는 최소 실제 명령으로 확인 |

외부 스킬은 관련성이 있다는 이유만으로 모두 자동 적용하지 않습니다. Ponytail, grilling,
아키텍처 결정과 제품 탐색 스킬은 사용자가 요청하거나 현재 결정의 불확실성과 위험을 실제로
줄일 때만 선택합니다.

## 라우팅 평가

경계 변경은 [repository-level routing cases](../../evals/skill-routing/cases.json)의 positive,
near-miss, 조합과 단독 설치 사례로 검토합니다. 이 파일은 기대 라우팅을 정의하며 JSON 파싱만
통과했다고 실제 모델 동작이 검증된 것은 아닙니다. 모델 기반 평가는 격리된 읽기 전용 환경과
명시된 실행 범위에서 수행하고 `pass`, `fail`, `not_run`, `inconclusive`를 구분합니다.
