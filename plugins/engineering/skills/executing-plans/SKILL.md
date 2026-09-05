---
name: executing-plans
description: 별도 session에서 review checkpoint와 함께 실행할 작성된 구현 계획이 있을 때 사용한다
---

# executing-plans: 계획 실행

## 개요

계획을 불러와 비판적으로 검토하고 모든 task를 실행한 뒤 완료 시 보고한다.

**시작할 때 알린다:** "executing-plans 스킬을 사용해 이 계획을 구현하겠습니다."

**참고:** 독립된 실행·리뷰에는 subagent를 사용할 수 있다. 효과는 작업 분해와 context 구성에
따라 달라지며 subagent가 있다는 사실만으로 품질 향상을 보장하지 않는다. 지원 도구는
`../using-engineering-skills/references/`의 플랫폼별 참고 문서를 확인한다. subagent capability가 있고
현재 plan의 task commit을 사용자가 명시적으로 승인한 경우에만 `engineering:subagent-driven-development`를
선택할 수 있다. task commit이 승인되지 않았다면 이 스킬에서 직접 실행한다.

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
실행 또는 위임 전에 [공통 실행·context 계약](../using-engineering-skills/references/agent-execution.md)을
현재 task/gate 기록에 연결한다. 실제 model/effort, source revision, 환경과 완료 상태를 구분한다.

1. `in_progress`로 표시한다.
2. 각 단계를 정확히 따른다. 계획은 작은 실행 단위로 작성되어 있다.
3. 지정된 검증을 실행한다.
4. 근거와 finding을 포함하여 정확한 task `diff` 또는 artifact 리비전에 task 게이트를 기록한다.
5. 검사가 실패하면 영향을 받은 가장 작은 구현 단계로 돌아간다. 원인을 모르면 `engineering:systematic-debugging`을 사용한 뒤 변경된 artifact에 집중된 검사를 다시 실행한다.
6. task 게이트가 `passed`이거나 사람이 해당 리비전에 대해 `accepted_risk`를 명시적으로 기록한 경우에만 `completed`로 표시한다.

유효한 task 구현 finding의 자동 수정은 task마다 최대 5회다. 회차 수는 ledger 또는 plan 실행 기록에
남겨 session 재진입, compaction, 소유 단계 복귀 뒤에도 이어서 센다. 1~3회차에는 원래 implementer가
수정한다. 이 스킬처럼 controller가 직접 구현했다면 같은 controller가 집중 수정하고, child implementer가
있다면 그 child를 재개한다. 원래 implementer가 종료됐거나 사용할 수 없거나, 새 반례에도 같은
잘못된 가정을 반복해 진전이 없을 때에는 더 이른 회차에도
`fork_turns: "none"` fresh implementer를 사용할 수 있지만, 아래의 factual handoff만 전달한다.

4~5회차에는 이전 conversation을 상속하지 않는 `fork_turns: "none"` fresh implementer를 사용한다.
4회차는 해당 문제를 해결할 수 있는 모델을 선택하고, 앞선 실패가 판단력 부족을 보여 주면 필요한
판단 수준에 맞춰 모델과 추론도를 직접 선택한다. 정해진 tier 순서를 거치지 않는다. 5회차도 현재 사용 가능한 가장 적합한 capable model을
선택한다. 사용할 수 없는 특정 tier를 기다리느라 자동으로 막히지는 않지만, 실제로 필요한 capability가
없으면 `blocked`와 `decision_required`를 기록한다.

fresh implementer에게는 [fix-implementer-prompt.md](fix-implementer-prompt.md)에 따라 다음 evidence만
간결하게 전달한다: 승인된 task brief, 정확한 현재 리비전에 고정한 binary-safe artifact package, 열린
finding, 관찰한 검증 명령과 결과, 이전에 시도했지만 실패한 접근. 관찰 사실과 원인·해법 가설을 명시적으로
구분한다. 전체 conversation, 장문의 구현 서사나 자기변호, self-review, reviewer 칭찬·통과 판정과 agent
identity는 전달하지 않는다. strict normalized JSON schema나 별도의 fix 전용 tar 형식은 요구하지 않는다.
같은 task/gate ID, 소비·남은 부모 예산, deadline과 허용된 작업·scratch 범위도 전달한다. 조기 fresh
진단은 별도 무료 loop가 아니다. 3+2는 운영값이며 서로 다른 작업 세 개 뒤 세션을 폐기하는 규칙이 아니다.
현재 artifact는 task 최초 구현 전 기준점부터 현재까지의 전체 변경을 포함한다. direct working-tree
실행에서도 누적 변경과 현재 exact artifact를 고정하며, 마지막 수정 delta만으로 handoff하지 않는다.
마지막 수정 전후의 delta는 아래 scoped 재리뷰용이다.

