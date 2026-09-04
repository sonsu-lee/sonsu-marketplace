---
name: verification-before-completion
description: 작업이 완료·수정됐거나 검사를 통과했다고 주장하기 직전과 commit 또는 PR 생성 전에 사용한다. 성공을 주장하기 전에 검증 명령을 실행하고 출력을 확인해야 하며, 항상 주장보다 근거가 먼저다
---

# verification-before-completion: 완료 전 검증

## 개요

**핵심 원칙:** 항상 주장보다 근거가 먼저다.

**이 규칙의 문구를 어기는 것은 규칙의 취지를 어기는 것이다.**

공통 [품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽고 적용한다.
이 스킬은 최종 근거 게이트를 제공할 뿐 Git 또는 외부 작업 권한을 부여하지 않는다.

## 절대 규칙

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

이번 메시지에서 검증 명령을 실행하지 않았다면 통과했다고 주장할 수 없다.

## 게이트 절차

```
BEFORE claiming any status or expressing satisfaction:

1. SCOPE: Identify the exact artifact and revision the claim covers
2. IDENTIFY: What command or review proves this claim?
3. RUN: Execute the FULL check (fresh, complete)
4. READ: Full output, check exit code, count failures
5. VERIFY: Does output confirm the claim for this revision?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
6. RECORD: Preserve the gate status, evidence, findings, and return target
7. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## 게이트 결과

- `passed`가 되려면 현재 리비전에서 모든 필수 검사가 통과 조건을 충족해야 한다.
- `failed`이면 실패한 입력을 바꿀 수 있는 가장 가까운 구현·계획·설계 소유 단계로 돌아간다.
- `blocked`, `inconclusive`와 필수 `not_run`은 완료 주장을 뒷받침하지 못한다.
- `accepted_risk`에는 정확한 리비전에 대한 사람의 명시적인 결정이 필요하다. 미해결 위험을 보고하며, 테스트나 게이트가 통과했다고 바꿔 말하지 않는다.
- 검사에서 결과 리비전까지 다뤘음이 명백하지 않다면 artifact 변경으로 이전 근거는 오래된 것이 된다.
- plan-backed 작업은 결정론적 검증과 일반 최종 리뷰만으로 완료할 수 없다. 같은 전체 변경
  리비전에 대한 fresh-context red-team gate가 `survives_challenge`여야 한다. reviewer를 사용할
  수 없거나 판정이 `invalidated`, `inconclusive`, `blocked`, 필수 `not_run`이면 완료 주장을
  뒷받침하지 못한다. 사람이 정확한 리비전과 위험을 명시적으로 수용한 `accepted_risk`는 통과와
  구분해 보고한다.

## 자주 하는 잘못된 주장

| 주장 | 필요한 근거 | 충분하지 않은 근거 |
|-------|----------|----------------|
| 테스트 통과 | 테스트 명령 출력: 실패 0개 | 이전 실행, "should pass" |
| Linter 오류 없음 | Linter 출력: 오류 0개 | 일부 검사, 외삽 |
| Build 성공 | Build 명령: exit 0 | Linter 통과, 문제가 없어 보이는 로그 |
| 버그 수정 | 원래 증상을 재현하는 테스트 통과 | 코드 변경, 수정됐다는 가정 |
| 회귀 테스트 동작 | Red-green cycle 검증 | 테스트 한 번 통과 |
| 에이전트 완료 | VCS `diff`에서 변경 확인 | 에이전트의 "success" 보고 |
| 요구사항 충족 | 줄 단위 checklist | 테스트 통과 |
| plan-backed 완료 | 결정론적 검증 + 일반 최종 리뷰 + fresh red-team `survives_challenge` | 일반 리뷰 승인만 있음 |

## 위험 신호 - 중단

- "should", "probably", "seems to" 사용
- 검증 전에 만족을 표현함("Great!", "Perfect!", "Done!" 등)
- 검증 없이 commit/push/PR을 하려 함
- 에이전트의 성공 보고를 그대로 신뢰함
- 일부 검증에 의존함
- "just this once"라고 생각함
- 피곤해서 작업을 끝내고 싶어 함
- **검증을 실행하지 않고 성공을 암시하는 모든 표현**

## 합리화 방지

| 변명 | 실제 |
|--------|---------|
| "Should work now" | 검증을 실행한다. |
| "I'm confident" | 확신은 근거가 아니다. |
| "Just this once" | 예외는 없다. |
| "Linter passed" | Linter는 compiler가 아니다. |
| "Agent said success" | 독립적으로 검증한다. |
| "I'm tired" | 피로는 변명이 아니다. |
| "Partial check is enough" | 일부 검사는 전체를 증명하지 못한다. |
| "Different words so rule doesn't apply" | 문구보다 취지가 우선한다. |

## 핵심 pattern

**테스트:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**회귀 테스트(TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**빌드:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**요구사항:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**에이전트 위임:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## 적용 시점

**항상 다음 작업 전에 적용한다.**
- 성공 또는 완료를 뜻하는 모든 형태의 주장
- 모든 만족 표현
- 작업 상태에 대한 모든 긍정적인 진술
- commit, PR 생성, task 완료
- 다음 task로 이동
- 에이전트에게 위임

**다음 표현에도 규칙이 적용된다.**
- 정확히 일치하는 문구
- 바꿔 쓴 문구와 동의어
- 성공을 암시하는 표현
- 완료 또는 정확성을 나타내는 모든 의사소통
