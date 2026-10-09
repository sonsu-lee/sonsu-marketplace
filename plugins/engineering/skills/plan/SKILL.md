---
name: plan
description: 여러 단계의 구현 작업에 대해 승인된 요구사항이 있고 구현 전에 흐름·책임·의존 관계를 정해야 할 때 사용한다
---

# plan: 계획 작성

기존 코드와 승인된 요구사항을 다른 실행자도 따라갈 수 있는 구현 계획으로 바꾼다. 요구 출처 → 동작 흐름 → 파일·작업·의존성 → 검증과 이유를 추적할 수 있게 한다.

## 절차

1. **적용 여부와 권한을 정한다.** 여러 단계·파일·구성 요소나 인터페이스·상태 전이·오류·마이그레이션·회귀 위험을 조정해야 하면 계획을 쓴다. 범위 설명과 검증으로 닫을 수 있는 오탈자·명백한 기계적 수정은 긴 의사코드 없이 처리한다. 요구 출처는 원래 구현 요청, 이전 사용자 승인, 승인된 문서·이슈·티켓이다. [brainstorming의 실행 권한](../brainstorming/SKILL.md)에 따라 승인된 범위를 계속하고 절차 전환·재개만으로 재승인을 요구하지 않는다. 설계 전용 요청은 산출물 완성으로 끝낸다. 명시적 구현 전 확인 조건이 있으면 요청된 산출물을 완성한 뒤 그 조건에 의존하는 작업만 보류한다. 미결정 계약과 독립적인 승인 작업은 계속한다.
2. **위치와 연속성을 정한다.** 기본 산출물은 대화 계획이다. 실행 도구에 파일이 필요하면 Git에서 제외한 `.engineering/plans/<feature-name>.md`에 임시 사본을 둔다. 저장소 이슈·티켓 관례나 사용자 지정 위치를 우선한다. 날짜 기반 계획이나 `docs/engineering/plans/`는 자동 생성하지 않는다. 격리가 필요하면 실행 시점에 `engineering:worktree`를 적용한다. 여러 단계 작업의 주 조정자는 [연속성 참고 자료](../../references/continuity.md)에 기록하고, 위임된 작업자와 새 문맥 검토자는 별도 기록을 만들지 않는다.
3. **입력을 읽는다.** 요구사항과 관련 문서·코드를 읽고 앞선 단계의 문서 영향·목적·경로·갱신 범위를 이어받는다. 달라진 부분만 확인한다. 내부 선택은 자료로 해결하고, 사용자 결정이 필요한 계약 공백은 의존 작업과 함께 미결정 항목으로 표시한다.
4. **동작 흐름을 먼저 쓴다.** 구현 세부사항·파일 단계·TDD 여부보다 먼저 `F1`, `F2` 의사코드를 작성한다. 필요한 입력·관찰 결과·순서·상태·분기·반복·오류·경계·책임·가정만 표현한다.
5. **흐름을 작업에 연결한다.** 정확한 파일과 책임, 인터페이스·의존성, 실행 담당·병렬 묶음·쓰기 범위를 정한다. 요구사항·수용 기준·우선순위·비목표·성공 신호·위험·미결정 ID는 [계획 형식](references/plan-format.md#흐름과-추적성)에 따라 보존한다.
6. **검증과 이유를 고른다.** 동작 변경과 자동 검사 추가·확장에는 동작 기록과 `verification_mode`를 구현 전에 정한다. 변경 종류별 선택은 [검증 선택](references/plan-format.md#검증-선택)을 따른다.
7. **계획을 쓴다.** `Requirements source`, `Documentation impact`, `Commit authorization`, `Quality policy`를 포함해 [계획과 Task 양식](references/plan-format.md#계획과-task-양식)으로 작성한다. 판단 근거에는 [공유 출처 태그](../../references/provenance.md)를 붙인다. 현재 사용자 승인에 맞게 `granted for this plan` 또는 `not granted`를 적는다.
8. **구조를 검사한다.** 파일 계획은 이 SKILL.md가 있는 실제 디렉터리에서 실행한다.

   ```bash
   ../../scripts/validate_plan.py <계획 절대 경로> --root <저장소 절대 경로>
   ```

   | 결과 | 행동 |
   | --- | --- |
   | exit 0, `status: valid` | 흐름·작업 ID, 대응 쌍, 파일 선언 구조가 맞다. 9단계의 의미 리뷰로 간다. |
   | exit 1, `status: invalid` | `errors[].code`·`line`을 고친다. 아직 없는 검증 파일은 실제 생성 대상이면 `Create`로 선언하고, 기존 파일 수정이면 경로를 바로잡는다. 다시 실행한다. |
   | exit 2, `status: input_error` 또는 사용법 오류 | 계획 경로·UTF-8·저장소 root를 고친다. 구조 결과로 기록하지 않는다. |

   대화 계획은 같은 항목을 직접 대조한다. 검사기는 승인·요구사항 의미·검증 검출력을 판정하지 않는다. 허용 형식과 출력 필드는 [구조 검사기가 받는 형식](references/plan-format.md#구조-검사기가-받는-형식)에 있다.
9. **자체 리뷰와 준비 상태 게이트를 닫는다.** 요구사항(PRD가 있으면 REQ ID) → 흐름 → 파일·작업·의존성 → 검증을 대조한다. 실제 경로·인터페이스·type·값, 문서 영향, 권한·실행 가능성을 확인하고 자리표시자, 미정 오류 처리, 명령·예상 결과 없는 검증, 정의되지 않은 인터페이스와 추측성 작업을 없앤다. [품질 게이트 계약](../../references/quality-gates.md)에 따라 정확한 계획 리비전의 근거를 기록한다. 여러 구성 요소·장기·고위험 계획이거나 독립 리뷰가 위험을 줄이면 [계획 검토자](plan-document-reviewer-prompt.md)를 사용한다. 선택적 리뷰 제외는 `not_applicable`, 필수 검토자 부재는 `blocked` 또는 `not_run`으로 기록한다.
   - 준비 상태 리뷰는 초기 리뷰를 포함해 최대 5회이며 세션·담당자 변경으로 초기화하지 않는다. 재시도에는 변경된 작업·요구사항 근거·인터페이스·평가 문맥이 있어야 한다.
   - 작업 결함은 계획으로, 요구사항 모순은 `engineering:brainstorming`으로 돌린다. 산출물·리비전·근거·지적·상태·반환 대상·회차·의사결정 담당자를 기록한다.
   - `passed` 또는 정확한 리비전에 대한 사람의 명시적 `accepted_risk`만 인계 근거다. 상한 도달은 통과가 아니다.
10. **실행자에게 인계한다.** 계획 위치·권한·준비 상태·남은 결정과 unit 의존성·산출물·검사·정책을 전달한다. 직접 실행과 위임은 `engineering:execute-plan`을 따른다. 실행 묶음은 진입 시 현재 의존성·도구 수용량을 다시 확인하고 적격 작업자를 실제로 할당한다. 작은 brief는 직접 전달하고 큰 계획은 `task-brief`가 읽는 파일 사본을 선택적으로 쓴다. 파일 계획과 작업별 커밋은 위임의 선행 조건이 아니다.

## 결과

- 대화 계획 또는 지정 위치의 계획 파일
- `FLOW F<n>` 의사코드, 흐름 대응표, `### Task <n>` 작업과 파일 선언
- 흐름별 검증 방식과 이유, 문서 영향, 커밋 권한, 품질 정책
- 파일 계획의 `validate_plan.py` JSON 결과, 자체 리뷰·준비 상태 근거와 남은 결정

## 예시

입력: `NOTIFY-27` 티켓은 일일 알림 다이제스트를 사용자 시간대의 09:00에 예약하고, 시간대가 없거나 잘못되면 UTC 09:00으로 예약하라고 한다. `src/notify/digest_schedule.py`와 `tests/test_digest_schedule.py`가 있다.

```markdown
**Requirements source:** NOTIFY-27 정상·대체 조건 [제공 자료: 대화에 붙인 티켓 본문, 고정 위치 없음]
**Documentation impact:** 없음
**Commit authorization:** not granted
**Quality policy:** independent (발송 시각이 사용자에게 관찰되는 동작으로 바뀜)

FLOW F1: 사용자 시간대의 다음 09:00을 예약한다
  INPUT: user.timezone=Asia/Seoul, now=2026-10-09T01:30Z
  OUTPUT: send_at=2026-10-10T00:00Z
FLOW F2: 시간대가 없거나 잘못되면 UTC 09:00으로 예약한다
  INPUT: user.timezone=Mars/Base, now=2026-10-09T01:30Z
  CALL: resolve_timezone(user.timezone) → UTC, 경고 로그 1건
  OUTPUT: send_at=2026-10-09T09:00Z

| 흐름 | 요구사항 | 입력과 결과 | 파일과 책임 | 작업과 의존 관계 | 검증과 이유 |
| --- | --- | --- | --- | --- | --- |
| F1 | NOTIFY-27 정상 조건 | 서울 사용자 → 다음 현지 09:00 | `src/notify/digest_schedule.py`: 시각 계산 | Task 1; 없음 | extend_existing_test: 기존 예약 테스트가 같은 함수를 호출함 |
| F2 | NOTIFY-27 대체 조건 | 잘못된 시간대 → UTC 09:00 | `src/notify/timezone_fallback.py`: 시간대 해석 | Task 1; F1 계산 | new_test_file: `resolve_timezone`을 호출하는 기존 검사가 없음 |

### Task 1: 시간대별 다이제스트 예약
**Flows:** `F1`, `F2`
**Files:**
- Modify: `src/notify/digest_schedule.py:30`
- Create: `src/notify/timezone_fallback.py`
- Modify: `tests/test_digest_schedule.py`
- Create: `tests/test_timezone_fallback.py`
- Verify: `tests/test_timezone_fallback.py`
```

`validate_plan.py`가 exit 0과 새 테스트 파일의 `"planned_new": true`를 반환하면 9단계 의미 리뷰로 간다. `Create` 줄이 빠진 계획에서는 `Verify` 줄에 `missing_file`이 나온다. 새로 만들 파일이면 `Create`를 추가하고, 기존 파일을 확인하려던 것이면 경로를 고친다.

대조: 오류 메시지의 오탈자 하나를 고치고 기존 문자열 테스트로 확인하는 요청은 흐름표와 Task 없이 범위·검사 명령·기대 결과만 적는다.

## 경계

- 계획은 Git·외부 권한을 부여하지 않는다. `git add`·`git commit`을 자동 작업 단계로 넣지 않고 푸시·PR·병합·배포는 각각의 권한을 따른다. 실행 방식도 권한을 늘리지 않는다.
- 입력·결과·외부 상태·분기·오류·인터페이스·책임·의존성·범위·위험·검증 전략이 바뀌면 중대한 계획 변경이다. 흐름을 보존하는 도구 이름·동등한 표현·작은 배치는 작업 안에서 처리한다. 중대한 변경은 다음 순서로 처리한다.
  1. 차이와 이유를 기록하고 의존 작업을 보류한다. 독립적인 승인 작업은 계속한다.
  2. 승인된 요구사항·설계·관찰 가능한 계약이 바뀌면 `engineering:brainstorming`으로 변경안을 보내 사용자 재승인을 받는다. 기존 계약 안의 계획 수정은 새 승인 대화 없이 처리한다. 계획 준비 상태는 사용자 승인을 대신하지 않는다.
  3. 의사코드 → 대응 관계 → 작업·검증 순서로 갱신한다.
  4. 영향받은 완료 작업의 이전 근거가 새 흐름을 다루지 않으면 `reopened`로 표시하고 구현·검증·리뷰를 다시 한다.
  5. 변경된 계획에 자체 리뷰·준비 상태 게이트를 적용하고 가장 이른 실행 가능한 미완료·reopened 작업부터 재개한다.
- 설계와 계획 gate는 읽을 수 있는 고정 문서 패키지를 식별한다. 이후 구현 workspace 변화만으로 그 근거를 만료시키지 않고, 실제 계약 변화가 의존 근거를 다시 연다.

## 참고 자료

- [계획 형식](references/plan-format.md): 추적성·검증 선택·전체 양식·검사기 허용 형식
- [공유 출처 태그](../../references/provenance.md)
- [병렬 위임 경계](../../references/delegation.md)
- [품질 게이트 계약](../../references/quality-gates.md)
- [계획 검토자](plan-document-reviewer-prompt.md)
- [검증 방식 선택](../test-driven-development/verification-selection.md)
