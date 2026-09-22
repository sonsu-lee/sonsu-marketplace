# Product

제품 탐색, 근거 종합, 도메인 발견, 검증 설계·판정과 PRD 작성을 각각 독립 완료하는 `1.0.0`
capability pack이다.

## Skills

- `product-discovery`: 사용자, 문제, 기대 결과, 범위, 규칙과 미결정 사항 탐색
- `synthesize-product-evidence`: interview, survey, feedback, issue와 metric을 traceable theme,
  반례와 불확실성으로 종합
- `product-domain-discovery`: 용어, actor, state, event, rule과 exception 후보 발견
- `design-product-test`: 가설의 반증 조건, 방법, 계측과 판정 기준 설계
- `assess-product-test`: 사전 기준과 실제 한계에 따른 결과 판정
- `to-prd`: 승인된 제품 결정을 PRD 문서 또는 초안으로 변환

고정 pipeline이 아니다. 각 skill은 다른 plugin 호출이나 continuity state 없이 요청한 산출물을
독립적으로 완료한다. 일반 아이디어 발산은 host가 담당한다. 외부 조사, 구현, Git delivery와
provider mutation을 Product 책임으로 확장하지 않는다.

`to-prd`는 PRD 파일/초안만 소유한다. issue 생성은 별도 `workflow:to-ticket` 책임이며 Product가
설치나 실행을 가정하지 않는다. 핵심 결정이 없으면 임의로 채우지 않고 `blocked`와 필요한 결정만
반환한다.

```sh
codex plugin add product@sonsu-marketplace
```
