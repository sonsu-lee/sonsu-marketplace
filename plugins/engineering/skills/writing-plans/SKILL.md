---
name: writing-plans
description: 여러 단계의 구현 task에 대해 승인된 설계나 요구사항이 있고 코드를 수정하기 전일 때 사용한다
---

# writing-plans: 계획 작성

## 개요

codebase를 거의 모르는 엔지니어도 실행할 수 있는 구현 계획을 작성한다. 먼저 검토 가능한
의사코드로 전체 동작과 제어 흐름을 정의하고, 그 흐름에서 정확한 파일, task, dependency와
검증을 도출한다. 계획은 독립적으로 이해할 수 있고 초점이 분명하며 추측성 작업을 포함하지
않아야 한다.

**시작할 때 알린다:** "I'm using the writing-plans skill to create the implementation plan."

실행에 격리된 worktree를 사용할 예정이면 실행 시점에 `engineering:using-git-worktrees`로 만들거나 확인한다.

## Plan 위치

기본 산출물은 chat 안에 작성하는 plan이다. `docs/engineering/plans/` 또는 날짜 기반 plan 파일을 만들지 않는다.

실행 도구에 파일이 필요하면 scratch 사본을 다음 위치에 저장한다.

```text
.superpowers/plans/<feature-name>.md
```

scratch 경로는 Git에서 제외해야 한다. 저장소가 이미 issue, ticket 또는 다른 plan 위치를 사용하거나 사용자가 위치를 지정했다면 그 관례를 따른다. plan 파일 작성은 staging이나 commit 권한을 부여하지 않는다.

## 문서 확인

task를 정의하기 전에 승인된 설계 또는 요구사항과 관련 기존 문서를 읽는다. 다음 결과 중 하나를 plan에 기록한다.

- 문서 변경 없음
- 기존 문서 갱신
- 승인된 영속 문서 생성
- 기존 결정 대체

구현 plan 자체를 영속 설계 문서로 만들지 않는다. 계획 과정에서 빠진 결정이나 기존 문서와의 충돌이 드러나면 구현 전에 finding을 사용자에게 알린다.

## Plan이 필요한지 판단

여러 단계, 파일 또는 component가 연결되거나 interface, 상태 전이, 오류 처리, migration이나
회귀 위험을 조정해야 하면 구현 plan을 작성한다. 오탈자, 명백한 한 줄 수정, 기계적인 이름 변경처럼
별도 구현 plan 없이 바로 범위를 설명하고 검증할 수 있는 작업에는 긴 의사코드를 만들지 않는다.

구현 plan을 작성하기로 했다면 아래 의사코드 단계를 생략하지 않는다. plan의 세부 정도는 작업
복잡성에 맞추되 순서는 다음과 같다.

```text
의사코드로 전체 작업 흐름 정의
  → 흐름을 파일·task·dependency에 연결
  → 각 흐름에 적합한 테스트·검증 방법과 이유 선택
```

## 의사코드로 동작 흐름 정의

구현 세부사항, 파일별 단계 또는 TDD 적용 여부를 정하기 전에 요구사항과 기존 코드 흐름을
언어 중립적인 의사코드로 정리한다. 이 의사코드는 production code도, 모델의 숨은 사고 과정도
아니다. implementer와 reviewer가 구현 전에 동작, 제어 흐름과 책임 경계를 검토할 수 있는
외부 산출물이다.

각 흐름에 `F1`, `F2` 같은 안정적인 ID를 부여하고 작업 성격상 필요한 항목을 표현한다.

- 입력과 관찰 가능한 기대 결과
- 주요 처리 순서
- 데이터 또는 상태 변화
- 조건 분기와 반복
- 오류, 예외와 경계 조건
- 기존 코드와 새 코드의 책임 경계
- 확인되지 않은 가정과 구현 전에 필요한 결정

모든 항목을 형식적으로 채우지 않는다. 상태나 반복이 없는 작업에는 만들지 않으며, 확인되지 않은
내용을 사실처럼 채우지 않는다. 미확인 가정이 구현 방향을 바꿀 수 있으면 decision으로 올려
구현 전에 해결한다. 다음은 형식의 예시이지 특정 문법을 강제하는 template이 아니다.

