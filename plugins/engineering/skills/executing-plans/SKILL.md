---
name: executing-plans
description: 별도 session에서 review checkpoint와 함께 실행할 작성된 구현 계획이 있을 때 사용한다
---

# executing-plans: 계획 실행

## 개요

계획을 불러와 비판적으로 검토하고 모든 task를 실행한 뒤 완료 시 보고한다.

**시작할 때 알린다:** "executing-plans 스킬을 사용해 이 계획을 구현하겠습니다."

**참고:** Engineering은 subagent를 사용할 수 있을 때 훨씬 잘 동작한다고 사용자에게 알린다(Claude Code, Codex CLI, Codex App, Copilot CLI, Gemini CLI가 모두 해당하며 `../using-engineering-skills/references/`의 플랫폼별 도구 참고 문서를 확인한다). subagent를 사용할 수 있으면 이 스킬 대신 `engineering:subagent-driven-development`를 사용한다.

## 절차

### 1단계: 계획 불러오기와 검토
1. 격리된 workspace를 확보한다. `engineering:using-git-worktrees`로 만들거나 기존 workspace를 확인한다.
2. 승인된 출처에서 계획을 읽는다. 계획이 chat에 있으면 실행 전에 정확한 task를 todo에 보존한다.
3. 계획을 비판적으로 검토하여 질문이나 우려 사항을 찾는다.
4. 계획의 commit 권한을 읽는다. 계획 자체는 권한을 부여하지 않으므로 현재 대화의 사용자 요청과 일치하는지 확인한다.
5. 공통 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽고 plan-readiness 게이트가 정확한 계획 리비전을 대상으로 하는지 확인한다. 오래됐거나 `failed`, `blocked`, `inconclusive` 또는 필수 `not_run` 상태인 게이트는 구현 전에 계획 단계로 돌려보낸다.
6. 우려 사항이 있으면 시작하기 전에 사용자에게 알린다.
7. 우려 사항이 없으면 계획 항목으로 todo를 만들고 진행한다.

### 2단계: Task 실행

각 task에서 다음을 수행한다.
1. `in_progress`로 표시한다.
2. 각 단계를 정확히 따른다. 계획은 작은 실행 단위로 작성되어 있다.
3. 지정된 검증을 실행한다.
4. 근거와 finding을 포함하여 정확한 task `diff` 또는 artifact 리비전에 task 게이트를 기록한다.
5. 검사가 실패하면 영향을 받은 가장 작은 구현 단계로 돌아간다. 원인을 모르면 `engineering:systematic-debugging`을 사용한 뒤 변경된 artifact에 집중된 검사를 다시 실행한다.
6. task 게이트가 `passed`이거나 사람이 해당 리비전에 대해 `accepted_risk`를 명시적으로 기록한 경우에만 `completed`로 표시한다.

변경 없이 실패한 명령이나 변경 없이 같은 reviewer prompt를 반복하지 않는다. 도구, 권한, dependency 또는 외부 service가 없으면 `blocked`다. 이를 이유로 무작정 재시도하거나 계획을 다시 쓰지 않는다. task 세부사항의 모순은 `engineering:writing-plans`로, 승인된 요구사항의 모순은 `engineering:brainstorming`으로 돌려보낸다.

현재 대화에서 명시적으로 승인하지 않았다면 `git add`, `git commit`, push, PR, merge, 배포 또는 그 밖의 외부 작업을 실행하지 않는다. 이전 계획에 승인되지 않은 commit 단계가 있으면 이를 건너뛰고 최종 보고에 기록한다.

### 3단계: 개발 완료

모든 task를 완료하고 검증한 뒤 다음을 수행한다.

1. 승인된 계획과 관련 문서를 기준으로 전체 working tree `diff`를 검토한다.
2. 전체 변경에 필요한 최종 결정론적 검증을 실행한다.
3. 크거나 위험도가 높은 직접 변경은 evaluator를 사용할 수 있을 때 독립적인 전체 변경 리뷰를 받는다. 해당 리뷰가 필수지만 사용할 수 없으면 게이트를 통과했다고 하지 말고 `blocked` 또는 `not_run`으로 기록한 뒤 사람의 결정을 요청한다.
4. 유효한 finding에는 한 번에 하나의 집중된 수정과 범위가 제한된 재리뷰를 적용하고, 리뷰 시도는 최대 3회로 제한한다. 계획 또는 요구사항의 모순은 해당 소유 단계로 돌려보낸다. 상한에 도달해도 필수 finding이 해결되지 않았다면 사람의 결정이 필요하며, 명시적인 `accepted_risk`만 다음 단계 진행을 허용한다.
5. 정확한 working tree 또는 commit 리비전에 최종 게이트를 기록한다. 변경 내용, 검증 근거, 남은 위험과 상태가 `passed`인지 `accepted_risk`인지 보고한다.
6. commit 권한이 없으면 중단하고 commit 결정을 요청한다. 검증된 변경은 commit하지 않은 상태로 둔다.
7. commit 권한이 있으면 저장소 Git 규칙에 따라 승인된 범위만 commit하고, 생성된 commit을 검증한 뒤 계속한다. commit하면 artifact 리비전이 바뀌므로 committed tree를 다루지 않은 최종 검사는 다시 실행한다.
8. "finishing-a-development-branch 스킬을 사용해 이 작업을 마무리하겠습니다."라고 알린다.
9. **필수 하위 스킬:** `engineering:finishing-a-development-branch`를 사용하고 통합 방법을 제시하는 절차를 따른다.

## 중단하고 도움을 요청할 때

**다음 상황에서는 즉시 실행을 중단한다.**
- blocker가 발생했다(dependency 누락, 테스트 실패, 불명확한 지침).
- 계획에 시작을 막는 중대한 공백이 있다.
- 지침을 이해하지 못했다.
- 검증이 반복해서 실패한다.
- 계획이 사용자가 승인하지 않은 commit 또는 외부 작업을 요구한다.

**추측하지 말고 명확화를 요청한다.**

## 이전 단계로 돌아갈 때

**다음 상황에서는 검토(1단계)로 돌아간다.**
- 사용자가 피드백을 반영해 계획을 갱신했다.
- 근본적인 접근 방식을 다시 검토해야 한다.

**blocker를 억지로 통과하지 않는다.** 중단하고 질문한다.

## 기억할 사항
- 먼저 계획을 비판적으로 검토한다.
- 계획 단계를 정확히 따른다.
- 검증을 생략하지 않는다.
- 계획에서 지시한 스킬을 참조한다.
- blocked 상태에서는 추측하지 말고 중단한다.
- 사용자의 명시적인 동의 없이 main/master 브랜치에서 구현을 시작하지 않는다.
