# JavaScript·TypeScript 리뷰 판단 평가

이 fixture는 Code Review의
[`JavaScript·TypeScript 개인 리뷰 체크리스트`](../../plugins/code-review/references/javascript-typescript-review.md)가
실제 코드 문맥에서 올바른 finding과 no-finding을 구분하는지 평가합니다.

## 평가 범위

[`cases.json`](cases.json)의 각 사례는 다음을 함께 제공합니다.

- 실제 코드와 필요한 caller·도메인 계약
- 기대 finding 또는 no-finding
- 허용할 최소 수정 방향
- 무조건적인 hardening이나 잘못된 단순화를 막는 `must_not`

평가 모델에는 `id`와 `expected`를 숨기고 `request`, `contract`, `code`, `context`만 제공합니다.
Code Review의 요청에 맞는 focused skill과 공통 reference를 읽게 한 뒤 결과를 `expected`와
대조합니다. 단어 포함 여부만으로 통과시키지 않고 trigger, 실제 영향, 경계 소유자와 최소 수정이
현재 코드 흐름에 맞는지 확인합니다.

결과는 `pass`, `fail`, `not_run`, `inconclusive`로 기록합니다. JSON parsing과 TypeScript compiler
fixture 성공은 모델 판단 품질의 `pass`가 아닙니다. skill selection attribution이나 실제 모델
출력을 확인하지 못했으면 `not_run`, 필수 코드·caller 근거가 빠졌으면 `inconclusive`입니다.

## TypeScript compiler fixture

[`compiler/satisfies-contract.ts`](compiler/satisfies-contract.ts)는 TypeScript `5.9.2`와 아래 option을
기준으로 `satisfies`의 contextual typing, optional property 부재와 mutable widening 대안을
고정합니다.

```sh
npm exec --yes --package typescript@5.9.2 -- \
  tsc --noEmit --strict --exactOptionalPropertyTypes \
  --noUncheckedIndexedAccess --useUnknownInCatchVariables \
  evals/javascript-typescript-review/compiler/satisfies-contract.ts
```

`@ts-expect-error`가 붙은 줄은 오류가 있어야 전체 compile이 성공합니다. 외부 값을 runtime에서
검증하지 않는다는 별도 사례는 compile 후 실행합니다.

```sh
fixture_out="$(mktemp -d)"
npm exec --yes --package typescript@5.9.2 -- \
  tsc --strict --target ES2022 --module commonjs \
  --outDir "$fixture_out" \
  evals/javascript-typescript-review/compiler/satisfies-runtime.ts
node "$fixture_out/satisfies-runtime.js"
```

성공 출력은 `satisfies-does-not-validate-runtime:number`입니다. 이는 잘못된 값이 안전하다는 뜻이
아니라 `satisfies`가 runtime 값을 바꾸거나 검사하지 않는다는 반례입니다.

## 정적 검증과 실제 실행 구분

```sh
python3 -m json.tool evals/javascript-typescript-review/cases.json >/dev/null
```

위 명령은 fixture 문법만 확인합니다. 모델 기반 사례 실행과 격리된 Codex 설치본에서 관련 스킬이
공통 reference를 실제로 읽는지 확인하는 native loading·behavior 검증은 별도입니다. 실행하지
않은 항목을 통과로 기록하지 않습니다.
