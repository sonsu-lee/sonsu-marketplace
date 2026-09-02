---
name: receiving-code-review
description: 코드 리뷰 피드백을 받고 제안을 구현하기 전에 사용하며, 특히 피드백이 불명확하거나 기술적으로 의심스러울 때 적용한다. 보여 주기식 동의나 무조건적인 구현이 아니라 기술적 엄밀함과 검증을 요구한다
---

# receiving-code-review: 코드 리뷰 수용

## 개요

코드 리뷰에는 감정적인 연기가 아니라 기술적인 평가가 필요하다.

**핵심 원칙:** 구현하기 전에 검증한다. 가정하기 전에 질문한다. 사회적 편안함보다 기술적 정확성이 우선이다.

피드백이 Engineering 품질 게이트에 속하면 공통
[품질 게이트 계약](../using-engineering-skills/references/quality-gates.md)을 읽는다.
나중에 범위를 제한한 재리뷰에서 정확히 해당 finding을 해결했는지 판단할 수 있도록 원래 artifact 리비전과 finding 식별자를 유지한다.

## 대응 pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. ROUTE: Send a valid finding to the nearest implementation, plan, or design owner
7. IMPLEMENT: One item at a time, test each
8. RE-REVIEW: Verify the changed revision with focused evidence
```

## 금지하는 응답

**절대 하지 않는다.**
- "You're absolutely right!" (명시적인 지침 파일 위반)
- "Great point!" / "Excellent feedback!" (과장된 반응)
- "Let me implement that now" (검증 전)

**대신 다음과 같이 대응한다.**
- 기술 요구사항을 다시 설명한다.
- 명확화 질문을 한다.
- 틀렸다면 기술적 근거를 들어 반박한다.
- 말보다 행동으로 바로 작업을 시작한다.

## 불명확한 피드백 처리

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**예시:**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## 출처별 처리

### 사용자에게 받은 피드백
- **신뢰한다.** 이해한 뒤 구현한다.
- 범위가 불명확하면 **여전히 질문한다.**
- **보여 주기식으로 동의하지 않는다.**
- **바로 행동하거나** 기술적으로 이해한 내용을 확인한다.

### 외부 reviewer에게 받은 피드백
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**사용자의 규칙:** "External feedback - be skeptical, but check carefully"

## "Professional" 기능의 YAGNI 확인

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**사용자의 규칙:** "You and reviewer both report to me. If we don't need this feature, don't add it."

## 구현 순서

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## 반박해야 할 때

다음 상황에서는 반박한다.
- 제안이 기존 기능을 깨뜨린다.
- reviewer에게 전체 context가 없다.
- 사용하지 않는 기능을 추가해 YAGNI를 위반한다.
- 현재 stack에서 기술적으로 틀렸다.
- legacy 또는 compatibility 사유가 있다.
- 사용자의 architecture 결정과 충돌한다.

**반박 방법:**
- 방어적인 태도가 아니라 기술적 근거를 사용한다.
- 구체적인 질문을 한다.
- 동작하는 테스트와 코드를 참조한다.
- architecture 문제라면 사용자를 참여시킨다.

**공개적으로 반박하기 불편하다면:** 그 불편함을 밝힌 뒤 발견한 문제를 사용자에게 설명한다. 사용자는 솔직한 설명을 이해할 것이다.

## 올바른 피드백 확인

피드백이 올바를 때:
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**감사를 표현하지 않는 이유:** 행동으로 보여 준다. 수정하면 코드 자체가 피드백을 반영했음을 보여 준다.

**"Thanks"라고 쓰려는 자신을 발견했다면:** 삭제하고 대신 수정 내용을 말한다.

## 잘못된 반박을 바로잡기

반박했지만 자신이 틀렸다면 다음처럼 대응한다.
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

수정된 사실을 담담하게 밝히고 다음으로 넘어간다.

## 자주 하는 실수

| 실수 | 수정 방법 |
|---------|-----|
| 보여 주기식 동의 | 요구사항을 말하거나 바로 행동한다. |
| 무조건적인 구현 | 먼저 codebase와 대조해 검증한다. |
| 테스트 없이 일괄 처리 | 한 번에 하나씩 처리하고 각각 테스트한다. |
| reviewer가 옳다고 가정 | 기존 동작을 깨뜨리는지 확인한다. |
| 반박 회피 | 편안함보다 기술적 정확성이 우선이다. |
| 일부만 구현 | 먼저 모든 항목을 명확히 한다. |
| 검증할 수 없는데 진행 | 제한을 밝히고 방향을 질문한다. |

## 실제 예시

**보여 주기식 동의(나쁜 예):**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**기술적 검증(좋은 예):**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI(좋은 예):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**불명확한 항목(좋은 예):**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub thread 답글

GitHub의 inline review comment에 답할 때에는 최상위 PR comment가 아니라 해당 comment thread(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`)에 답한다.
