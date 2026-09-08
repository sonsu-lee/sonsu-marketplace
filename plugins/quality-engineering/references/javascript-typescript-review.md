# JavaScript·TypeScript 개인 리뷰 체크리스트

JS·TS 코드를 구현하거나 리뷰할 때 모든 규칙을 기계적으로 적용하지 않는다. 먼저 값의 출처와
도메인 계약을 확인하고, 실제로 도달 가능한 잘못된 상태와 독자가 반복해서 추론해야 하는 지식을
줄인다.

## 먼저 정할 원칙

```text
외부의 unknown
  -> 소유 경계에서 parse / validate / normalize
  -> transport DTO를 필요한 domain type으로 변환
  -> 내부에는 신뢰된 타입과 불변식을 전달
  -> leaf 함수는 자기 계약만 구현
```

- 외부 입력은 TypeScript 타입만으로 신뢰하지 않는다. 런타임 경계에서 한 번 확인한다.
- public API와 변경 가능한 값에는 의도한 계약을 annotation으로 고정하고, 지역 값은 추론을
  우선한다.
- object literal의 shape을 검사하면서 구체적인 key·literal 정보를 유지하려면 `satisfies`를
  검토한다.
- `null`, `undefined`, 빈 문자열, `0`, `false`가 같은 의미가 아니면 truthiness로 합치지 않는다.
- 내부에 반복되는 guard는 안전의 증거가 아니다. 경계가 빠졌거나 타입이 실제 계약보다 넓다는
  신호일 수 있다.

## 1. `null`, `undefined`와 값의 부재

### 의미를 먼저 하나로 정한다

프로젝트 안에서 다음 의미를 섞지 않는다.

- `undefined`: 값이 제공되지 않았거나 optional property가 존재하지 않음
- `null`: 제공자가 의도적으로 "값 없음"을 전달함
- `""`, `0`, `false`: 존재하는 유효 값

외부 API가 두 nullish 값을 모두 사용하더라도 내부 도메인에는 필요한 한 형태로 정규화한다.

```ts
type User = { nickname?: string };

function toUser(dto: { nickname: string | null }): User {
  return dto.nickname === null ? {} : { nickname: dto.nickname };
}
```

`nickname?: string`과 `nickname: string | undefined`도 같지 않다. 전자는 property 자체가 없을 수
있고, 후자는 property가 존재하되 값이 `undefined`일 수 있다. 이 구분이 중요하면
`exactOptionalPropertyTypes`를 켠다.

### `??`와 `||`를 구분한다

`||`는 `false`, `0`, `""`, `NaN`도 대체한다. nullish 값만 기본값으로 바꿀 때는 `??`를 쓴다.

```ts
const retryCount = input.retryCount ?? 3;
const displayName = input.displayName || "Anonymous"; // 빈 문자열도 금지할 때만
```

`filter(Boolean)`은 짧지만 `0`, `false`, `""`도 제거한다. nullish만 제거하려면 의도를 드러낸다.

```ts
const present = values.filter(
  (value): value is NonNullable<typeof value> => value != null,
);
```

여기서 `value != null`은 `null`과 `undefined`를 함께 검사하려는 의도적인 예외다. 그 외에는
`===`와 `!==`를 기본으로 한다.

### 호출과 직렬화의 차이를 확인한다

- 기본 parameter는 인자가 생략되거나 `undefined`일 때만 적용된다. `null`에는 적용되지 않는다.
- `JSON.stringify`는 object property의 `undefined`를 생략하지만 array의 `undefined`는 `null`로
  직렬화한다.
- `{ ...source, key: undefined }`는 `key`를 제거하지 않고 존재하는 property로 덮어쓴다.
- `obj?.value`는 `obj`만 nullish 검사한다. 얻은 값의 shape이나 이후 불변식을 검증하지 않는다.

```ts
function pageSize(value = 20) {
  return value;
}

pageSize(undefined); // 20
pageSize(null); // type이 허용한다면 null

JSON.stringify({ a: undefined }); // "{}"
JSON.stringify([undefined]); // "[null]"
```

