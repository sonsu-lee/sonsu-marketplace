# ADR 0018: UI 디자인 작업을 하나의 플러그인으로 통합

- 날짜: 2026-09-28
- 상태: 채택
- 대체하는 디자인 패키지 결정: [ADR 0010](0010-add-figma-workflow-plugin.md)의 독립 Figma 패키지 경계

## 결정

공개 플러그인은 `design` 하나로 두고 표시 이름도 Design으로 한다. 공개 스킬은
신규 설계 `design-interface`, 재설계 `redesign-interface`, 읽기 전용 감사 `audit-interface`다.
운영 업무 계약과 Figma native 제작·prototype·감사 절차는 플러그인 내부의 조건부 참고 자료다.
공식 Figma connector metadata와 수동 Desktop companion도 같은 패키지에 둔다.

작업 시작 시 대상 제품, 기존 `DESIGN.md`, 레퍼런스, 제품 디자인 시스템과 보존할 동작을 확인한다.
새 설계·재설계에서는 Google 형식 `DESIGN.md`를 작성·검증하고 감사는 읽기 전용으로 확인한다.
Figma를 사용하면 화면·상태·요청한 prototype을 먼저 Figma에서 만들고 검토 가능한 결과를 제시한다.
그 revision을 코드로 옮기는 일에는 명시적 허가가 필요하다. Figma를 사용하지 않는 요청은
대상 앱에서 직접 구현하고 실행 화면을 검증한다.

기존 DQ0–DQ8 임계치와 저장된 contract/report의 `profile` 값은 이번 구조 변경에서 유지한다.
기존 `interface-design`, `operations-ui`, `figma-workflow` 설치는 `design` 설치 후 진행 중인
작업 기록을 확인·이전하고 제거한다. 세 패키지는 더 이상 독립 설치 패키지로 배포하지 않는다. 저장된
`profile` 문자열은 이전 계약과의 호환성 값이며 공개 스킬 라우팅의 이름은 아니다.

## 이유와 범위

기존 세 플러그인은 같은 과업·산출물·디자인 품질 계약을 중복 선택하게 했다. 공개 진입점을
작업 유형으로 고정하면 일반/운영 도메인과 Figma/코드 경로를 같은 명세에서 이어갈 수 있다.
세부 품질 기준 개선, 저장 계약 v2 전환과 native Figma 능력 검증은 별도 작업으로 다룬다.
