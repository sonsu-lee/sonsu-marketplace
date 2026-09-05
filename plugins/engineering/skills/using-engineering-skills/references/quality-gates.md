# Engineering 품질 게이트 계약

Engineering lifecycle 스킬이 품질 게이트를 선언할 때 이 계약을 사용한다. artifact를 만드는
단계가 해당 게이트와 반환 경로를 소유한다. 중앙 게이트 dispatcher를 만들거나 전체 workflow를
재귀적으로 호출하지 않는다.

## 품질 판정은 권한이 아니다

품질 게이트는 현재 artifact에 다음 단계로 진행할 충분한 근거가 있는지 판단한다. 영속 문서
작성, 구현, staging, commit, push, PR 생성, merge, 배포, 게시 또는 다른 외부 작업의 권한은
절대 부여하지 않는다. 관련 권한 게이트를 별도로 적용한다.

## 실행 전에 게이트를 정의한다

대화, plan, 진행 ledger 또는 review package에 다음 필드를 기록한다.

```text
Gate: <stable gate id>
Artifact: <path, task, diff, or other exact scope>
Revision: <commit SHA, content digest, or saved review-package identity>
Required checks: <checks that must produce evidence>
Pass condition: <observable result>
Evidence: <commands, outputs, review result, or human decision>
Findings: <none or unresolved findings>
Status: <status below>
Return target: <nearest stage that can change the failing input>
Attempt: <current>/<cap>
Decision owner: <stage owner or named human decision-maker>
```

첫 실행 전에 필수 검사, 통과 조건, 반환 대상과 유한한 시도 횟수 상한을 정한다. 파일이
commit되지 않았다면 content digest 또는 변경할 수 없는 review package를 사용한다. artifact가
바뀌면 이전 판정을 그대로 복사하지 않는다. 아래 변경 영향 규칙으로 필요한 검증과 리뷰를
갱신하고, 재사용한 근거와 새 근거가 현재 리비전 전체의 필수 조건을 다루는지 기록한다.

별도 stage가 더 낮은 상한을 선언하지 않는 한 자동 review/fix loop는 최대 5회다. 횟수 상한은
같은 evaluator와 context를 반복 사용하는 허가가 아니다. 재시도 조건에 evaluator 또는 context
변경이 포함되면 이전 session history를 상속하지 않는 fresh context에 필요한 artifact만 전달한다.
상한은 목표 횟수가 아니다. task/gate ID와 소비한 횟수를 유지하며 session 교체, owner 반환,
package 재생성으로 예산을 초기화하지 않는다. 각 owner 호출은 남은 상위 gate 예산 안에서
수행하고 종료 조건을 먼저 정한다. 중첩 loop마다 새 5회 예산을 발급하지 않는다.

digest는 내용을 식별하지만 노출하지 않는다. 독립 evaluator가 commit하지 않은 artifact를
검사해야 한다면 digest와 함께 읽을 수 있는 고정 package를 제공한다. working tree 변경을
누락한 현재 commit range는 이와 같지 않다.

## 상태

| 상태 | 의미 | 필수 게이트를 통과할 수 있는가? |
| --- | --- | --- |
| `passed` | 모든 필수 검사에서 현재 리비전의 통과 조건을 충족하는 근거가 나왔다 | 예 |
| `failed` | 필수 조건을 충족하지 못했음이 근거로 드러났다 | 아니요 |
| `blocked` | capability, 권한, dependency 또는 외부 상태의 부재가 필수 검사나 수정을 막는다 | 아니요 |
| `inconclusive` | 근거가 있지만 통과 또는 실패를 뒷받침하지 못한다 | 아니요 |
| `not_run` | 필수 또는 제안 검사를 실행하지 않았다 | 아니요 |
| `not_applicable` | 현재 artifact에 적용되지 않아 실행 전에 검사 대상에서 제외했다 | 다른 모든 필수 검사를 충족한 경우에만 가능 |
| `accepted_risk` | 지명된 사람인 의사결정자가 현재 리비전의 명시된 미해결 위험을 명시적으로 수용했다 | 예. 단, `passed`로 보고하지 않는다 |

