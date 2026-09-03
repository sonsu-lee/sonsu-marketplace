---
name: ticket-lifecycle
description: 기존 Linear, GitHub Issues 또는 Jira 티켓의 상태·담당자·blocking·related·duplicate 관계를 시작, review, 완료, reopen, cancel, assign, unassign, block, unblock 요청에 따라 변경하거나 lifecycle 결과를 확인해야 할 때 사용한다. 티켓 생성·초안, Git 작업 또는 PR 작성만 요청한 경우에는 사용하지 않는다.
---

# ticket-lifecycle: 기존 티켓 변경하기

## 책임과 권한을 구분한다

기존 티켓의 상태·담당자·native relation만 변경한다. 함께 요청된 새 티켓, Git과 PR 책임은 runtime에서 독립적으로 조합한다.

조회·설명 요청은 원격 쓰기를 허가하지 않는다. 티켓과 변경 의도를 명시해야 mutation할 수 있다. 일반 코드 작업이나 branch ID만으로 바꾸지 않는다. `ENG-123`처럼 모호한 key는 URL, 사용자 맥락, tracker 또는 integration으로 확인한다.

## 요청을 operation으로 만든다

주 티켓과 relation target을 각각 다음 정보로 정규화한다.

```text
provider: github | linear | jira
key, url, scope
verified: true | false
canonical: true | false
```

```text
status_intent: start | review | ready | complete | reopen | cancel | none
assignee_change:
  { action: assign, target: { id, display_name, verified } }
  | { action: unassign, target: none }
  | none
relation_operations: Array<{
  action: add | remove
  kind: blocked-by | blocks | related | duplicate
  target: verified canonical ticket
}>
```

status intent는 최대 하나다. “나”도 현재 tracker identity 없이 account ID로 추정하지 않는다. `A is blocked by B`와 `A blocks B`의 방향을 보존한다. `unblock`은 target과 방향이 일치하는 기존 relation을 확인한 뒤 제거한다. `duplicate`는 어떤 티켓이 어느 canonical target의 중복인지 보존한다. target이나 방향을 확정할 수 없으면 쓰지 않는다.

## 현재 상태를 읽고 한 번씩 적용한다

- GitHub Issues: [GitHub lifecycle](references/github.md)
- Linear: [Linear lifecycle](references/linear.md)
- Jira: [Jira lifecycle](references/jira.md)

status, transition, assignee, relation, automation과 권한을 읽는다. 이름과 ID를 추정하지 않는다. completed·canceled 티켓은 명시적인 `reopen` 없이 되돌리지 않는다.

각 operation은 순서대로 처리한다.

1. 이미 목표 상태·담당자·relation이면 `no-op`으로 기록한다.
2. 지원되고 권한이 확인된 operation을 한 번 적용한다.
3. canonical 티켓을 다시 읽어 실제 결과를 확인한다.
4. `applied | unapplied | unknown | no-op`으로 분류한다.

부분 실패 뒤 최신 상태에서 같은 종류·방향·target의 미적용 operation만 재시도한다. 불명확한 operation은 반복하지 않는다. 권한 부족, 미지원과 확인 불가를 구분한다. 로그인, 계정 전환, integration 설치와 권한 확대를 자동 수행하지 않는다.

## relation과 status를 섞지 않는다

`block`과 `unblock`은 native blocked-by·blocking relation을 먼저 처리한다. Waiting 또는 Blocked status는 대상 공간에 독립적인 정책과 유효한 transition이 있을 때만 별도 operation으로 적용한다. `related`와 `duplicate`도 native relation을 우선하고 관련 없는 status를 바꾸지 않는다. native operation에 provider 고유의 필수 상태 효과가 있으면 실행 전에 확인한다. 요청이 그 효과를 금지하면 원격 호출 없이 operation을 `unapplied`, reason을 `conflict`로 보고한다. 구조화된 relation이 없으면 `unsupported`로 보고하며, body 수정까지 명시적으로 요청받은 경우에만 의미를 본문에 보존한다.

PR event automation이 구성되었으면 그 event의 status effect를 직접 중복 적용하지 않는다. automation 부재·비적용, 현재 상태, 목표 transition, 권한과 전이 의도가 모두 확인된 경우에만 직접 fallback한다. 비동기 결과가 불명확하면 `unknown`으로 보고하고 전이하지 않는다.

## 결과를 보고한다

provider, canonical key·URL, 변경 전후 상태와 operation별 target·결과·근거를 보고한다. 적용하지 않은 요청, 권한·interface 제한, 불명확한 automation과 남은 후속 작업을 성공한 변경과 분리한다.