### lookup의 "없음"과 저장된 `undefined`를 분리한다

`Map#get`과 index access 결과만 보면 key가 없는지, 값으로 `undefined`를 저장했는지 구분할 수
없다. 그 차이가 계약에 중요하면 존재 확인을 함께 쓴다.

```ts
if (!cache.has(key)) return { kind: "miss" } as const;
return { kind: "hit", value: cache.get(key) } as const;
```

plain object의 own property 여부는 `Object.hasOwn(object, key)`로 확인한다. `key in object`는
prototype chain까지 포함한다.

## 2. `satisfies` 사용 기준

### 무엇을 보장하는가

`expr satisfies T`는 compile time에 `expr`이 `T`에 할당 가능한지 검사한다. 결과 값은 `expr`
그 자체이며 runtime 검사 코드는 생기지 않는다. 일반적인 `: T` annotation처럼 결과를 무조건
`T`로 보이게 하기보다 object literal의 구체적인 key와 값 정보를 보존하는 데 유용하다.

```ts
type Route = {
  path: `/${string}`;
  auth: "public" | "user" | "admin";
};

const routes = {
  home: { path: "/", auth: "public" },
  settings: { path: "/settings", auth: "user" },
} satisfies Record<string, Route>;

routes.settings.path; // "/settings"에 대한 구체적인 정보 유지
```

고정 configuration처럼 key와 값 모두 literal이어야 하면 `as const satisfies`를 검토한다.

```ts
const transitions = {
  draft: ["submitted"],
  submitted: ["approved", "rejected"],
} as const satisfies Record<string, readonly string[]>;
```

### 좋은 사용처

- route, command, feature, event handler 같은 정적 registry
- key 누락·오타는 막되 key별 구체적인 값은 후속 추론에 남겨야 하는 object literal
- callback parameter를 target type으로 contextual typing하고 결과의 구체성은 유지할 때
- immutable configuration을 `as const`와 함께 검사할 때

### 사용하지 말아야 할 자리

- `fetch(...).json()`이나 `JSON.parse()` 결과의 런타임 검증
- public 함수의 반환 계약을 고정해야 하는 자리
- 나중에 더 넓은 값으로 변경할 mutable state
- 컴파일러 오류를 억누르기 위한 `as unknown as T`의 대체 문법

```ts
// 나쁨: 외부 값은 실제로 검사되지 않는다.
const user = (await response.json()) satisfies User;

// 좋음: 경계 parser가 runtime 사실을 확인한다.
const user = parseUser(await response.json());
```

### 추론이 기대와 달라지는 대표 사례

`satisfies`가 "좌변 추론에 전혀 영향을 주지 않는다"고 이해하면 안 된다. target type은 object
literal과 callback의 contextual typing에 참여할 수 있다.

#### 1) mutable 값이 literal로 너무 좁아질 수 있다

```ts
const state = { enabled: true } satisfies { enabled: boolean };
state.enabled = false; // compiler version과 문맥에 따라 literal true로 좁아져 오류 가능
```

변경 가능한 계약이라면 의도한 widening을 annotation으로 직접 고정한다.

```ts
const state: { enabled: boolean } = { enabled: true };
state.enabled = false;
```

#### 2) optional property가 결과 타입에 새로 생기지 않는다

```ts
type Config = { timeout?: number };

const config = {} satisfies Config;
config.timeout; // 오류: 추론된 {}에 timeout property가 생기지 않음
```

전체 optional surface가 후속 mutation·접근 계약이면 annotation을 쓴다.

```ts
const config: Config = {};
config.timeout = 1_000;
```

#### 3) `satisfies`가 optional spread를 안전하게 만들지는 않는다

`exactOptionalPropertyTypes`가 꺼진 코드에서 `{ key: undefined }`와 optional property가 섞이면
spread 결과가 실제 runtime shape보다 낙관적으로 보일 수 있다. `satisfies`를 더 붙이는 대신
compiler option을 켜고, property를 제거할 때는 명시적으로 제외한다.

