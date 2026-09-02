---
name: writing-plans
description: 여러 단계의 구현 task에 대해 승인된 설계나 요구사항이 있고 코드를 수정하기 전일 때 사용한다
---

# writing-plans: 계획 작성

## 개요

codebase를 거의 모르는 엔지니어도 실행할 수 있는 구현 계획을 작성한다. 정확한 파일, interface, 명령어, 예상 결과, 문서 영향과 각 변경에 적합한 검증을 명시한다. 계획은 독립적으로 이해할 수 있고 초점이 분명하며 추측성 작업을 포함하지 않아야 한다.

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

## 범위와 파일 구조

요구사항이 독립적으로 구현하고 검증할 수 없는 여러 subsystem을 포함한다면 plan을 분리하자고 제안한다. task를 정의하기 전에 생성하거나 수정할 정확한 파일과 각 파일의 책임을 연결한다.

- 기존 project pattern을 따른다.
- 각 단위의 초점을 유지하고 interface를 명시한다.
- 설정, configuration, 문서와 migration 작업은 해당 작업을 필요로 하는 산출물의 task에 포함한다.
- reviewer가 한 부분은 승인하고 다른 부분은 거부할 수 있는 의미 있는 경계에서만 task를 나눈다.
- 관련 없는 refactoring을 포함하지 않는다.

## 검증 선택

모든 변경에 하나의 절차를 적용하지 말고 task마다 검증 방법을 선택한다.

| 변경 | Plan |
| --- | --- |
| 새 코드 동작 또는 코드 동작 변경 | `engineering:test-driven-development`를 사용하고 RED, GREEN, 회귀 명령을 포함한다. |
| 버그 수정 | 실패하는 테스트로 재현하고 수정한 뒤 회귀 테스트를 유지한다. |
| 동작을 바꿀 수 있는 refactoring | refactoring 전에 테스트로 영향받는 동작을 보호한다. |
| 문서 | link, 경로, 예시와 관련 문서 사이의 일관성을 확인한다. |
| 스킬 지침 | frontmatter와 경로를 검증하고, 위험에 필요할 때에만 현실적인 동작 평가를 추가한다. |
| Manifest 또는 metadata | syntax를 parse하고 참조 경로를 검증하며, 사용할 수 있으면 native loader를 사용한다. |
| 단순 configuration | 변경된 configuration을 소비하는 가장 작은 명령을 실행한다. |

정적 text, metadata 또는 구현을 그대로 반복하는 테스트를 추가하지 않는다. TDD의 test-first cycle은 task가 production 동작을 바꿀 때 적용한다.

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

```markdown
# [Feature Name] Implementation Plan

**Goal:** [one sentence]

**Approach:** [two or three sentences]

**Requirements source:** [approved document, issue, ticket, or user-approved conversation design]

**Documentation impact:** [none, update path, create approved path, or supersede decision]

**Commit authorization:** [granted for this plan | not granted]

## Global Constraints

[Exact project-wide constraints that every task must preserve]
```

영속 요구사항 문서가 없다면 원래 대화를 읽을 수 없는 executor도 이해할 만큼 승인된 맥락을 plan에 포함한다.

## Task 구조

파일 기반 plan에는 실행 중 진행 상태를 추적할 수 있도록 checkbox 단계를 사용한다.

````markdown
### Task N: [Deliverable]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123`
- Verify: `tests/exact/path/to/test.py` or the applicable validation target

**Interfaces:**
- Consumes: [exact earlier interface or input]
- Produces: [exact interface later tasks rely on]

**Verification:** [TDD, regression test, native loader, syntax/path check, or other proportionate method]

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
2. task 전반의 모든 경로, interface 이름, type과 정확한 값을 확인한다.
3. placeholder와 추측성 작업을 제거한다.
4. 각 task의 검증이 변경 유형과 일치하는지 확인한다.
5. 어떤 task도 현재 권한을 넘는 commit, push, PR, merge 또는 배포를 수행하지 않는지 확인한다.
6. 문서 영향이 기존 project 문서와 일치하는지 확인한다.

plan을 제시하기 전에 문제를 그 자리에서 수정한다.

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
