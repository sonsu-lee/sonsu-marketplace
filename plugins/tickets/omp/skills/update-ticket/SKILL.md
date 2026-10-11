---
name: update-ticket
description: 기존 GitHub Issues·Linear 티켓의 상태·담당자·blocking·related·duplicate 관계를 변경하거나 lifecycle 결과를 확인할 때 사용한다. 티켓 생성·제목·본문 수정은 write-ticket이 담당한다.
---

# update-ticket: 상태·담당자·관계 변경

검증된 기존 티켓에 사용자가 요청한 상태·담당자·native relation 변경을 적용한다. 관계 방향과 플랫폼의 자동 상태 효과를 확인하고, 실제 반영 결과를 operation별로 보고한다.

## 절차

1. **대상과 변경 권한을 확인한다.** 티켓과 변경 의도가 명시된 요청을 mutation으로 구분하고 조회·설명 요청은 읽기 전용으로 처리한다. `ENG-123`처럼 모호한 key는 URL, 사용자 맥락, tracker 또는 integration으로 확인한다. 함께 요청된 내용 수정·새 티켓·Git·PR은 runtime에서 각 담당 스킬과 독립적으로 조합한다.

   여러 단계의 작업이나 외부 쓰기를 맡은 메인 controller는 [연속성 참고 자료](../../references/continuity.md)로 진행과 근거를 기록한다. 컴팩션·재개 후에는 실제 상태와 대조한다. 짧은 단발 작업과 위임된 작업자는 별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 수정하지 않는다.

2. **요청을 operation으로 정규화한다.** 주 티켓과 relation target을 각각 다음 정보로 확인한다. status intent는 최대 하나다.

   ```text
   provider: github | linear
   key, url, scope
   verified: true | false
   canonical: true | false
   ```

   ```text
   status_intent: start | review | ready | complete | reopen | cancel | none
   assignee_change:
     { action: assign, target: { id, display_name, verified } }
     | { action: unassign, target: { id, display_name, verified } | all }
     | none
   relation_operations: Array<{
     action: add | remove
     kind: blocked-by | blocks | related | duplicate
     target: verified canonical ticket
   }>
   ```

   “나”는 현재 tracker의 사용자 정보로 확인한다. 특정 담당자 해제는 현재 담당자에서 확인한 사용자를 대상으로 하며, `all`은 모든 담당자 해제를 명시한 경우에만 사용한다. `A is blocked by B`와 `A blocks B`의 방향을 보존한다. `unblock`은 대상과 방향이 일치하는 기존 관계를 확인한 뒤 제거한다. `duplicate`는 중복 티켓과 기준 티켓의 방향을 보존한다.