```ts
const { key: _removed, ...withoutKey } = source;
```

### 회피 순서

추론이 목적과 맞지 않으면 다음 순서로 해결한다.

1. 이 값이 좁고 immutable해야 하는지, 넓고 mutable해야 하는지 먼저 결정한다.
2. 정적 literal registry라면 `satisfies`, 필요하면 `as const satisfies`를 사용한다.
3. mutable 값이나 public 계약이면 `: Type` annotation을 사용한다.
4. 외부 값이면 parser·schema validator·decoder로 runtime 검증한다.
5. TypeScript가 표현하지 못하는 확인된 불변식만 가장 좁은 위치에서 assertion으로 연결하고
   compiler regression test를 둔다.

double assertion, 넓은 `any`, 모든 소비자의 반복 guard로 추론 문제를 덮지 않는다.

## 3. API 경계와 type guard

### guard의 소유자를 정한다

외부 API response가 문서상 특정 shape이라는 사실과 현재 runtime 값이 실제 그 shape이라는 사실은
다르다.

- 제3자 API, version drift 가능성이 있는 API, `JSON.parse`, storage 복원: 경계에서 runtime
  validation을 수행한다.
- 같은 조직이 소유하며 schema에서 client type을 생성하는 API: adapter에서 transport type을
  받고 domain type으로 변환한다. 생성 타입만으로 runtime 정합성이 증명되는 것은 아니므로
  contract test, schema compatibility 또는 server validation 중 실제 보증을 확인한다.
- 생성된 공통 DTO가 특정 endpoint의 실제 계약보다 넓다면 endpoint adapter에서 한 번 좁힌 뒤
  더 좁은 domain type을 반환한다.

```ts
type PaidOrder = {
  id: string;
  paidAt: Date;
};

function parsePaidOrder(value: unknown): PaidOrder {
  if (typeof value !== "object" || value === null) {
    throw new ContractViolation("paid order endpoint returned an invalid order");
  }

  const dto = value as Record<string, unknown>;
  if (
    typeof dto.id !== "string" ||
    dto.status !== "paid" ||
    typeof dto.paidAt !== "string"
  ) {
    throw new ContractViolation("paid order endpoint returned an invalid order");
  }

  const paidAt = new Date(dto.paidAt);
  if (Number.isNaN(paidAt.getTime())) {
    throw new ContractViolation("paid order endpoint returned an invalid paidAt");
  }

  return { id: dto.id, paidAt };
}

function renderReceipt(order: PaidOrder) {
  return order.paidAt.toISOString(); // 내부 재검증 없음
}
```

도메인 계약상 불가능한 상태를 leaf에서 조용히 `null`이나 빈 UI로 바꾸면 API 계약 위반이 정상
분기로 숨는다. 복구 정책이 확인된 경우가 아니라면 경계 소유자가 오류를 분류하고 원인을 보존한다.

### type predicate는 compiler에게 하는 약속이다

`value is T`는 함수 본문을 보고 자동 검증되는 명제가 아니다. 검사한 runtime 사실이 `T`의 전체
계약을 증명해야 한다.

```ts
// 나쁨: id만 확인하고 User 전체를 약속한다.
function isUser(value: unknown): value is User {
  return typeof value === "object" && value !== null && "id" in value;
}
```

다음 중 하나를 선택한다.

- 작은 union이나 nullish 제거처럼 증명 범위가 작으면 정확한 predicate를 작성한다.
- object schema가 크면 parser/validator가 성공 값 또는 구조화된 오류를 반환하게 한다.
- 내부 값이면 호출자가 더 정확한 parameter type을 넘기게 하고 guard를 제거한다.

내부 재검증은 mutable state, 우회 가능한 경계, 서로 다른 실패 소유권이 실제로 있을 때만 둔다.

## 4. 비동기 코드에서 놓치기 쉬운 패턴

### `forEach(async ...)`를 기다림으로 착각하지 않는다

