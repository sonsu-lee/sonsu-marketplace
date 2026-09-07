---
name: requesting-code-review
description: task를 완료할 때, 주요 기능을 구현한 뒤 또는 merge 전에 작업이 요구사항을 충족하는지 검증하기 위해 사용한다
---

# 코드 리뷰 요청

리뷰어에게 승인된 요구사항, 정확한 변경 내용과 검증 사실을 전달한다. 리뷰어는
[공통 리뷰 기준](review-criteria.md)에 따라 현재 작업의 동작과 구조 품질을 검토한다.

## 작업 연속성

현재 메인 controller가 여러 단계의 작업을 소유하거나 외부 쓰기를 수행할 때에는 같은 플러그인의
[task-continuity](../task-continuity/SKILL.md)를 적용해 시작·중요한 진행 변화·외부 쓰기 전후를 기록한다.
컴팩션·재개 후에는 그 기록과 현재 근거를 대조한다. 짧은 단발 작업, 위임된 subagent와 fresh reviewer는
별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 변경하지 않는다.

## 시점과 입력

- subagent-driven development의 각 task 이후, 주요 기능 완료 이후, main merge 이전에 리뷰한다.
- artifact·상태·재시도는 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 따른다.
- reviewer는 fresh context에서 시작한다. 구현자 대화·자체 판정·칭찬을 제외하고 승인 계약,
  현재 변경, 명령·결과와 제약을 전달한다. 모델·추론도·예산은 [실행 계약](../using-engineering-skills/references/agent-execution.md)을 따른다.

이 스킬 디렉터리의 script로 정확한 변경 범위를 고정한다. BASE는 task 시작점 또는 확인한
merge base이며 여러 commit의 작업을 HEAD~1로 줄이지 않는다.

```bash
./scripts/review-package range "$BASE_SHA" "$HEAD_SHA"
# commit하지 않은 변경:
./scripts/review-package working-tree
```

출력된 package 경로와 SHA-256을 [code-reviewer.md](code-reviewer.md)에 채우고, 공통 리뷰
기준의 내용을 prompt 앞에 붙여 reviewer를 위임한다. working-tree mode는 staged·tracked·
untracked 변경을 포함한다. reviewer는 선언된 artifact를 확인한 뒤 읽기 전용으로 검토한다.

## 결과 처리

[receiving-code-review](../receiving-code-review/SKILL.md)에 따라 지적을 근거와 대조한다.
유효한 Critical/Important는 소유 단계에서 수정하고 영향받은 검증과 집중 재리뷰를 수행한다.
근거 없는 지적은 이유를 기록하고 닫는다. 근거 있는 비차단 구조 지적은 보고하되 자동 수정
loop나 backlog로 넘기지 않는다. 추가 구현은 사용자가 요청한 범위에서 다룬다.
reviewer를 사용할 수 없으면 blocked 또는 not_run이며 자체 리뷰로 대체하지 않는다. 필수 근거가 부족한 보고서는 inconclusive다.

수정 뒤에는 기존 finding과 수정으로 생긴 회귀를 검토한다. 국소 수정에서는 이전의 유효한 근거와
새 검증 결과를 현재 revision에 연결한다. 목표·계약·설계·dependency 경계가 바뀌거나 영향이 불명확하면 전체
리뷰를 다시 연다. 유효한 미해결 필수 finding에는 수정 또는 사람의 명시적인 accepted_risk가 필요하다.

## Plan-backed 완료 리뷰

계획에 따라 수행한 작업은 일반 최종 리뷰 뒤 별도의 fresh-context
[red-team-reviewer.md](red-team-reviewer.md)로 목표·해법·실제 검증이 서로 연결되는지 확인한다.
plan 없는 Fast Path에는 적용하지 않는다. 일반 리뷰 결과나 구현자 대화를 정답으로 넘기지 않는다.

red-team 직전에 현재 전체 변경 package와 아래 근거를 고정한다. 각 component의 **내용**을
`scripts/red-team-package`로 하나의 bundle에 넣고, reviewer에는 bundle 경로와 digest를 전달한다.
mutable source 경로를 별도로 넘기지 않는다.

```bash
./scripts/red-team-package \
  "$WHOLE_CHANGE_PACKAGE" "$ORIGINAL_GOAL_FILE" "$REQUIREMENTS_FILE" \
  "$PLAN_AND_MAPPING_FILE" "$VERIFICATION_REPORT" "$OUTCOMES_FILE" \
  "$PROVENANCE_FILE" "$RED_TEAM_BUNDLE"
```

provenance에는 artifact에 영향을 준 finding의 원문·근거, 적용 revision·path와 관찰 결과만
넣는다. verdict·칭찬·reviewer 권위는 제외하며 해당 내용이 없으면 none을 기록한다. script는
필수 component 누락·빈 내용·기존 출력 경로를 거부한다. 공통 리뷰 기준은 prompt에 포함한다.

survives_challenge만 통과다. invalidated는 구현·설계·계획·검증 중 해당 소유 단계로 돌려보내고,
원래 목표를 바꾸는 결정에는 사용자 재승인이 필요하다. 필수 근거 부족은 inconclusive,
검토를 수행할 수 없으면 blocked 또는 not_run이다. 일반 리뷰 승인이 이를 대신하지 않는다.

수정 후에는 영향받은 검증·일반 리뷰 근거와 현재 전체 bundle을 갱신한다. 다음 fresh reviewer는
기존 반례와 수정으로 생긴 회귀를 검토하고, 계약·경계가 바뀌거나 영향이 불명확하면 전체 challenge를
다시 연다. 이전 finding도 근거로 반증할 수 있으며 잘못된 수정이 영향을 준 task를 reopened한다.
자동 시도는 게이트마다 최대 5회로, session·owner 변경으로 초기화하지 않는다.
