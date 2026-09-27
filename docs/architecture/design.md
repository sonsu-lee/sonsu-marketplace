# UI 디자인 작업 구조

`design` 하나가 신규 설계, 재설계, 읽기 전용 감사를 담당합니다. 공개 스킬은
`design-interface`, `redesign-interface`, `audit-interface`입니다. 일반 UI와 운영 UI의 차이는
도메인 계약으로, Figma와 코드의 차이는 실행 경로로 다룹니다.

```mermaid
flowchart TD
  A[요청·대상 제품·레퍼런스 확인] --> B{작업 유형}
  B -->|신규| C[design-interface]
  B -->|기존 변경| D[redesign-interface]
  B -->|수정 없음| E[audit-interface]
  C --> F{Figma가 정본인가}
  D --> F
  E --> G[대상 읽기·finding]
  F -->|예| H[Figma 화면·상태·prototype 제작과 readback]
  H --> I[검토 가능한 결과 제시]
  I --> J{코드 이전 허가}
  J -->|명시적 허가| K[기존 앱 구현과 runtime 확인]
  F -->|아니오| K
```

모든 경로는 대상 앱의 가장 가까운 Google 형식 `DESIGN.md`, 제품 component·token,
실제 사용자 과업을 읽습니다. 새 설계·재설계는 문서를 작성·갱신하고 공통 명령으로 검증합니다.
읽기 전용 감사는 문서를 수정하지 않습니다. 레퍼런스의 시각 구성과 실제 제품 값·상태·기능을
구분하고, 기존 제품 동작은 보존 또는 명시적 변경으로 추적합니다.

운영 업무이면 [Operations 계약](../../plugins/design/references/operations/screen-contract.md)의
requirement↔scenario, action·permission·risk·state, 부분 실패·복구를 적용합니다. Figma 경로는
[공식 도구·native 증거](../../plugins/design/references/figma/workflow.md)를 사용합니다.
Figma에서 코드로 옮기기 전에는 실제 결과의 범위와 revision에 대한 명시적 허가가 필요합니다.
직접 코드 경로는 기존 프로젝트의 UI를 구현하고 실제 화면·대표 조작을 확인합니다.

공통 DQ 계약의 `profile` 값은 기존 저장된 계약·리포트 호환성을 위해 이번 구조 정리에서는
유지합니다. 공개 스킬 선택 기준이 아니며, Figma 산출물에는 Figma receipt를, 운영 업무에는
Operations 확장을 적용합니다. DQ 임계치와 세부 품질 개선은 별도 작업으로 다룹니다.
