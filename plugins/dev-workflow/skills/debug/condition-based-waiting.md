# 조건에 따른 대기

비동기 완료를 일정 시간 뒤로 추정하는 테스트는 느린 기기·병렬 실행·CI에서 불안정해질 수
있다. 필요한 이벤트나 상태가 관찰될 때까지 기다리고, 실패를 종료할 제한 시간을 둔다.
실제 debounce·throttle·주기 동작을 검사할 때에는 해당 시간 계약에 맞는 대기를 사용한다.

## 적용 예시

```typescript
// ❌ BEFORE: Guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ AFTER: Waiting for condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

| 기다릴 결과 | 조건 예시 |
| --- | --- |
| 이벤트 | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| 상태 | `waitFor(() => machine.state === 'ready')` |
| 개수 | `waitFor(() => items.length >= 5)` |
| 파일 | `waitFor(() => fs.existsSync(path))` |
| 복합 조건 | `waitFor(() => obj.ready && obj.value > 10)` |

## 반복 확인 도우미

기존 프레임워크의 대기 기능이 있으면 우선 사용한다. 아래는 값이 참으로 평가될 때 반환하는
단순 예시다. 확인 간격과 제한 시간은 실제 계약·환경에 맞게 정하며 루프 안에서 최신 상태를 읽는다.

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
  }
}
```

반환값 `0`·빈 문자열·`false`가 유효한 결과인 계약에는 위 예시의 참/거짓 판정을 그대로
사용하지 않는다. 별도 완료 조건을 표현한다. 실제 세션에서 추출한 `waitForEvent`,
`waitForEventCount`, `waitForEventMatch` 구현은
[condition-based-waiting-example.ts](condition-based-waiting-example.ts)에 있다.

## 시간 자체를 검사할 때

먼저 시작 조건을 기다린 뒤 알려진 주기·간격에 맞춰 관찰한다. 대기 시간의 근거를 주석으로 남긴다.

```typescript
// Tool ticks every 100ms - need 2 ticks to verify partial output
await waitForEvent(manager, 'TOOL_STARTED'); // First: wait for condition
await new Promise(r => setTimeout(r, 200));   // Then: wait for timed behavior
// 200ms = 2 ticks at 100ms intervals - documented and justified
```

## 과거 기록

원 자료의 2025-10-03 세션 기록은 3개 파일의 불안정한 테스트 15개 수정, 통과율 60% → 100%,
실행 시간 40% 감소를 보고했다. 원 결론은 “No more race conditions”였다. 이 수치는 해당
기록의 결과이며 현재 도우미나 다른 환경의 성능·경쟁 상태 부재를 입증하지 않는다.