각 회차 뒤에는 원래 finding과 수정이 만든 회귀만 대상으로 scoped 검증과 재리뷰를 수행한다. 새로운
범위 아이디어는 deferred로 기록한다. 수정이 승인된 목표·계약·설계나 dependency boundary를 바꾼다면
해당 소유 단계와 `engineering:brainstorming`의 재승인으로 돌아가며, agent가 위험을 자동 수용하지 않는다.
5회 뒤에도 유효한 필수 finding이 남으면 `failed`와 `decision_required`를 기록하고 자동 반복을 중단한다.
정확한 리비전에 대한 사람의 명시적인 `accepted_risk` 없이는 task를 완료하지 않는다.

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
4. 일반 리뷰의 유효한 finding에는 집중된 수정과 범위가 제한된 재리뷰를 적용하고, 자동 리뷰 시도는
   게이트마다 최대 5회로 제한한다. 소유 단계나 원래 session으로 돌아가도 회차 수를 초기화하지 않는다.
   계획 또는 요구사항의 모순은 해당 소유 단계로 돌려보낸다. 상한에 도달해도 필수 finding이 해결되지
   않았다면 `decision_required`이며, 명시적인 `accepted_risk`만 다음 단계 진행을 허용한다. scoped
   재리뷰는 원래 finding과 수정이 만든 회귀만 판정하고 새로운 범위 아이디어는 deferred로 기록한다.
   수정 뒤에는 이전 전체 게이트의 리비전, 현재 delta, 이 delta가 다룬 finding·검사, 영향이 제한됐다고
   판단한 근거와 현재 리비전의 새 게이트를 기록해 영향받지 않은 기존 evidence를 현재 artifact에
   연결한다. 승인된 목표·계약·설계·dependency boundary가 바뀌거나 bounded impact를 근거로 확정할 수
   없을 때에만 현재 전체 package를 다시 생성해 fresh-context whole-change reviewer로 일반 gate를
   다시 연다. 단지 artifact가 수정됐다는 이유만으로 전체 리뷰를 반복하지 않는다. 이 scoped 또는
   whole-change review 모두 같은 게이트의 5회 상한에 포함한다.
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
   implementation 또는 verification 소유 단계로 routing한다. 최초 red-team은 언제나 현재 전체 목표와
   변경을 새 immutable bundle로 고정해 fresh-context reviewer가 검토한다. 소유 단계가 bounded fix를
   적용했다면 scoped 검증·재리뷰를 완료한 뒤 이전 ordinary gate 리비전, fix delta, 다룬 finding·검사와
   bounded impact 근거를 기록해 영향받지 않은 evidence를 현재 리비전의 ordinary gate에 연결한다. 이어서
   이전 challenge와 그 수정이 만든 회귀만 fresh scoped red-team reviewer가 다시 판정하며, 새로 고정한
   현재 전체 bundle도 참조할 수 있게 제공한다. unrelated issue를 다시 찾도록 요구하지 않는다. 이전
   전체 red-team 리비전, fix delta, 다룬 challenge와 검사, bounded impact 근거, 현재 리비전의 새 scoped
   red-team gate를 기록한다. 목표·계약·설계·dependency boundary가 바뀌었거나 bounded impact를 확정할 수 없을
   때에만 전체 결정론적 검증과 일반 whole-change gate를 갱신하고 새 전체 red-team bundle로 처음부터
   다시 검토한다. red-team 자동 시도는 게이트마다 최대 5회이며 소유 단계나 session 복귀로 초기화하지
   않는다. 상한 뒤에는 `decision_required`를 기록하고 사람의 `accepted_risk` 없이 진행하지 않는다.
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
