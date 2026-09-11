---
name: requesting-code-review
description: 구현 작업의 검토 단계, 주요 기능 완료 이후 또는 merge 전에 독립 리뷰가 필요할 때 사용한다
---

# 코드 리뷰 요청

리뷰어에게 승인된 요구사항, 정확한 변경 내용과 검증 사실을 전달한다. 리뷰어는
[공통 리뷰 기준](review-criteria.md)으로 현재 작업의 동작과 구조 품질을 검토한다.

## 시점과 입력

에이전트가 구현한 각 작업, 주요 기능과 최종 변경 등 현재 절차가 선언한 리뷰를 수행한다.
리뷰 적용 여부와 상태·재시도는 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을
따른다. 단순 문서·메타데이터 변경은 결정론적 검사가 충분한지 판단한다.

리뷰어는 이전 구현 이력을 상속하지 않는 새 문맥에서 시작한다. 승인 계약, 고정한 변경,
실제 명령·결과와 제약을 전달한다. 모델·추론 수준·예산은
[실행 계약](../using-engineering-skills/references/agent-execution.md)에 따른다.

검토할 저장소를 현재 작업 디렉터리로 유지한다. 현재 읽은 스킬의 설치 위치에서 `scripts/`의
절대 경로를 확인해 `REVIEW_SCRIPTS`로 둔다. 도구는 현재 디렉터리의 Git 저장소를 대상으로
변경 범위를 고정한다. `BASE_SHA`는 작업 시작점 또는 확인한 merge base다. 여러 커밋으로
구성된 작업을 `HEAD~1`로 줄이지 않는다.

```bash
"$REVIEW_SCRIPTS/review-package" range "$BASE_SHA" "$HEAD_SHA"
# commit하지 않은 변경:
"$REVIEW_SCRIPTS/review-package" working-tree
```

출력 경로와 SHA-256을 [code-reviewer.md](code-reviewer.md)에 채우고 공통 리뷰 기준을 앞에
붙여 위임한다. `working-tree`는 staged·tracked·untracked 변경을 포함한다. 리뷰어는 고정
패키지의 무결성을 확인한 뒤 읽기 전용으로 검토한다.

## 결과와 재검토

[receiving-code-review](../receiving-code-review/SKILL.md)에 따라 근거를 대조한다. 유효한
Critical/Important는 소유 단계에서 수정하고 관련 검증·집중 재리뷰를 수행한다. 근거로
무효화한 지적은 이유와 함께 닫고, 근거 있는 비차단 지적은 보고한다. 비차단 지적만으로
필수 수정·재리뷰·할 일 목록을 추가하지 않는다.

필수 독립 리뷰를 수행할 수 없으면 `blocked` 또는 `not_run`, 판정 근거가 부족하면
`inconclusive`다. 자체 검토를 독립 리뷰로 보고하지 않는다. 국소 수정은 이전 전체 리뷰의
유효 범위, 실제 변경과 새 근거를 현재 리비전에 연결한다. 목표·계약·설계·의존 경계 변경이나
영향 불명확성은 해당 전체 리뷰를 다시 여는 조건이다. 필수 미해결 지적에는 해결 또는
사람의 명시적인 `accepted_risk` 결정이 필요하다.

## 계획에 따른 작업의 완료 리뷰

구현 계획이 있는 작업은 일반 최종 리뷰 뒤 별도의 새 문맥에서
[red-team-reviewer.md](red-team-reviewer.md)로 원래 목표·해법·실제 검증의 연결을 확인한다.
계획 없는 Fast Path에는 적용하지 않는다.

직전에 전체 변경과 아래 근거의 내용을 `scripts/red-team-package`로 하나의 고정 묶음에 넣는다.
리뷰어에는 이 묶음과 digest를 전달한다.

```bash
"$REVIEW_SCRIPTS/red-team-package" \
  "$WHOLE_CHANGE_PACKAGE" "$ORIGINAL_GOAL_FILE" "$REQUIREMENTS_FILE" \
  "$PLAN_AND_MAPPING_FILE" "$VERIFICATION_REPORT" "$OUTCOMES_FILE" \
  "$PROVENANCE_FILE" "$RED_TEAM_BUNDLE"
```

`PROVENANCE_FILE`에는 변경에 영향을 준 지적의 원문·근거, 적용 리비전·경로와 관찰 결과를
기록한다. 이전 판정·칭찬·리뷰어 권위를 결론의 근거로 넣지 않으며, 해당 이력이 없으면
`none`을 기록한다. 스크립트는 필수 구성요소의 누락·빈 내용·기존 출력 경로를 거부한다.
리뷰어에게 가변 원본 경로를 별도 입력으로 제공하지 않고 공통 리뷰 기준을 전달한다.

`survives_challenge`가 통과다. `invalidated`는 반증된 구현·설계·계획·검증의 소유 단계로
반환한다. 원래 목표를 바꾸는 결정은 사용자 재승인이 필요하다. 필수 근거 부족은
`inconclusive`, 검토를 수행할 수 없으면 `blocked` 또는 `not_run`으로 보고한다.
사람이 위험을 수용한 `accepted_risk`는 통과와 구분한다.

수정 후 검증·일반 리뷰 근거와 전체 묶음을 갱신한다. 새 리뷰어는 기존 반례와 실제 수정
회귀에 집중할 수 있다. 전제가 바뀌거나 영향이 불명확하면 전체 검토를 다시 연다. 기존
지적도 근거로 반증할 수 있으며 잘못된 수정이 영향을 준 작업은 `reopened`한다.
자동 시도는 동일 게이트에서 최대 5회이며 세션·담당자·패키지 변경으로 초기화하지 않는다.

## 작업 연속성

여러 단계의 작업이나 외부 쓰기를 맡은 조정자는 [task-continuity](../task-continuity/SKILL.md)에
따라 진행과 게이트 근거를 기록한다. 위임된 리뷰어는 별도 기록을 만들지 않는다.