```text
FLOW F1: [관찰 가능한 결과]
  INPUT: [기존 호출자나 사용자가 제공하는 값]
  READ: [현재 코드 또는 상태]
  IF [조건]:
      CHANGE [데이터 또는 상태]
  ELSE:
      RETURN [경계 또는 오류 결과]
  OUTPUT: [호출자나 다음 흐름이 받는 결과]
  BOUNDARY: [기존 책임] / [새 책임]
  ASSUMPTION OR DECISION: [확인할 내용]
```

## 흐름을 구현 plan으로 연결

요구사항이 독립적으로 구현하고 검증할 수 없는 여러 subsystem을 포함한다면 plan을 분리하자고 제안한다. task를 정의하기 전에 생성하거나 수정할 정확한 파일과 각 파일의 책임을 연결한다.

- 기존 project pattern을 따른다.
- 각 단위의 초점을 유지하고 interface를 명시한다.
- 설정, configuration, 문서와 migration 작업은 해당 작업을 필요로 하는 산출물의 task에 포함한다.
- reviewer가 한 부분은 승인하고 다른 부분은 거부할 수 있는 의미 있는 경계에서만 task를 나눈다.
- 관련 없는 refactoring을 포함하지 않는다.

각 의사코드 흐름을 다음 표에 연결한다. 한 흐름이 여러 task에 걸치거나 여러 흐름이 한 task에
모이면 dependency와 책임 경계를 명시한다. `Verification and reason`은 아래 검증 선택을 마친 뒤
채운다.

| Flow | Inputs and outcomes | Files and responsibilities | Task and dependencies | Verification and reason |
| --- | --- | --- | --- | --- |
| `F1` | [input → outcome] | [`path`: existing/new responsibility] | [Task N; depends on F0/Task M] | [method; why it fits the behavior and risk] |

## 검증 선택

의사코드와 파일·task·dependency mapping을 만든 뒤, 모든 변경에 하나의 절차를 적용하지 말고
흐름의 동작 민감도, 회귀 위험과 검증 실익을 기준으로 task마다 방법을 선택한다. 선택한 방법과
이유를 flow mapping과 task에 모두 기록한다. 코드 파일을 수정한다는 사실만으로 TDD를 선택하지
않는다.

| 변경 성격 | 선택 기준과 Plan |
| --- | --- |
| 기능 추가, 로직·상태 전이·오류 처리 변경 | 관찰 가능한 계약과 회귀 위험을 자동화 테스트로 유용하게 보호할 수 있는지 판단한다. TDD를 선택하면 `engineering:test-driven-development`를 사용하고 RED, GREEN, 회귀 명령을 포함한다. |
| 버그 수정 | 재현 가능한 결함은 실패하는 회귀 테스트를 우선한다. 자동화 실익이 낮거나 불가능하면 이유와 가장 강한 재현·검증 절차를 기록한다. |
| 동작에 민감한 refactoring | 바뀔 수 있는 동작을 테스트로 보호할 가치가 있으면 TDD 또는 characterization/regression test를 선택한다. 순수한 기계적 변경에는 강제하지 않는다. |
| 문서 | link, 경로, 예시와 관련 문서 사이의 일관성을 확인한다. |
| 스킬 지침 | frontmatter와 경로를 검증하고, 위험에 필요할 때에만 현실적인 동작 평가를 추가한다. |
| Manifest 또는 metadata | syntax를 parse하고 참조 경로를 검증하며, 사용할 수 있으면 native loader를 사용한다. |
| 단순 configuration | 변경된 configuration을 소비하는 가장 작은 명령을 실행한다. |

정적 text, metadata 또는 구현을 그대로 반복하는 가치 없는 테스트를 추가하지 않는다. TDD가
적합한 것으로 분류된 task에는 test-first cycle을 완전하게 적용한다. TDD를 선택하지 않은
task에는 syntax, static analysis, path check, native loader, build, smoke test 또는 실제 소비
명령 중 변경 위험에 비례한 검증을 지정한다. 테스트는 의사코드로 정의한 동작을 검증하는
수단이지 plan의 출발점이나 그 자체의 목적이 아니다.

## Commit 권한

plan은 Git 권한을 부여하지 않는다. 사용자의 요청에서 현재 상태를 판단하고 다음 값 중 하나를 header에 쓴다.

```text
Commit authorization: granted for this plan
Commit authorization: not granted
```

`git add` 또는 `git commit`을 task 단계로 추가하지 않는다. 잠재적인 commit 경계를 권고 메모로 나열할 수는 있지만 실행에는 명시적인 승인이 필요하다. Push, PR, merge와 배포는 별도의 권한으로 유지한다.

