---
name: subagent-driven-development
description: 승인된 구현 작업을 하위 에이전트에게 나누어 맡기고 현재 세션에서 결과를 통합할 때 사용한다
---

# 하위 에이전트로 구현

[executing-plans](../executing-plans/SKILL.md)의 준비·진입·구현·검증·완료 절차를 그대로 사용한다.
이 스킬은 위임 입력과 통합 경계만 추가한다. 파일 계획·작업별 커밋은 필수 조건이 아니다.

root가 목표·입력·쓰기 범위·선행 인터페이스·필수 검사·반환 조건을 정의하고
[실행 계약](../using-engineering-skills/references/agent-execution.md)의 model+effort를 선택한다.
독립 산출물을 가진 작업만 병렬화하며 별도 worktree에서 작성하고 순차 통합한다.
worker는 직접 수행하고 추가 할당을 root에 요청한다.

- 구현 입력: [implementer-prompt.md](implementer-prompt.md).
- 작업 리뷰: [task-reviewer-prompt.md](task-reviewer-prompt.md), 일반 독립 리뷰 구성은
  [requesting-code-review](../requesting-code-review/SKILL.md).
- 집중 수정·재검토: [re-review-prompt.md](re-review-prompt.md).

대화 brief는 직접 전달한다. 큰 파일 계획은 선택적 `scripts/task-brief`로 작업 부분을
추출할 수 있고 `scripts/sdd-workspace`는 임시 실행 자료 위치를 준비한다. 미커밋 리뷰는
requesting-code-review의 `scripts/review-package working-tree`로 고정한다.
도구 형식을 맞추기 위한 빈 계획·커밋·중복 체크리스트를 만들지 않는다.

작업자 DONE은 실행 보고다. root가 실제 변경과 현재 gate 근거를 확인한 뒤 unit을 완료한다.
검사·리뷰·라운드·재개 규칙은 공통 실행 절차를 참조하며 여기서 다시 정의하지 않는다.