사용자 또는 식별되고 권한을 가진 다른 사람인 의사결정자만 `accepted_risk`를 설정할 수 있다.
controller, implementer, reviewer, retry 상한, 일정 또는 token budget은 이를 만들 수 없다.
위험을 수용하고 진행할 때에는 finding, 결과, 범위, 리비전과 결정 근거를 보존한다.

## 판단보다 저렴한 oracle을 먼저 실행한다

추론 기반 리뷰 전에 질문을 판정할 수 있는 결정론적 검사를 실행한다. 여기에는 테스트, type
check, build, parser, native loader, link/path 검사와 실제 소비 명령이 포함된다. 독립 reviewer는
판단이 위험을 실질적으로 줄이는 곳에 사용하고, 사용할 수 있는 oracle을 대신하는 용도로 쓰지 않는다.

독립 리뷰는 일반적으로 다음 경계에서 비용을 들일 가치가 있다.

- 아키텍처 또는 고위험 영속 설계 문서
- 여러 component에 걸치거나 오래 걸리거나 위험도가 높은 구현 계획
- 각 subagent 구현 task
- 크거나 위험도가 높은 직접 변경과 최종 전체 변경

구현 plan이 있는 작업의 whole-change gate에는 위험도와 관계없이 일반 final review 뒤
fresh-context red-team challenge가 필요하다. 이는 plan artifact 존재로 trigger하며, plan 없는
Fast Path에는 적용하지 않는다. challenge 전에는 목표, 요구사항·설계, plan·mapping, 전체 diff,
검증 report, 관찰 결과·제약과 review finding provenance의 내용을 하나의 immutable bundle로
복사하고 bundle 전체 digest를 고정한다. mutable source 경로를 별도로 reviewer에게 넘기지 않는다.
challenge verdict는 quality status와 분리해 기록한다.

| Challenge verdict | Quality status | 의미 |
| --- | --- | --- |
| `survives_challenge` | `passed` | 전체 전제를 뒤집을 근거가 없고 필수 검사가 충족됨 |
| `invalidated` | `failed` | 목표·요구사항·설계·plan·구현 또는 review 방향이 근거로 반증됨 |
| `inconclusive` | `inconclusive` | 판정에 필요한 실제 근거가 부족함 |
| `blocked` | `blocked` | artifact, capability 또는 외부 상태가 challenge를 막음 |

문서, metadata와 단순 설정에는 보통 변경에 비례한 결정론적 검사가 필요하다. 리뷰가 선택
사항이고 의도적으로 제외했다면 `not_applicable`로 기록한다. 필수지만 사용할 수 없었다면
게이트를 조용히 약화하지 말고 `blocked` 또는 `not_run`으로 기록한다.

## Fast Path의 현재 판단과 영속 예산

Fast Path의 판정과 실행은 [brainstorming](../../brainstorming/SKILL.md)의 bounded 계약을 따른다.
controller가 실제 현재 파일과 consumer를 확인하며, 별도 classifier subagent는 필수가 아니다.
`HEAD` 일치나 과거 `eligible` 기록은 미커밋 변경을 포함한 현재 작업의 자격을 증명하지 않는다.
긍정 판정은 중단 없는 현재 실행에만 사용한다. 영속 상태에는 stable task ID의 소비한 탐색·실행
예산과 `disqualified`만 남긴다. 재개, context 손실, handoff 또는 설명되지 않는 파일 변경에서는
과거 판정을 복구하지 않고 일반 workflow로 올린다. 같은 실행에서 확인한 자신의 수정과 허용된
집중 수정은 재개로 취급하지 않는다. ID 교체나 재분류로 예산 또는 탈락 기록을 초기화하지 않는다.
이 gate는 구현, 위임 또는 Git 권한을 부여하지 않는다.

## 가장 가까운 소유 단계로 돌아간다