`engineering:subagent-driven-development`는 복구와 review range를 위해 task commit에 의존한다. task commit이 명시적으로 승인된 경우에만 제안한다. 그 외에는 `engineering:executing-plans`로 직접 실행하고, 완료된 `diff`를 보고한 뒤 commit 결정을 요청한다.

## Plan header(계획 머리말)

chat 안의 plan을 포함한 모든 plan은 아래 필드로 시작한다. 그래야 handoff 뒤에도 요구사항,
문서 작업과 Git 경계가 보존된다. 짧은 in-chat plan은 plan 본문에 접근 방식이 이미 있고 추가
전역 제약이 없을 때에만 `Approach`, `Global Constraints`를 생략할 수 있다. `Requirements source`,
`Documentation impact`, `Commit authorization`은 반드시 유지한다.

`Goal`, 요구사항·문서·권한 context와 전역 제약은 의사코드 앞에 둘 수 있지만, 구현 방식을
정하는 `Approach`와 파일별 세부사항은 의사코드 뒤에서 도출한다.

```markdown
# [Feature Name] Implementation Plan

**Goal:** [one sentence]

**Requirements source:** [approved document, issue, ticket, or user-approved conversation design]

**Documentation impact:** [none, update path, create approved path, or supersede decision]

**Commit authorization:** [granted for this plan | not granted]

## Global Constraints

[Exact project-wide constraints that every task must preserve]

## Behavioral Flow Pseudocode

FLOW F1: [reviewable behavior and control flow before implementation details]
  INPUT: [input]
  ...
  OUTPUT: [observable outcome]

## Approach

[Two or three sentences derived from the behavioral flow]

## Flow Mapping

| Flow | Inputs and outcomes | Files and responsibilities | Task and dependencies | Verification and reason |
| --- | --- | --- | --- | --- |
| `F1` | [...] | [...] | [...] | [...] |
```

영속 요구사항 문서가 없다면 원래 대화를 읽을 수 없는 executor도 이해할 만큼 승인된 맥락을 plan에 포함한다.

## Task 구조

파일 기반 plan에는 실행 중 진행 상태를 추적할 수 있도록 checkbox 단계를 사용한다.

````markdown
### Task N: [Deliverable]

