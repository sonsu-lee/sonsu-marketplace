---
name: systematic-debugging
description: 버그, 테스트 실패 또는 예상하지 못한 동작을 만났을 때 수정안을 제안하기 전에 사용합니다
---

# systematic-debugging: 체계적인 디버깅

## 개요

**핵심 원칙:** 수정하기 전에 항상 근본 원인을 찾습니다. 증상만 고치는 것은 실패입니다.

**이 절차의 문구를 어기는 것은 디버깅의 취지를 어기는 것입니다.**

## 절대 원칙

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

1단계를 완료하지 않았다면 수정안을 제안할 수 없습니다.

## 사용 시점

모든 기술 문제에 사용합니다.
- 테스트 실패
- 프로덕션 버그
- 예상하지 못한 동작
- 성능 문제
- build 실패
- integration 문제

**특히 다음 상황에서 사용합니다.**
- 시간 압박을 받을 때(긴급 상황에서는 추측하고 싶어집니다)
- "Just one quick fix"가 분명해 보일 때
- 이미 여러 수정안을 시도했을 때
- 이전 수정안이 작동하지 않았을 때
- 문제를 완전히 이해하지 못했을 때

**다음 상황에서도 건너뛰지 않습니다.**
- 문제가 단순해 보일 때(단순한 버그에도 근본 원인이 있습니다)
- 서두르고 있을 때(서두르면 반드시 재작업이 생깁니다)
- manager가 즉시 수정하기를 원할 때(체계적인 접근이 무작정 시도하는 것보다 빠릅니다)

## 네 단계

다음 단계로 넘어가기 전에 각 단계를 반드시 완료해야 합니다.

### 1단계: 근본 원인 조사

**어떤 수정이든 시도하기 전에 다음을 수행합니다.**

1. **오류 메시지를 주의 깊게 읽기**
   - error나 warning을 건너뛰지 않습니다
   - 정확한 해결책이 들어 있는 경우가 많습니다
   - stack trace를 끝까지 읽습니다
   - line number, file path, error code를 기록합니다

2. **일관되게 재현하기**
   - 안정적으로 발생시킬 수 있습니까?
   - 정확한 절차는 무엇입니까?
   - 매번 발생합니까?
   - 재현할 수 없다면 → 추측하지 말고 data를 더 수집합니다

3. **최근 변경 확인하기**
   - 원인이 될 만한 무엇이 바뀌었습니까?
   - Git diff와 최근 commit
   - 새로운 dependency와 config 변경
   - 환경 차이