```ts
// 나쁨: callback promise를 기다리지 않는다.
items.forEach(async (item) => {
  await save(item);
});

// 순차 실행이 계약일 때
for (const item of items) {
  await save(item);
}

// 독립 병렬 실행이 계약일 때
await Promise.all(items.map((item) => save(item)));
```

`Promise.all`은 하나가 reject되면 반환 promise가 즉시 reject하지만 이미 시작한 작업을
취소하지 않는다. write가 섞이면 부분 성공, retry, idempotency와 cleanup을 함께 검토한다.

다음도 확인한다.

- 의도하지 않은 floating promise와 event handler의 rejection 소유자
- `catch` 후 원인 손실, 무조건 성공 반환, log-and-rethrow
- timeout이 실제 작업 취소인지 단순히 기다림만 중단하는지
- 반복 retry가 duplicate write를 만들 수 있는지

## 5. 코드가 더러워지는 신호

| 신호 | 먼저 물을 질문 | 기본 개선 방향 |
| --- | --- | --- |
| 같은 null/shape guard가 여러 함수에 반복됨 | trust boundary가 빠졌거나 타입이 너무 넓은가 | 경계에서 한 번 검증하고 좁은 타입 전달 |
| optional property 여러 개가 상태를 표현함 | 불가능한 조합이 생기는가 | 확인된 variant만 discriminated union으로 표현 |
| boolean parameter가 계속 늘어남 | 서로 다른 동작 모드나 정책을 숨기는가 | 의미 있는 variant·함수로 분리; 한 번 쓰는 wrapper는 피함 |
| 긴 optional chaining 뒤 기본값 | 어느 지점의 부재가 정상인지 알 수 있는가 | 정상적인 부재만 표현하고 계약 위반은 경계에서 처리 |
| `as`, `!`, `any`가 연쇄됨 | 타입이 실제 값보다 낙관적인가 | 경계 parser, 제어 흐름 narrowing, 정확한 annotation |
| nested ternary와 한 줄 표현식 | 독자가 evaluation order를 재구성해야 하는가 | 이름 있는 중간 값과 직접적인 분기 |
| DTO가 UI·domain 깊숙이 전달됨 | transport의 optional·legacy 상태가 누수되는가 | adapter에서 domain type으로 변환 |
| 한 caller를 감싼 generic/factory/interface | 현재 제거하는 중복이나 오류가 있는가 | inline하거나 직접 함수 사용 |
| 같은 domain rule이 여러 validator에 복제됨 | 규칙의 단일 소유자가 있는가 | 생성·변환 경계 한곳으로 모음 |
| 모든 오류를 `null`로 바꿈 | 정상적인 부재와 실패를 구분할 수 있는가 | Result, typed error 또는 소유 경계의 예외 정책 |

짧은 코드가 항상 깨끗한 코드는 아니다. 도메인 의미, 실패 소유권과 변경 이유가 더 직접적으로
보이는 쪽을 선택한다.

## 6. 자동화할 항목과 사람이 판단할 항목

### compiler와 lint로 고정

새 프로젝트의 기본 후보:

