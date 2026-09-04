---
name: executing-plans
description: 별도 session에서 review checkpoint와 함께 실행할 작성된 구현 계획이 있을 때 사용한다
---

# executing-plans: 계획 실행

## 개요

계획을 불러와 비판적으로 검토하고 모든 task를 실행한 뒤 완료 시 보고한다.

**시작할 때 알린다:** "executing-plans 스킬을 사용해 이 계획을 구현하겠습니다."

**참고:** Engineering은 subagent를 사용할 수 있을 때 훨씬 잘 동작한다고 사용자에게 알린다(Claude Code, Codex CLI, Codex App, Copilot CLI, Gemini CLI가 모두 해당하며 `../using-engineering-skills/references/`의 플랫폼별 도구 참고 문서를 확인한다). subagent capability가 있고 현재 plan의 task commit을 사용자가 명시적으로 승인한 경우에만 이 스킬 대신 `engineering:subagent-driven-development`를 사용한다. subagent가 있어도 task commit이 승인되지 않았다면 이 스킬에서 직접 실행하며 SDD로 전환하지 않는다.

## 절차

### 1단계: 계획 불러오기와 검토
1. 격리된 workspace를 확보한다. `engineering:using-git-worktrees`로 만들거나 기존 workspace를 확인한다.
2. 승인된 출처에서 계획을 읽는다. 계획이 chat에 있으면 실행 전에 정확한 task를 todo에 보존한다.
3. 계획을 비판적으로 검토하여 질문이나 우려 사항을 찾는다. 별도 구현 plan이 필요한 작업이면
   `engineering:writing-plans`가 정의한 의사코드가 구현 세부사항보다 먼저 있고, 각 flow ID가
   파일, task, dependency와 이유가 있는 검증 방법에 연결되는지 확인한다.
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

구현이 plan과 달라져야 할 때에는 `engineering:writing-plans`의 material deviation 기준을 적용한다.
그 기준에 해당하면 차이와 이유를 설명하고 중단한다. 승인된 요구사항·설계·관찰 가능한 계약을
바꾸는 차이는 `engineering:brainstorming`으로 돌아가 사용자의 명시적인 재승인을 받아야 한다.
승인된 설계 안의 차이이거나 재승인을 받은 뒤에는 의사코드를 먼저 갱신하고 영향을 받는 mapping,
task와 검증을 조정한다. 이미 완료한 task가 새 흐름의 영향을 받으면 `reopened`로 표시하고 그
task의 구현·검증·리뷰부터 다시 수행한다. material하지 않은 local 구현 세부사항은 해당 task
안에서 처리할 수 있다.

변경 없이 실패한 명령이나 변경 없이 같은 reviewer prompt를 반복하지 않는다. 도구, 권한, dependency 또는 외부 service가 없으면 `blocked`다. 이를 이유로 무작정 재시도하거나 계획을 다시 쓰지 않는다. task 세부사항의 모순은 `engineering:writing-plans`로, 승인된 요구사항의 모순은 `engineering:brainstorming`으로 돌려보낸다.

현재 대화에서 명시적으로 승인하지 않았다면 `git add`, `git commit`, push, PR, merge, 배포 또는 그 밖의 외부 작업을 실행하지 않는다. 이전 계획에 승인되지 않은 commit 단계가 있으면 이를 건너뛰고 최종 보고에 기록한다.

### 3단계: 개발 완료

모든 task를 완료하고 검증한 뒤 다음을 수행한다.

1. 승인된 계획과 관련 문서를 기준으로 전체 working tree `diff`를 검토한다.
2. 전체 변경에 필요한 최종 결정론적 검증을 실행한다.
3. 모든 plan-backed 변경은 evaluator를 사용할 수 있을 때 독립적인 일반 전체 변경 리뷰를 받는다.
   해당 리뷰가 필수지만 사용할 수 없으면 게이트를 통과했다고 하지 말고 `blocked` 또는
   `not_run`으로 기록한 뒤 사람의 결정을 요청한다.
