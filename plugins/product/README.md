# Product

제품 아이디어를 넓히고 문제·근거·도메인 규칙을 정리하며, 검증을 설계·판정한 뒤 합의된 내용만 PRD로 변환합니다.

## 설치

```bash
codex plugin add product@sonsu-marketplace
claude plugin install product@sonsu-marketplace
omp plugin install product@sonsu-marketplace
```

omp에서는 기본 구성에 들지 않는 opt-in 패키지이므로 필요할 때 직접 설치합니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `product-brainstorming` | 제품 문제·기회·해법 후보를 넓힐 때 | 가정과 검증 질문이 붙은 구분되는 후보 |
| `product-discovery` | PRD 전에 문제·사용자·결과·규칙과 미결정을 구체화할 때 | 출처에 연결된 탐색 결과, 준비 상태, 다음 결정 |
| `synthesize-product-evidence` | 여러 인터뷰·피드백·지표를 종합할 때 | 근거 원장, theme·반례·한계 |
| `product-domain-discovery` | 제품 용어·상태·규칙을 같은 언어로 맞출 때 | 확인 상태가 붙은 후보 도메인 모델 |
| `design-product-test` | 제품 가설을 실행 전 test plan으로 만들 때 | 사전 판정 기준을 고정한 계획 |
| `assess-product-test` | 실행된 검증 결과를 해석할 때 | `supported`·`invalidated`·`inconclusive`·`invalid`·`not-run`·`mixed` 판정과 한계 |
| `to-prd` | 합의된 제품 내용을 PRD로 쓰거나 갱신할 때 | PRD-lite·전체 PRD 또는 `blocked` 판정과 다음 결정 |

스킬은 요청의 목적과 현재 근거 상태에 따라 어느 것에서든 시작합니다. 작업 크기별 후속 산출물은 [인계 계약](references/delivery-handoff.md)을 따르고, 외부 조사·기술 설계·구현은 해당 플러그인이나 대화 안내로 이어 갑니다.

## 사용 예시

요청: “배송 지연 문의를 줄일 방법을 넓게 생각해 보고, 가장 유력한 가설을 검증할 계획까지 세워 줘.”

`product-brainstorming`이 문의 원인별 후보를 가정과 함께 제시하고, `design-product-test`가 선택한 가설의 반증 관찰과 사전 판정 기준을 정합니다. 수치 기준이 합의되지 않았다면 `open`으로 남깁니다.

## 구성

여러 단계 작업은 [작업 연속성](references/continuity.md)으로 `.sonsu/continuity/`에 진행과 근거 위치를 기록합니다. 포함된 `SessionStart` hook은 호스트에서 신뢰한 뒤 실행되며, 형식은 [기록 형식](../../docs/reference/task-continuity.md)에 있습니다.

## 검증

```bash
python3 -B -m unittest plugins/product/tests/test_validate_prd.py
python3 -B -m unittest discover -s evals/task-continuity -p 'test_*.py'
```