```json
{
  "compilerOptions": {
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "useUnknownInCatchVariables": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

기존 프로젝트에서는 오류 수를 줄이려고 assertion을 일괄 삽입하지 않는다. 경계와 모델을 먼저
고친 뒤 option별로 단계적으로 켠다. `noUncheckedIndexedAccess`가 과도한 guard를 유발한다면
index 기반 구조가 맞는지, key 집합을 더 정확히 표현할 수 있는지 먼저 본다.

type-aware ESLint에서는 현재 코드에 맞춰 다음 규칙을 검토한다.

- `@typescript-eslint/no-floating-promises`
- `@typescript-eslint/no-misused-promises`
- `@typescript-eslint/no-unnecessary-condition`
- `@typescript-eslint/switch-exhaustiveness-check`
- `@typescript-eslint/only-throw-error`
- `eqeqeq`와 의도적인 `== null` 예외

`strict-boolean-expressions`는 truthiness 혼동이 빈번한 코드에서 유용하지만 migration 비용이 크다.
경고를 없애기 위한 `Boolean(...)` 포장보다 도메인 의미를 드러내는 비교가 생기는지 확인한다.

### 사람이 리뷰

- `null`과 `undefined`가 실제로 다른 도메인 의미인지
- API의 runtime 보증과 client type 사이에 증거가 있는지
- guard가 도달 가능한 입력을 막는지, 이미 신뢰된 내부 값을 재검증하는지
- `satisfies`, annotation, parser 중 선택이 값의 수명과 변경 가능성에 맞는지
- fallback이 정상적인 부재를 처리하는지 계약 위반을 숨기는지
- 추상화가 현재 중복 지식·오류를 실제로 제거하는지
- async 실패 시 부분 성공과 재실행 결과가 무엇인지

## 7. 리뷰 출력 형식

규칙 이름만 나열하지 말고 다음 순서로 쓴다.

```text
[priority] 짧은 제목
- 위치: path:line
- 분류: correctness | boundary | inference | maintainability | failure-mode
- trigger: 어떤 입력·호출·상태에서 도달하는가
- 실제 영향: 현재 코드가 무엇을 잘못하거나 독자에게 어떤 계약을 중복 추론시키는가
- 수정: 가장 작은 경계·타입·제어 흐름 변경
- 예외: 현재 코드가 유지되어야 하는 확인된 이유가 있는가
- 자동화: compiler/lint/test로 재발을 막을 수 있는가
```

취향, 코드 줄 수, 가상의 미래 요구만으로 finding을 만들지 않는다. 실행 가능한 문제가 없으면
없다고 말하고, runtime 계약처럼 근거가 부족한 항목은 `inconclusive`로 구분한다.

## 빠른 체크리스트

- [ ] `strictNullChecks`를 포함한 `strict`가 켜져 있는가?
- [ ] optional property와 `| undefined`를 의도적으로 구분했는가?
- [ ] 유효한 `0`, `false`, `""`를 `||`나 truthiness가 지우지 않는가?
- [ ] default parameter, JSON 직렬화, object spread의 nullish 동작을 확인했는가?
- [ ] index·`Map#get`의 부재를 타입이나 존재 확인으로 다루는가?
- [ ] `satisfies`를 runtime validation이나 cast처럼 쓰지 않았는가?
- [ ] mutable/public 값에는 필요한 widening·계약 annotation이 있는가?
- [ ] 외부 값은 소유 경계에서 한 번 검증·정규화되는가?
- [ ] 내부 함수가 신뢰된 좁은 타입을 받고 중복 guard를 만들지 않는가?
- [ ] type predicate가 반환 타입의 전체 runtime 사실을 증명하는가?
- [ ] 불가능한 상태를 정상 fallback으로 숨기지 않는가?
- [ ] `forEach(async ...)`, floating promise, 부분 성공과 retry 위험이 없는가?
- [ ] boolean soup, optional soup, DTO 누수, double assertion과 의미 없는 wrapper가 없는가?
- [ ] finding마다 실제 trigger·영향·최소 수정·예외가 있는가?

## 근거

- [TypeScript: `strictNullChecks`](https://www.typescriptlang.org/tsconfig/strictNullChecks.html)
- [TypeScript: `exactOptionalPropertyTypes`](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html)
- [TypeScript: `noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html)
- [TypeScript 4.9: `satisfies`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [TypeScript narrowing과 type predicates](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript issue #55189: contextual typing과 literal inference](https://github.com/microsoft/TypeScript/issues/55189)
- [TypeScript issue #52805: optional property가 결과에 추가되지 않음](https://github.com/microsoft/TypeScript/issues/52805)
- [TypeScript issue #57086: optional property spread와 explicit `undefined`](https://github.com/microsoft/TypeScript/issues/57086)
- [MDN: Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: `Map.prototype.get`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map/get)
- [MDN: `JSON.stringify`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)
- [MDN: default parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Default_parameters)
- [MDN: `Promise.all`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)
- [typescript-eslint rules](https://typescript-eslint.io/rules/)
