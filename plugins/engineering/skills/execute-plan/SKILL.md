---
name: execute-plan
description: 승인된 여러 단계의 작업을 직접 또는 하위 에이전트로 실행·통합하거나 기존 계획을 재개할 때 사용한다
---

# 계획 실행

직접 구현과 위임 구현에 같은 수명주기를 적용한다. 대화 계획과 미커밋 산출물도 사용할 수
있으며 작업별 커밋은 선행 조건이 아니다. 주 조정자는 [연속성 참고 자료](../../references/continuity.md)에
안정적인 task ID·현재 근거·다음 작업을 기록한다.

## 준비

현재 승인과 작업 공간을 확인한다. 목표 → 동작 흐름 → 작업·의존성 → 검사·통과 조건이
연결돼야 한다. 이미 승인된 내부 선택은 계속하고 새 계약 결정에 의존하는 작업만 보류한다.
[품질 게이트](../../references/quality-gates.md)로 각 unit의 정책을 정하고
[관리형 게이트](../../references/evidence-gates.md)에 등록한다.
설계/계획은 고정 문서 패키지로, 구현/통합은 전체 workspace snapshot으로 식별한다.

## 실행·통합

1. `ready`로 현재 선행 조건을 확인하고 `enter`로 작업 진입을 기록한다.
2. root가 직접 수행하거나 [실행 계약](../../references/agent-execution.md)에
   따라 필요한 독립 작업자를 할당한다. 구현을 위임하면
   [위임 절차](../../references/subagent-development.md)를 읽는다. 병렬 writer는 별도 worktree를 사용한다.
3. [공통 코드 품질](../../references/code-quality.md)을 구현자 brief에 포함한다. 테스트가
   의미 있는 동작을 보호하면 [test-driven-development](../test-driven-development/SKILL.md)를 적용한다.
4. 선언한 검사를 실행한다. 필수 독립 리뷰는 [review](../review/SKILL.md)와
   [독립 리뷰 실행 절차](../../references/independent-review.md)로
   수행한다. 미완료·stale·필수 지적이 있으면 소유 단계로 반환한다.
5. 현재 근거를 대조해 `complete-unit`을 요청한다. 과거 idempotent 응답은 현재 유효성의
   증거가 아니므로 `status`의 유효 상태를 확인한다.
6. root가 작업 결과를 순차 통합하고 최종 workspace에서 통합 unit의 필수 검사·리뷰를 수행한다.

임의 도구 호출까지 gate가 막는 것은 아니다. 등록한 unit의 진입·완료를 우회하지 않는다.
호스트 세션 완료와 품질 완료를 구분한다. 정상 작업이 실패하면 원인을 고치며 환경 부재는
`blocked`, 근거 부족은 `inconclusive`로 남긴다.

## 수정과 재개

지적은 [address-review](../address-review/SKILL.md)로 검증한다. 유효한 지적만
가장 가까운 구현·계획·설계·검증 단계에서 수정한다. 원인 불명은 debug으로
보낸다. 집중 수정 brief는 [fix-implementer-prompt.md](fix-implementer-prompt.md)를 사용한다.
원 구현자 재개 또는 새 문맥 선택은 반례·문맥·가용성으로 판단한다.

일반 전체 리뷰는 호스트의 `general_review` 프로필 5개로 한 라운드다. 국소 수정은 이전 전체 근거와 새 `focused_review`
프로필 1개를 연결한다. 계약·설계·의존 경계 변화나 영향 불명확성은 전체 리뷰를 다시 연다.
고위험 unit만 별도 `red_team` 프로필을 거친다. 최대 5라운드는 작업·게이트에 누적하며
세션·담당자·정책 재분류로 초기화하지 않는다. 같은 입력의 검증을 형식적으로 반복하지 않는다.

계약 변경은 의존 unit의 근거를 다시 검토한다. 이미 유효한 독립 작업은 보존한다. 사용자
목표 변경은 해당 결정을 확인하지만 기존 승인 안의 계획·구현 보완에는 새 승인을 요구하지 않는다.

## 완료

등록한 모든 필수 unit이 현재 근거로 충족되면 [완료 근거 확인](../../references/verification.md)에
따라 실제 주장과 검사·리뷰의 리비전을 대조하고 `close`한다. `accepted_risk`는 사람의 명시된
결정으로 별도 보고하며 통과로 바꾸지 않는다. 변경 결과·실제 검사·독립 리뷰·red-team 적용 여부·
미실행·미해결·근거 한계를 보고한다. [전달 권한](../../references/delivery-authority.md)에 따라
승인된 Git/외부 작업만 수행하고 미승인이라면 검증된 diff 상태로 전달한다.