| 실패 | 반환 대상 |
| --- | --- |
| 동작 검사 또는 테스트 실패 | task 구현. 원인을 모르면 systematic debugging을 사용한다 |
| 유효한 task-review finding | task의 집중 수정 loop를 거친 뒤 범위를 제한해 재리뷰한다 |
| 불완전하거나 모순된 plan | 영향을 받은 task 또는 interface의 `writing-plans` |
| 요구사항 또는 설계 모순 | 논쟁 중인 결정의 `brainstorming` |
| 통합에서만 발생한 실패 | 전체 프로젝트가 아니라 통합 단계 또는 영향받은 구현 |
| 도구, 권한, service 또는 외부 상태 부재 | `blocked`. capability 변경이나 사람의 조치를 기다린다 |
| Reviewer 의견 불일치 | 결정적 근거를 수집하거나 요구사항을 명확히 하거나 사람의 판정을 요청한다 |
| Red-team이 구현을 반증 | 영향받은 task 구현 |
| Red-team이 task·interface plan을 반증 | `writing-plans`의 영향받은 flow 또는 task |
| Red-team이 설계·해결책을 반증 | `brainstorming` |
| Red-team이 원래 문제 정의·사용자 목표를 반증 | 사용자 재승인 |
| Red-team이 실제 효과 근거 부족을 발견 | 검증 단계 또는 제품 실험 |
| Red-team이 기존 review finding·수정 방향을 반증 | finding을 근거와 함께 무효화하고 영향 task를 `reopened` |

마지막 green checkpoint와 이미 검증한 작업을 보존한다. 되돌아가기는 표적화된 상태 전환이며,
재시작이나 재귀적인 자기 호출이 아니다.

## 변경 영향에 따른 근거 갱신

최초 일반 final review와 최초 red-team은 전체 변경을 검토한다. 수정 후에는 기존 finding의
해결 여부와 수정으로 생긴 회귀를 검토한다. unrelated 개선안이나 새로운 위협 모델을 자동으로
완료 조건에 추가하지 않는다. 승인 범위의 결함과 새 요구사항을 구분하고 후자는 별도 결정으로 올린다.

국소 수정의 영향이 확인되면 전체 리뷰를 다시 시작하지 않고 다음 근거를 현재 gate에 연결한다.

- 이전 전체 리뷰의 artifact/revision과 아직 유효한 검증 범위
- 이전 revision부터 현재 revision까지의 실제 delta와 영향을 받는 계약·consumer
- 변경 부분의 검증 명령·결과와 scoped reviewer의 finding별 판정 및 회귀 확인
- 영향받지 않은 근거를 재사용하는 이유, 남은 필수 조건과 현재 artifact/revision

scoped 결과만으로 전체 `passed`를 만들지 않는다. 위 근거의 합이 현재 전체 필수 조건을
충족해야 한다. reviewer가 영향 경계를 확인할 수 없거나 목표·승인 계약·설계·dependency 경계가
바뀌면 해당 전체 gate를 다시 연다. 설계 변경에는 사용자 재승인이 먼저 필요하다.
required full test suite는 영향 범위에 따라 계속 실행하되, 같은 bytes에 대한 검증은 중복하지 않는다.

red-team도 최초에는 전체 목표를 독립 검토하고, 국소 수정 뒤에는 현재 전체 bundle을 제공하되
이전 반례와 수정 회귀에 범위를 제한한 새 context로 검토한다. 전체 전제가 바뀌거나 영향이
불명확하면 broad challenge를 다시 연다. 일반 gate와 red-team gate는 별도로 현재 리비전에
기록하며 어느 한쪽의 통과가 다른 쪽을 대신하지 않는다.

## 정보가 달라졌을 때 재시도한다

재시도할 때마다 artifact, 가설, 구현, 근거, context, evaluator, 사용 가능한 capability 또는 human decision 중
하나 이상이 달라져야 한다. 바뀌지 않은 artifact에 동일한 결정론적 명령을 반복하지 않고,
같은 evaluator에게 변경 없는 입력으로 “try harder”라고 지시하지 않는다.

시도 횟수 상한에서는 다음과 같이 처리한다.

1. 근거에서 finding이 유효하지 않거나 선언한 게이트 범위 밖임이 드러난 경우에만 닫는다.
2. 유효한 미해결 finding은 가장 가까운 소유 단계로 보내고, 게이트의 `failed` 또는 `blocked`
   상태와 함께 산문으로 `decision_required`를 기록한다.
3. 새 리비전이 통과하거나 사람이 현재 리비전에 대해 `accepted_risk`를 명시적으로 기록한
   뒤에만 진행한다.

경미한 권고 사항이 통과 조건에 포함된 적이 없다면 나중으로 미룰 수 있다. retry 상한에
도달했다는 이유만으로 유효한 필수 finding이 `passed`가 되지는 않는다.
