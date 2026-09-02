# Writing Good Tests: 좋은 테스트 작성하기

**이 참고 문서를 읽을 때:** 테스트를 작성하거나 변경할 때, mock을 추가할 때 또는
테스트용 cleanup/helper method를 추가할 때 읽습니다.

## 개요

테스트는 특정한 고장을 포착하기 위해 존재합니다. 다음 두 원칙이 이 문서의
모든 내용을 이끕니다.

```
1. Every test names the break it catches
2. Every test exercises the real thing
```

엄격한 TDD는 두 원칙을 자연스럽게 충족합니다. 먼저 작성한 테스트가 실제 코드를
대상으로 실패하는 모습을 확인했다면 그 테스트는 실패할 수 있음을 이미 증명한
것입니다. 실제 dependency가 느리거나 외부에 있을 때만 mock을 사용할 근거가 생깁니다.

## 원칙 1: 포착할 고장을 명시하기

테스트 본문을 작성하기 전에 다음 질문에 답합니다. **어떤 프로덕션 변경이 이 테스트를
실패하게 해야 하며, 그 변경은 버그입니까 아니면 의도적인 결정입니까?** 테스트는 잘못된
branch, 누락된 side effect, 잘못된 argument, boundary case 또는 깨진 contract를
포착할 때 존재 가치를 얻습니다.

**기대값을 독립적으로 도출합니다.** literal과 직접 확인한 fixture를 사용합니다.
literal `want` 값을 가진 table-driven test가 선호되는 형태입니다. 테스트 대상 코드나
그 helper로 계산한 기대값은 해당 코드가 무엇을 하든 통과합니다.

```typescript
// ❌ Mirror assertion: the same builder computes both sides — always true
const expected = buildSearchQuery({ tag: 'urgent' });
expect(buildSearchQuery({ tag: 'urgent' })).toBe(expected);

// ✅ Hand-derived literal
expect(buildSearchQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

**변경 감지기를 만들지 않습니다.** constant 값, 정확한 메시지 문구, private 구조처럼
의도적인 결정만 테스트를 실패하게 한다면, 그 테스트는 재설계 때는 울리고 버그는
놓칩니다. 결정 자체가 아니라 그 결정에 의존하는 동작을 테스트합니다.
`expect(MAX_RETRIES).toBe(5)`가 아니라 "a failing call is retried 5 times and the 6th attempt never happens."를 검증합니다.

**텍스트가 아니라 동작을 검증합니다.** script, skill 또는 config에 정확한 한 줄이
포함되어 있다고 assertion해도 source가 source라는 사실만 증명합니다. 통제된 입력으로
script를 실행하고 output, side effect 또는 exit code를 assertion합니다. 에이전트에게
지침을 제공하는 문서는 이를 소비하는 에이전트의 동작으로 테스트합니다
(`engineering:writing-skills`). 사람이 읽는 산문에는 테스트가 필요하지 않습니다.

**framework가 아니라 자신의 코드를 검증합니다.** 등록한 route, 내보내는 query, 생성하는
payload처럼 코드가 경계에서 제공하는 contract를 테스트합니다. Upstream 동작 원리는
해당 maintainer가 테스트할 영역입니다. 대표적으로 router가 등록된 handler를 호출하는지
assertion하는 것은 자신의 테스트가 아니라 framework의 테스트입니다. Upstream 동작이
실제로 예상 밖이었다면 가정을 명시한 좁은 characterization test 하나를 작성합니다.
같은 경계는 코드 내부에도 적용됩니다. constructor, getter, constant와 단순 forwarding은
검증, 정규화, 기본값 설정, 파생, 강제 또는 side effect를 수행할 때만 테스트할 가치가
있습니다. 그렇지 않다면 해당 요소에 의존하면서 소비자가 처음 관찰할 수 있는 결과를
assertion합니다.

### Gate function(판정 절차)

```
BEFORE writing the test body:
  Name the production change that would make this test fail.

  Cannot name one            → redesign around an observable behavior
  "The source text changed"  → run the artifact and assert its effects
  Only intentional decisions → change detector; test the behavior
                               that depends on the decision

  Confirm the expected value is derived without the code under test.
  IF it reuses the code's logic or helpers:
    Replace it with a literal or hand-checked fixture
```

## 원칙 2: 실제 대상을 실행하기

**mock 자체는 assertion 대상이 아닙니다.** mock assertion은 mock이 있으면 통과하고
없으면 실패하므로 component에 관해서는 아무것도 말해 주지 않습니다. 실제 component의
동작을 assertion합니다. mock을 확인하고 있다면 mock을 제거하거나 assertion을 삭제합니다.

```typescript
// ✅ Real behavior
expect(screen.getByRole('navigation')).toBeInTheDocument();

// ❌ Mock existence
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
```

**사람 협업자의 지적:** "Are we testing the behavior of a
mock?"

**올바른 수준에서 mock합니다.** 실제 method를 대체하기 전에 모든 side effect를
파악합니다. 느리거나 외부인 operation을 mock하고 테스트가 의존하는 부분은 실제로
유지합니다. 확실하지 않다면 먼저 실제 구현을 대상으로 테스트를 실행해 무엇이 실제로
일어나야 하는지 관찰합니다.

```typescript
// ❌ The mock swallows the config write that duplicate detection reads
vi.mock('ToolCatalog', () => ({
  discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
}));

