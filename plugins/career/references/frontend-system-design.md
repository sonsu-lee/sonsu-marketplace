# 프론트엔드 시스템 설계

`prepare-interview`의 system-design 준비와 `mock-interview`의 `system-design` 모드가 읽는다. 알고리즘
문제 풀이와 채점은 다루지 않는다.

## RADIO 요약

출처: [GreatFrontEnd Front End System Design Playbook, RADIO framework](https://www.greatfrontend.com/front-end-system-design-playbook/framework).
아래는 그 틀을 이 플러그인 용도로 직접 정리한 것이며 원문을 옮기지 않았다.

RADIO는 프론트엔드 설계 면접에서 다룰 다섯 영역의 머리글자다.

- Requirements: 무엇을 만들지 범위를 좁힌다. 핵심 사용 사례, 지원 기기, 데이터 규모, 꼭 필요한 기능과
  뺄 기능을 면접관에게 확인한다.
- Architecture: 화면을 이루는 큰 부품과 그 사이의 책임을 나눈다. 뷰, 클라이언트 상태 저장소, 서버
  통신 계층처럼 부품을 그리고 데이터가 어디서 어디로 흐르는지 설명한다.
- Data model: 클라이언트가 들고 있을 데이터의 모양을 정한다. 서버에서 온 데이터와 화면에서만 쓰는
  상태를 구분하고 각각 어느 부품이 소유하는지 밝힌다.
- Interface: 부품 사이와 서버와의 계약을 정한다. API 요청·응답 형태, 페이지네이션 파라미터, 컴포넌트
  props와 이벤트를 적는다.
- Optimizations: 남은 시간에 깊이를 보여 준다. 성능, 접근성, 네트워크 실패, 국제화처럼 이 문제에서
  가장 중요한 영역을 골라 파고든다.

### 시간 배분

- Requirements: 10% 이하
- Architecture: 약 20%
- Data model: 약 10%
- Interface: 약 20%
- Optimizations: 남은 시간

순서를 고정하지 않는다. 요구사항부터 시작하고, 이후에는 면접관의 관심과 문제의 성격에 맞춰 오간다.

## 출제 유형 범주

- news feed
- autocomplete
- image carousel
- chat
- video player
- e-commerce product page
- rich text editor
- data table/dashboard

## 깊이 파기 체크리스트

- 렌더링 전략: CSR/SSR/SSG
- server state와 client state, 캐싱
- 페이지네이션·가상화
- 네트워크: debounce, 취소, 재시도
- 성능: LCP/INP/CLS, 번들 분할
- 접근성: 키보드, focus, ARIA
- i18n, 오프라인
- 보안: XSS, CSRF, 토큰 보관
- 관측성

## 평가 축

- 요구사항 명확화
- 컴포넌트 책임
- 데이터 모델
- API·props 계약
- 최적화 깊이
- 트레이드오프 설명
- 시간 관리

## 준비 방법

내 F-/S-를 각 깊이 파기 항목에 대응시킨다. 대응하는 사실이 있는 항목은 설계 중에 "실제로 이렇게 해
봤다"는 근거로 쓰고, 없는 항목은 원리 수준으로 설명할 준비를 한다. 사실은
[근거 규칙](evidence-rules.md)을 따른다.