**Flows:** `F1`, `F2`

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123`
- Verify: `tests/exact/path/to/test.py` or the applicable validation target

**Interfaces:**
- Consumes: [exact earlier interface or input]
- Produces: [exact interface later tasks rely on]

**Verification:** [TDD, regression test, native loader, syntax/path check, or other proportionate method]

**Verification reason:** [why this method fits the mapped flow and regression risk]

- [ ] **Step 1: Establish the expected behavior or invariant**

[Actual test, command, or invariant. For TDD tasks, include the failing test and expected failure.]

- [ ] **Step 2: Make the minimal change**

[Exact edit or code needed; no placeholders.]

- [ ] **Step 3: Verify the result**

Run: `[exact command]`
Expected: `[observable result]`

- [ ] **Step 4: Review task diff and documentation consistency**

[Exact paths and requirements to compare.]
````

## Placeholder를 남기지 않는다

다음 내용이 있으면 실행 가능한 plan이 아니다.

- `TBD`, `TODO`, "implement later" 또는 "fill in details"
- 실제 규칙 없이 "add appropriate error handling"이라고만 적은 내용
- 동작, 테스트 위치와 명령 없이 "write tests"라고만 적은 내용
- executor가 task를 독립적으로 볼 수 있는데도 "similar to Task N"이라고 적은 내용
- 어떤 task도 정의하지 않는 interface
- 관찰 가능한 예상 결과가 없는 검증 단계

## 자체 리뷰

handoff 전에 다음을 수행한다.

1. 승인된 모든 요구사항을 task에 연결한다.
2. 의사코드가 구현 세부사항과 검증 선택보다 먼저 있고, 필요한 입력, 결과, 순서, 상태, 분기,
   반복, 오류, 경계, 책임과 가정을 설명하는지 확인한다.
3. 모든 task가 하나 이상의 flow ID에서 추적되고, 모든 flow가 파일, task, dependency와 검증에
   연결되는지 확인한다.
4. task 전반의 모든 경로, interface 이름, type과 정확한 값을 확인한다.
5. placeholder와 추측성 작업을 제거한다.
6. 각 task의 검증이 의사코드 작성 후 선택됐고 변경 유형과 일치하며 선택 이유가 있는지 확인한다.
7. 어떤 task도 현재 권한을 넘는 commit, push, PR, merge 또는 배포를 수행하지 않는지 확인한다.
8. 문서 영향이 기존 project 문서와 일치하는지 확인한다.

plan을 제시하기 전에 문제를 그 자리에서 수정한다.

## 구현 중 계획과 달라질 때

다음처럼 plan의 관찰 가능한 흐름이나 책임을 바꾸는 차이는 material deviation이다.

- 입력, 결과, 상태 변화, 분기, 반복, 오류 또는 경계 조건 변경
- interface나 기존 코드와 새 코드의 책임 경계 변경
- 파일·task dependency, 범위, 위험 또는 검증 전략 변경

local helper 이름, 동등한 표현 또는 흐름을 바꾸지 않는 작은 배치는 material deviation이 아니다.
material deviation이 필요하면 해당 task를 계속 구현하지 않고 차이와 이유를 설명한다.

먼저 변경이 승인된 요구사항·설계·관찰 가능한 계약을 바꾸는지 판정한다. 입력, 기대 결과, 외부에
보이는 상태·오류, interface 또는 책임 경계를 승인 내용과 다르게 만드는 변경이면
`engineering:brainstorming`으로 돌아가 변경안을 제시하고 사용자의 명시적인 재승인을 기다린다.
plan-readiness gate는 설계 승인이나 재승인을 대신하지 않는다.

승인된 설계 안의 변경이거나 필요한 재승인을 받은 뒤에는 `Behavioral Flow Pseudocode`를 먼저
갱신하고, 그 다음 flow mapping, task와 검증을 새 흐름에 맞춘다. 새 plan 리비전의 영향을 받는
모든 task를 찾는다. 이미 완료한 task도 이전 완료·검증·리뷰 근거가 새 흐름을 다루지 않으면
`reopened`로 표시하고 다시 구현·검증·리뷰한다. 변경된 plan 리비전에 자체 리뷰와
plan-readiness gate를 다시 적용한 뒤 가장 이른 미완료 또는 reopened task부터 실행을 재개한다.

## Plan 준비 상태 게이트

공통 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽고 실행
handoff 전에 정확한 plan 리비전에 게이트를 적용한다.

1. 위의 자체 리뷰 검사를 필수 결정론적 검사로 취급하고 근거를 기록한다.
2. 여러 component에 걸치거나 오래 걸리거나 위험도가 높은 plan, 또는 독립 리뷰가 구현 위험을 실질적으로 줄이는 경우 [plan-document-reviewer-prompt.md](plan-document-reviewer-prompt.md)로 reviewer를 위임한다. 의도적으로 제외한 선택적 리뷰는 `not_applicable`이고, 필수 reviewer를 사용할 수 없으면 `blocked` 또는 `not_run`이다.
3. 리뷰 시도는 최대 3회로 제한한다(초기 리뷰와 수정 후 리뷰 2회). 재시도할 때마다 영향을 받은 task, 요구사항 근거, interface 정의 또는 evaluator context가 달라져야 한다.
4. task 세부사항에 대한 finding은 영향을 받은 plan task로 돌려보낸다. 빠졌거나 모순된 요구사항은 `engineering:brainstorming`과 논쟁 중인 설계 결정으로 돌려보낸다.
5. 현재 plan 리비전이 `passed`이거나 사람이 `accepted_risk`를 명시적으로 기록한 경우에만 handoff한다. 시도 횟수 상한에 도달했다는 이유로 미해결 필수 finding을 pass로 바꾸지 않는다.

게이트의 artifact, 리비전, 근거, finding, 상태, 반환 대상, 시도 횟수와 decision owner를 plan 또는 handoff 메시지에 기록한다. plan 준비 상태는 여전히 Git 또는 외부 작업 권한을 부여하지 않는다.

## 실행 handoff

plan의 위치와 commit 권한 상태를 보고한다. 적용 가능한 실행 방법만 제시한다.

- **직접 실행:** `engineering:executing-plans`를 사용한다. 구현하고 검증한 뒤 승인되지 않은 commit 전에 `diff`를 보고한다.
- **Subagent 기반 실행:** 파일 기반 plan이 있고, subagent를 사용할 수 있고, task commit이 명시적으로 승인된 경우에만 `engineering:subagent-driven-development`를 사용한다.

실행 mode 선택이 추가 Git 또는 외부 작업 권한을 부여한다고 암시하지 않는다.