4. 일반 리뷰의 유효한 finding에는 한 번에 하나의 집중된 수정과 범위가 제한된 재리뷰를 적용하고,
   자동 리뷰 시도는 최대 3회로 제한한다. 1회차 이후에는 가능한 경우 이전 session history를
   상속하지 않는 fresh-context evaluator를 사용한다. 계획 또는 요구사항의 모순은 해당 소유
   단계로 돌려보낸다. 상한에 도달해도 필수 finding이 해결되지 않았다면 사람의 결정이 필요하며,
   명시적인 `accepted_risk`만 다음 단계 진행을 허용한다. scoped 재리뷰는 finding 수정만 닫으며
   변경된 전체 artifact의 final gate를 대신하지 않는다. 수정이 있었다면 현재 `BASE..HEAD`의 전체
   package를 다시 생성해 fresh-context whole-change reviewer로 일반 final gate를 갱신한다. 이 전체
   review도 3회 상한에 포함하며, 현재 전체 리비전의 gate가 `passed` 또는 `accepted_risk`일 때만
   red-team으로 진행한다.
5. 일반 최종 리뷰 뒤에는 plan-backed 작업을 전체 구조에서 반증하는 fresh-context red-team
   리뷰를 반드시 수행한다. 이전 작업·리뷰의 결론이나 session history를 넘기지 않는다. red-team 직전에
   현재 전체 commit range 또는 전체 working tree를 저장소 root에서
   `plugins/engineering/skills/requesting-code-review/scripts/review-package range BASE HEAD` 또는
   같은 script의 `working-tree` mode로 다시 고정하며, 일반 리뷰 뒤 artifact가 바뀌었다면 이전
   package나 수정 range package를 재사용하지 않는다. 원래 목표, 승인된 요구사항·설계, plan
   의사코드·mapping, 결정론적 검증 report, 관찰 결과·제약과 verdict·칭찬을 제외한 finding-to-fix
   provenance도 파일로 고정한 뒤 저장소 root의
   `plugins/engineering/skills/requesting-code-review/scripts/red-team-package`로 전체 변경 package와
   함께 하나의 immutable bundle에 복사한다. reviewer에는 bundle 경로와 SHA-256만 전달하며
   별도의 mutable source 경로를 전달하지 않는다.
   `engineering:requesting-code-review`의 `red-team-reviewer.md` 계약을 사용한다.
6. red-team 판정은 `survives_challenge`, `invalidated`, `inconclusive`, `blocked` 중 하나다.
   `survives_challenge`만 일반 통과다. 나머지는 공통 품질 게이트 계약에 따라 design, plan,
   implementation 또는 verification 소유 단계로 routing한다. 수정된 새 리비전은 새
   fresh-context reviewer가 다시 검토하며 자동 시도는 최대 3회다. 상한 뒤에는 사람의
   `accepted_risk` 없이 진행하지 않는다.
7. 정확한 working tree 또는 commit 리비전에 결정론적 검증, 일반 최종 리뷰와 red-team 게이트를
   각각 기록한다. 변경 내용, 검증 근거, 남은 위험과 상태를 보고한다.
8. commit 권한이 없으면 중단하고 commit 결정을 요청한다. 검증된 변경은 commit하지 않은 상태로 둔다.
9. commit 권한이 있으면 저장소 Git 규칙에 따라 승인된 범위만 commit하고, 생성된 commit을 검증한 뒤 계속한다. commit하면 artifact 리비전이 바뀌므로 committed tree를 다루지 않은 최종 검사는 다시 실행한다.
10. "finishing-a-development-branch 스킬을 사용해 이 작업을 마무리하겠습니다."라고 알린다.
11. **필수 하위 스킬:** `engineering:finishing-a-development-branch`를 사용하고 통합 방법을 제시하는 절차를 따른다.

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
