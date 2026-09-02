# Product

제품 아이디어를 넓히고, 문제와 사용자를 구체화하고, 제품 근거와 도메인 규칙을 정리하고,
검증을 설계·판정한 뒤 승인된 내용만 PRD로 변환하는 개인용 Codex 플러그인입니다.

## 포함된 스킬

- `product-brainstorming`: 제품 문제, 기회와 해법 후보를 넓히되 검증된 결론으로 표현하지 않습니다.
- `product-discovery`: 사용자, 문제, 기대 결과, 범위, 제품 규칙과 미해결 결정을 구체화합니다.
- `synthesize-product-evidence`: 인터뷰, 설문, 피드백, 이슈와 지표를 출처에 연결된 theme,
  반례와 불확실성으로 종합합니다.
- `product-domain-discovery`: 제품의 용어, 행위자, 상태, 사건, 규칙과 예외를 정본이 아닌 후보
  모델로 정리합니다.
- `design-product-test`: 제품 가설의 반증 조건, 방법, 계측과 판정 기준을 실행 전에 정합니다.
- `assess-product-test`: 실행 결과를 사전 기준과 실제 한계에 따라 판정합니다.
- `to-prd`: 현재 리비전에 대해 합의된 제품 결정만 추적 가능한 PRD로 변환합니다.

## 조합과 경계

이 스킬들은 고정된 7단계 pipeline이 아닙니다. 요청의 직접 목적과 현재 증거 상태에 따라 어느
스킬에서든 시작하고, 검증 결과에 따라 앞선 탐색으로 돌아갈 수 있습니다. 각 스킬은 다른
플러그인의 설치나 선행 실행을 전제로 하지 않습니다.

외부의 여러 출처를 새로 조사해야 하면 Research와 runtime에서 조합할 수 있습니다. 승인된
요구사항을 구현해야 하면 Engineering과 조합할 수 있지만, Product manifest에는 plugin
dependency를 선언하지 않습니다. 기술 설계, 코드 구현, Git delivery와 외부 상태 변경은 이
플러그인의 책임이 아닙니다.

## 설치

마켓플레이스를 등록한 뒤 다음 명령으로 설치합니다.

```sh
codex plugin add product@sonsu-marketplace
```

기존 standalone `product-discovery` 또는 `to-prd`를 동시에 노출하면 같은 요청에 스킬이 경쟁할
수 있습니다. 플러그인판을 격리 검증한 뒤 실제 사용 환경에서는 기존 복사본을 discovery
경로에서 제외합니다.