4. **여러 component로 구성된 system에서 근거 수집하기**

   **system에 여러 component가 있을 때(CI → build → signing, API → service → database):**

   **수정안을 제안하기 전에 진단 instrumentation을 추가합니다.**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **예시(multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **이로써 알 수 있는 것:** 어느 layer가 실패하는지(secrets → workflow ✓, workflow → build ✗)

5. **data flow 추적하기**

   **error가 call stack 깊은 곳에서 발생할 때:**

   완전한 역방향 추적 기법은 이 directory의 `root-cause-tracing.md`를 참고합니다.

   **빠른 방법:**
   - 잘못된 값은 어디서 시작됩니까?
   - 무엇이 이 코드를 잘못된 값으로 호출했습니까?
   - source를 찾을 때까지 위로 계속 추적합니다
   - 증상이 아니라 source에서 수정합니다

### 2단계: pattern 분석

**수정하기 전에 pattern을 찾습니다.**

1. **작동하는 예시 찾기**
   - 같은 codebase에서 비슷하게 작동하는 코드를 찾습니다
   - 망가진 부분과 비슷하면서 작동하는 것은 무엇입니까?

2. **참고 구현과 비교하기**
   - pattern을 구현한다면 reference implementation을 끝까지 읽습니다
   - 훑어보지 말고 모든 줄을 읽습니다
   - 적용하기 전에 pattern을 완전히 이해합니다

3. **차이 식별하기**
   - 작동하는 부분과 망가진 부분은 무엇이 다릅니까?
   - 아무리 작아도 모든 차이를 나열합니다
   - "that can't matter"라고 가정하지 않습니다

4. **dependency 이해하기**
   - 어떤 다른 component가 필요합니까?
   - 어떤 setting, config, environment가 필요합니까?
   - 어떤 가정을 합니까?

### 3단계: 가설과 테스트

**과학적 방법:**

1. **하나의 가설 세우기**
   - "I think X is the root cause because Y"처럼 명확하게 서술합니다
   - 기록합니다
   - 모호하지 않게 구체적으로 작성합니다

2. **최소한으로 테스트하기**
   - 가설을 테스트할 수 있는 가장 작은 변경을 만듭니다
   - 한 번에 변수 하나만 바꿉니다
   - 여러 문제를 한꺼번에 수정하지 않습니다

3. **계속하기 전에 검증하기**
   - 작동했습니까? 예 → 4단계
   - 작동하지 않았습니까? 새로운 가설을 세웁니다
   - 기존 수정 위에 다른 수정을 덧붙이지 않습니다

4. **모를 때**
   - "I don't understand X"라고 말합니다
   - 아는 척하지 않습니다
   - 도움을 요청합니다
   - 더 조사합니다

### 4단계: 구현

**증상이 아니라 근본 원인을 수정합니다.**

1. **수정 전 실패 재현 만들기**
   - 가능한 가장 단순한 재현
   - 가능하면 자동화 테스트
   - framework가 없다면 일회성 test script
   - 수정 전에 반드시 준비함
   - 재현 가능한 동작 결함에 TDD가 실질적인 회귀 신호를 주면 `engineering:test-driven-development`를 사용합니다
   - TDD가 적합하지 않다면 이유를 기록하고 가능한 가장 강한 재현·검증 절차를 사용합니다

2. **하나의 수정 구현하기**
   - 식별한 근본 원인을 해결합니다
   - 한 번에 하나만 변경합니다
   - "while I'm here" 식의 개선을 하지 않습니다
   - 리팩터링을 묶어서 수행하지 않습니다

3. **수정 검증하기**
   - 수정 전 실패 재현이 이제 통과합니까?
   - 관련 회귀 검사나 다른 테스트가 망가지지 않았습니까?
   - 문제가 실제로 해결되었습니까?
   - 성공을 주장하기 전에 `engineering:verification-before-completion` 스킬을 사용합니다

4. **수정안이 작동하지 않을 때**
   - 중단합니다
   - 시도한 수정안의 수를 셉니다
   - 3개 미만이면 1단계로 돌아가 새로운 정보로 다시 분석합니다
   - **3개 이상이면 중단하고 architecture를 재검토합니다(아래 5번)**
   - architecture를 논의하지 않고 네 번째 수정안을 시도하지 않습니다

5. **수정안이 3개 이상 실패했을 때: architecture 재검토**

   **architecture 문제를 나타내는 pattern:**
   - 수정할 때마다 다른 곳에서 새로운 shared state, coupling 또는 문제가 드러남
   - 수정안을 구현하려면 "massive refactoring"이 필요함
   - 수정할 때마다 다른 곳에 새로운 증상이 생김

   **중단하고 근본을 재검토합니다.**
   - 이 pattern은 근본적으로 타당합니까?
   - "sticking with it through sheer inertia" 상태입니까?
   - 증상을 계속 수정하는 대신 architecture를 리팩터링해야 합니까?

   **수정을 더 시도하기 전에 사람 협업자와 논의합니다**

   이는 가설의 실패가 아니라 잘못된 architecture입니다.

## 위험 신호 - 중단하고 절차 따르기

다음과 같이 생각하고 있다면 주의합니다.
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- data flow를 추적하기 전에 해결책을 제안함
- **"One more fix attempt" (이미 2회 이상 시도했을 때)**
- **수정할 때마다 다른 곳에서 새로운 문제가 드러남**

**이 중 하나라도 해당하면 중단하고 1단계로 돌아갑니다.**

**수정안이 3개 이상 실패했다면:** architecture를 재검토합니다(4단계의 5번 참고)

## 사람 협업자가 보내는 잘못된 접근의 신호

**다음과 같은 방향 수정에 주의합니다.**
- "Is that not happening?" - 검증하지 않고 가정했습니다
- "Will it show us...?" - 근거 수집을 추가했어야 합니다
- "Stop guessing" - 이해하지 못한 채 수정안을 제안하고 있습니다
- "Ultra-think this" - 증상뿐 아니라 근본을 재검토해야 합니다
- "We're stuck?"(불만) - 현재 접근 방식이 작동하지 않습니다

**이런 신호가 보이면:** 중단하고 1단계로 돌아갑니다.

## 흔한 합리화

| 핑계 | 실제 |
|--------|---------|
| "Issue is simple, don't need process" | 단순한 문제에도 근본 원인이 있습니다. 단순한 버그에서는 이 절차도 빠릅니다. |
| "Emergency, no time for process" | 체계적인 디버깅이 guess-and-check를 반복하는 것보다 빠릅니다. |
| "Just try this first, then investigate" | 첫 수정이 pattern을 만듭니다. 처음부터 올바르게 수행합니다. |
| "I'll write test after confirming fix works" | TDD를 선택했다면 실패 테스트가 먼저다. TDD를 선택하지 않았더라도 수정 전에 재현과 검증 방법을 준비한다. |
| "Multiple fixes at once saves time" | 무엇이 작동했는지 분리할 수 없고 새로운 버그가 생깁니다. |
| "Reference too long, I'll adapt the pattern" | 불완전한 이해는 버그를 보장합니다. 끝까지 읽습니다. |
| "I see the problem, let me fix it" | 증상을 보는 것과 근본 원인을 이해하는 것은 다릅니다. |
| "One more fix attempt"(2개 이상 실패한 뒤) | 3개 이상 실패하면 architecture 문제입니다. 다시 수정하지 말고 pattern을 재검토합니다. |

## 빠른 참고

| 단계 | 핵심 활동 | 성공 기준 |
|-------|---------------|------------------|
| **1. 근본 원인** | error 읽기, 재현, 변경 확인, 근거 수집 | 무엇이 왜 일어났는지 이해함 |
| **2. pattern** | 작동하는 예시 찾기와 비교 | 차이를 식별함 |
| **3. 가설** | 가설 수립과 최소 테스트 | 가설이 확인되거나 새 가설이 생김 |
| **4. 구현** | 선택한 재현·검증 준비, 수정, 검증 | 버그가 해결되고 수정 전 재현이 통과함 |

## 절차 결과가 "No Root Cause"일 때

체계적인 조사 결과 문제가 실제로 환경, timing 또는 외부 요인에 의존한다면 다음을 수행합니다.

1. 절차를 완료합니다
2. 조사한 내용을 문서화합니다
3. 적절한 처리(retry, timeout, error message)를 구현합니다
4. 이후 조사를 위한 monitoring/logging을 추가합니다

**그러나:** "no root cause" 사례의 95%는 불완전한 조사입니다.

## 보조 기법

다음 기법은 systematic debugging의 일부이며 이 directory에서 확인할 수 있습니다.

- **`root-cause-tracing.md`** - call stack을 역방향으로 추적해 버그의 최초 trigger를 찾습니다
- **`defense-in-depth.md`** - 근본 원인을 찾은 뒤 여러 layer에 validation을 추가합니다
- **`condition-based-waiting.md`** - 임의의 timeout을 condition polling으로 바꿉니다