3. **인계 조건과 현재 상태를 읽는다.** 내용 수정과 함께 인계받은 요청은 [수정 결과와 후속 lifecycle](../write-ticket/SKILL.md#수정-결과와-후속-lifecycle)의 인계 필드와 결과별 행동을 그대로 따른다. [GitHub lifecycle](references/github.md) 또는 [Linear lifecycle](references/linear.md)을 읽고 실행 시점의 status, transition, assignee, relation, automation과 권한을 조회한다. 실제 이름과 ID를 사용하고, 지원하지 않는 tracker이면 지원 범위를 알린다.
4. **관계와 상태 효과를 구분한다.** `block`·`unblock`은 플랫폼의 blocked-by·blocking 관계를 먼저 처리한다. Waiting·Blocked 상태는 대상 공간의 별도 정책과 유효한 transition이 있을 때만 추가로 변경한다. `related`·`duplicate`도 관계 기능을 우선한다. 관계 변경의 플랫폼 고유 필수 상태 효과는 실행 전에 확인하고, 사용자 금지와 충돌하면 호출을 보류해 `unapplied`, reason `conflict`로 보고한다. 관계 기능이 없으면 `unsupported`로 알린다. 본문 수정까지 요청받았을 때만 `write-ticket`과 조합해 본문에 의미를 보존한다.

   PR event automation이 구성되었으면 해당 event의 status effect를 automation으로 확인한다. automation 부재·비적용, 현재 상태, 목표 transition, 권한과 전이 의도가 모두 확인된 경우에만 직접 fallback한다. 비동기 결과가 불명확하면 `unknown`으로 보고하고 전이를 보류한다.

5. **각 operation을 순서대로 한 번씩 적용한다.**
   1. 이미 목표 상태·담당자·relation이면 `no-op`으로 기록한다.
   2. 지원되고 권한이 확인된 operation을 한 번 적용한다.
   3. canonical 티켓을 다시 읽어 실제 결과를 확인한다.
   4. `applied | unapplied | unknown | no-op`으로 분류한다.

   부분 실패 뒤에는 최신 상태에서 같은 종류·방향·target의 미적용 operation만 재시도한다. 권한 부족, 미지원과 확인 불가를 구분한다.

6. **operation별 결과를 보고한다.** 설명과 보고에 Writing·Fluent를 함께 적용할 때는 [작성 지침 결합 기준](../../references/writing-composition.md)을 따른다. 해당 스킬이 없어도 작업은 계속하며 코드·식별자·링크와 의미를 보존한다.

## 결과

프로바이더, canonical key·URL, 변경 전후 상태와 operation별 target·결과·근거를 보고한다. 결과는 `applied | unapplied | unknown | no-op`으로 구분한다. 적용하지 않은 요청, 권한·인터페이스 제한, 불명확한 automation과 남은 후속 작업을 성공한 변경과 분리한다.

## 예시

예시 입력: “Linear `DOC-84`가 `OPS-29`에 막혀 있는 관계만 풀어 줘. 상태는 유지해.” 두 티켓은 URL·workspace·team으로 확인됐고, 현재 관계가 `DOC-84 is blocked by OPS-29`이며 제거에 필수 상태 효과가 없다고 조회된 상황을 가정한다.

- `status_intent: none`, `assignee_change: none`, relation은 `action: remove`, `kind: blocked-by`, target은 검증된 `OPS-29`로 정한다. 한 번 제거한 뒤 `DOC-84` 재조회에서 해당 관계의 제거와 상태 유지를 확인하면 `applied`로 보고한다.
- 대조 입력: 같은 요청에서 재조회한 현재 관계가 이미 제거돼 있다. 목표 상태가 확인됐으므로 원격 쓰기 없이 `no-op`으로 보고한다. 반대 방향의 다른 관계는 유지한다.

## 경계

- 제목·본문 작성과 수정은 `write-ticket`의 책임이다. 일반 코드 작업, branch ID, 본문 보강 또는 조회·설명 요청만으로 원격 변경 권한을 확대하지 않는다. Git·PR 작업만 요청받았을 때 lifecycle 변경을 실행하지 않는다.
- 사용자·티켓·관계의 ID를 추정하지 않는다. 담당자 해제 의도나 relation의 대상·방향이 불명확하면 변경하지 않는다. completed·canceled 티켓은 명시적인 `reopen` 없이 되돌리지 않는다.
- 지원하지 않는 tracker에는 lifecycle 변경을 수행하지 않는다. 관계 변경 때문에 관련 없는 상태를 바꾸거나 PR automation의 status effect를 직접 중복 적용하지 않는다.
- 불명확한 operation은 반복하지 않는다. 로그인, 계정 전환, integration 설치와 권한 확대를 자동 수행하지 않는다.

## 참고 자료

- [GitHub lifecycle](references/github.md), [Linear lifecycle](references/linear.md)
- [수정 결과와 후속 lifecycle](../write-ticket/SKILL.md#수정-결과와-후속-lifecycle)
- [연속성 참고 자료](../../references/continuity.md), [작성 지침 결합 기준](../../references/writing-composition.md), [호스트별 도구](../../references/hosts.md)