// ✅ Mock only the slow server startup; the config write stays real
vi.mock('MCPServerManager');
```

**test double을 구체적으로 만듭니다.** argument, 호출 횟수 또는 순서가 contract의
일부라면 이를 assertion합니다. 무엇이든 허용하는 fake는 아무것도 검증하지 않습니다.
각 branch(success, error, malformed)에 자체 fixture나 spy를 제공해 잘못된 branch가
기대값을 충족하지 못하게 합니다.

**실제 data를 완전하게 반영합니다.** 테스트가 읽는 field만이 아니라 문서화된 모든 field를
포함해 실제 존재하는 complete structure를 mock합니다. downstream 코드가 누락된 field를
읽을 때 partial mock은 조용히 실패합니다. 테스트는 통과하지만 integration은 깨집니다.

**프로덕션 class에는 프로덕션 method만 둡니다.** 테스트에서만 필요한 cleanup은
프로덕션 class의 `destroy()`가 아니라 test utility에 둡니다. 이 method를 테스트에서만
호출하는지, 이 class가 해당 resource의 lifecycle을 소유하는지 질문합니다. 답이
적절하지 않다면 test utility로 옮깁니다.

**복잡한 mock보다 실제 component를 선호합니다.** mock setup이 테스트 logic보다 커지거나,
mock에 실제 component의 method가 빠지거나, mock 변경으로 테스트가 깨진다면 실제
component를 사용하는 integration test로 전환합니다. **사람 협업자의 질문:**
"Do we need to be using a mock here?"

### Gate function(판정 절차)

```
BEFORE adding a mock or test helper:
  List the real method's side effects; keep the ones the test
  depends on real — mock the slow/external level below them.

  Mock responses mirror the complete real structure.

  A method only tests call lives in test utilities, not production.

  About to assert on the mock itself?
    Unmock it or delete the assertion.
```

## 테스트는 구현과 함께 제공하기

실패 테스트, 최소 구현, 리팩터링으로 이어지는 TDD cycle이 "complete"의 의미입니다.
동작에 필요한 테스트만 구현과 함께 제공합니다. 사소한 코드와 사람이 읽는 산문에는
테스트가 필요하지 않으며, 절차를 충족하기 위해 작성한 테스트는 계속 유지보수 비용을
발생시킵니다.

## Mutation 검사

완료하기 전에 프로덕션 코드를 머릿속으로 변형해 봅니다. 현실적인 각 mutation에 대해
최소 하나의 테스트가 실패해야 합니다.

- 잘못된 constant 또는 argument
- 잘못된 branch handler
- 누락된 상태 변경 또는 side effect
- 비어 있거나 기본값인 return
- zero, empty, nil, unauthorized 또는 malformed input에 대한 검증 누락

어떤 테스트도 포착하지 못하는 mutation은 해당 동작이 보호받지 못하거나 테스트가
동어 반복임을 뜻합니다.

## 빠른 참고

| 상황 | 수행할 일 |
|-------------|-----|
| 테스트 작성 | 포착할 고장을 명시합니다. 의도적인 결정이 아니라 버그여야 합니다 |
| 기대값 생성 | 테스트 대상 코드가 아니라 직접 도출합니다 |
| script 또는 문서 테스트 | 실행하거나 소비자를 pressure test합니다. 텍스트를 grep하지 않습니다 |
| dependency 테스트 고려 | 문서화된 내부 동작이 아니라 자신의 경계 contract를 테스트합니다 |
| mock된 element assertion 고려 | 실제 component를 테스트하거나 mock을 제거합니다 |
| method mock 직전 | side effect를 파악하고 느리거나 외부인 수준을 mock합니다 |
| mock response 생성 | 실제 구조를 완전하게 반영합니다 |
| 테스트에서만 쓰는 cleanup 필요 | test utility에 둡니다 |
| mock setup이 커짐 | 실제 component를 사용하는 integration test로 전환합니다 |
| test file 완료 | mutation 검사를 실행합니다 |

## 위험 신호

- setup과 assertion이 같은 object를 공유해 항상 같아짐
- panic, crash 또는 누락된 selector를 통해서만 테스트가 실패할 수 있음
- 우발적인 고장에는 실패하지 않고 의도적인 변경마다 실패함
- 기대값이 loop, builder 또는 helper 뒤에 숨겨짐
- source text를 grep하거나 제거된 symbol이 계속 제거된 상태인지 assertion함
- framework만 남아도 테스트가 여전히 의미 있음
- side effect나 outcome을 확인하지 않고 coverage만을 위해 테스트가 존재함
- assertion이 `*-mock` test ID를 확인하거나 mock을 제거하면 실패함
- method가 test file에서만 호출됨
- mock setup이 테스트의 절반을 넘거나 mock이 필요한 이유를 설명할 수 없음
- "just to be safe"라는 이유로 mock함
