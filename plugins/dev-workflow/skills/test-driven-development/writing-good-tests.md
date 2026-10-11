# 좋은 테스트 작성하기

테스트를 작성·수정하거나 외부 경계 대체와 테스트용 도우미를 추가할 때 참고한다.
테스트마다 포착할 고장과 실제로 실행할 대상을 명확히 한다.

## 포착할 고장과 기대값

본문을 쓰기 전에 어떤 잘못된 프로덕션 변경이 테스트를 실패하게 해야 하는지 정한다.
잘못된 분기·인수, 누락된 상태 변경·부수 효과, 경계 사례와 계약 위반이 대상이다.
의도적인 내부 구조 변경에만 반응한다면 그 구조의 소비자가 관찰할 결과로 검사를 옮긴다.

기대값은 테스트 대상 코드와 독립적으로 도출한 리터럴이나 직접 확인한 입력 자료를 사용한다.

```typescript
// ❌ Mirror assertion: the same builder computes both sides — always true
const expected = buildSearchQuery({ tag: 'urgent' });
expect(buildSearchQuery({ tag: 'urgent' })).toBe(expected);

// ✅ Hand-derived literal
expect(buildSearchQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

정확한 문자열이나 상수가 외부 계약이면 그 값을 검사한다. 내부 결정이라면 해당 결정에
의존하는 동작을 검사한다. 예를 들어 재시도 상수 자체보다 실제 호출 횟수와 종료 결과를 확인한다.

스크립트·설정은 통제된 입력으로 실행해 출력·부수 효과·종료 코드를 확인한다. 경로·구문·생성
동기화처럼 정적 계약은 정적 검사로 확인한다. 에이전트 지침의 중요한 동작 변화에는
[write-skill](../write-skill/SKILL.md)에 따라 실제 소비 사례가 필요한지 판단한다.
사람이 읽는 산문이나 구현을 그대로 반복하는 테스트에는 새 실행 테스트를 만들지 않는다.

## 자신의 경계 계약을 검사한다

등록한 경로, 생성한 쿼리·요청과 실제 사용자 결과를 확인한다. 프레임워크 내부 동작을 다시
검증하기보다 자신의 연결과 가정을 검증한다. 외부 동작이 예상과 달랐던 경우에는 그 가정을
고정하는 작은 특성 테스트가 유용하다.

생성자·getter·단순 전달도 검증, 정규화, 기본값, 파생 결과 또는 부수 효과를 소유하면 검사할
가치가 있다. 그렇지 않으면 해당 요소를 소비한 뒤 처음 관찰할 수 있는 결과를 검사한다.

## 필요한 경계만 대체한다

테스트 대역(mock·fake·spy)을 추가하기 전에 실제 메서드의 부수 효과와 테스트의 의존 관계를
확인한다. 느린 처리, 외부 서비스 또는 재현하기 어려운 실패 경계를 대체하고 검사할 동작은
실제로 실행한다. 호출 인수·횟수·순서가 경계 계약이라면 spy 단언도 유효하다.

```typescript
// ✅ Real behavior
expect(screen.getByRole('navigation')).toBeInTheDocument();

// ❌ Mock existence
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
```

원 자료에 기록된 검토 질문은 다음과 같다.

> Are we testing the behavior of a mock?

```typescript
// ❌ The mock swallows the config write that duplicate detection reads
vi.mock('ToolCatalog', () => ({
  discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
}));

// ✅ Mock only the slow server startup; the config write stays real
vi.mock('MCPServerManager');
```

성공·실패·잘못된 응답은 서로 구분되는 입력 자료로 표현한다. 실제 경계에서 요구하는 필드와
구조를 유지하고, 의도적으로 빠뜨린 필드는 검사할 실패 조건으로 명시한다. 관련 없는 전체
응답을 복제할 필요는 없다.

테스트에서만 쓰는 정리는 테스트 도우미에 둔다. 실제 자원 수명주기를 소유하는 프로덕션
메서드는 제품 계약에 따라 유지한다. 대역 설정이 복잡해 동작을 가리면 실제 구성요소를 쓰는
통합 테스트가 더 명확한지 확인한다. 원 자료의 검토 질문은 다음과 같다.

> Do we need to be using a mock here?

## 검출력을 확인한다

TDD를 선택한 동작은 의도한 RED 실패와 GREEN 통과를 확인한다. 그 밖의 테스트는 위험에 맞춰
실제 결함 상태나 작은 변형으로 검출력을 확인한다. 잘못된 분기·인수, 누락된 부수 효과,
빈 반환과 해당 계약의 경계 입력을 생각해 보고, 중요한 고장을 놓치는 경우에만 보완한다.
모든 테스트에 별도 변이 도구 실행이나 전 범위 재검사를 강제하지 않는다.

구현·테스트 준비 오류와 실제 동작 실패를 구분하고, 필요한 테스트를 구현과 함께 제공한다.
