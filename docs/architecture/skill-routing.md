# 스킬 라우팅

- Status: Current
- Last reviewed: 2026-09-01

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
