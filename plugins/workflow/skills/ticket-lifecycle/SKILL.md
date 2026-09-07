---
name: ticket-lifecycle
description: 기존 Linear, GitHub Issues 또는 Jira 티켓의 상태·담당자·blocking·related·duplicate 관계를 시작, review, 완료, reopen, cancel, assign, unassign, block, unblock 요청에 따라 변경하거나 lifecycle 결과를 확인해야 할 때 사용한다. 티켓 생성·초안·제목·본문 수정, Git 작업 또는 PR 작성만 요청한 경우에는 사용하지 않는다.
---

# ticket-lifecycle: 상태·담당자·관계 변경

## 작업 연속성

현재 메인 controller가 여러 단계의 작업을 소유하거나 외부 쓰기를 수행할 때에는 같은 플러그인의
[task-continuity](../task-continuity/SKILL.md)를 적용해 시작·중요한 진행 변화·외부 쓰기 전후를 기록한다.
컴팩션·재개 후에는 그 기록과 현재 근거를 대조한다. 짧은 단발 작업, 위임된 subagent와 fresh reviewer는
별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 변경하지 않는다.

## 책임과 권한을 구분한다

기존 티켓의 상태·담당자·native relation만 변경한다. 제목·본문 작성과 수정은 `to-ticket`의 책임이다. 함께 요청된 내용 수정·새 티켓·Git·PR은 runtime에서 독립적으로 조합한다. 본문 보강만으로 상태를 전이하지 않는다.

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
  | { action: unassign, target: { id, display_name, verified } | all }
  | none
relation_operations: Array<{
  action: add | remove
  kind: blocked-by | blocks | related | duplicate
  target: verified canonical ticket
}>
```

status intent는 최대 하나다. “나”도 현재 tracker identity 없이 account ID로 추정하지 않는다. 특정 담당자 해제는 현재 assignee에서 검증한 사용자를 target으로 보존하고, `all`은 사용자가 모든 담당자 해제를 명시한 경우에만 사용한다. 다중 assignee에서 특정 사용자와 `all` 중 어느 의도인지 확정할 수 없으면 쓰지 않는다. `A is blocked by B`와 `A blocks B`의 방향을 보존한다. `unblock`은 target과 방향이 일치하는 기존 relation을 확인한 뒤 제거한다. `duplicate`는 어떤 티켓이 어느 canonical target의 중복인지 보존한다. target이나 방향을 확정할 수 없으면 쓰지 않는다.

## 현재 상태를 읽고 한 번씩 적용한다

- GitHub Issues: [GitHub lifecycle](references/github.md)
- Linear: [Linear lifecycle](references/linear.md)
- Jira: [Jira lifecycle](references/jira.md)

status, transition, assignee, relation, automation과 권한을 읽는다. 이름과 ID를 추정하지 않는다. completed·canceled 티켓은 명시적인 `reopen` 없이 되돌리지 않는다.

내용 수정 성공을 전제로 인계받은 작업은 먼저 [수정 결과와 후속 lifecycle](../to-ticket/SKILL.md#수정-결과와-후속-lifecycle)의 선행 조건과 동일 canonical ticket의 검증 근거를 확인한다. 필요한 content field에 `unapplied`·`unknown` 또는 근거 누락이 있으면 후속 mutation을 보류한다. 독립 수행이 명시된 요청에만 별도 진행을 허용하며, 인계된 과거 status를 그대로 사용하지 않고 실행 시점의 현재 상태·권한을 읽는다.

각 operation은 순서대로 처리한다.

1. 이미 목표 상태·담당자·relation이면 `no-op`으로 기록한다.
2. 지원되고 권한이 확인된 operation을 한 번 적용한다.
3. canonical 티켓을 다시 읽어 실제 결과를 확인한다.
4. `applied | unapplied | unknown | no-op`으로 분류한다.

부분 실패 뒤 최신 상태에서 같은 종류·방향·target의 미적용 operation만 재시도한다. 불명확한 operation은 반복하지 않는다. 권한 부족, 미지원과 확인 불가를 구분한다. 로그인, 계정 전환, integration 설치와 권한 확대를 자동 수행하지 않는다.

## relation과 status를 섞지 않는다

`block`과 `unblock`은 native blocked-by·blocking relation을 먼저 처리한다. Waiting 또는 Blocked status는 대상 공간에 독립적인 정책과 유효한 transition이 있을 때만 별도 operation으로 적용한다. `related`와 `duplicate`도 native relation을 우선하고 관련 없는 status를 바꾸지 않는다. native operation에 provider 고유의 필수 상태 효과가 있으면 실행 전에 확인한다. 요청이 그 효과를 금지하면 원격 호출 없이 operation을 `unapplied`, reason을 `conflict`로 보고한다. 구조화된 relation이 없으면 `unsupported`로 보고하며, body 수정까지 명시적으로 요청받은 경우에만 내용 수정 책임을 `to-ticket`과 조합해 의미를 본문에 보존한다.

PR event automation이 구성되었으면 그 event의 status effect를 직접 중복 적용하지 않는다. automation 부재·비적용, 현재 상태, 목표 transition, 권한과 전이 의도가 모두 확인된 경우에만 직접 fallback한다. 비동기 결과가 불명확하면 `unknown`으로 보고하고 전이하지 않는다.

## 결과를 보고한다

provider, canonical key·URL, 변경 전후 상태와 operation별 target·결과·근거를 보고한다. 적용하지 않은 요청, 권한·interface 제한, 불명확한 automation과 남은 후속 작업을 성공한 변경과 분리한다.
