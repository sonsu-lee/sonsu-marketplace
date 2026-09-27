# Outbound management example

이 디렉터리는 WMS가 플러그인의 기본 도메인이라는 뜻이 아니라, 운영 과업을 Design Decision Contract와 Quality Report로 옮긴 **구조 예시**다.

`quality-report.json`은 모든 gate와 check를 `not_run`, `browser_receipts`를 빈 배열로 둔 형식 예시이며 실제 실행 증거가 아니다. 이 파일이 validator를 통과한다는 사실도 target UI, browser behavior나 gate 통과를 증명하지 않는다. 실제 작업에서는 각 상태를 실제 판정과 evidence로 교체해야 한다.

실제 화면 구조는 contract의 `primary_question`, must-know 정보와 제품 디자인 시스템에서 정한다.
다음은 가능한 작업 구조이지 고정 shell이 아니다.

1. 현재 판단 맥락과 다음 행동
2. lifecycle·위험·신선도를 비교하는 정보
3. 작업 범위를 좁히는 검색·필터
4. 선택 범위와 권한이 분명한 action
5. must-know 정보를 비교할 list/table/board
6. supporting·on-demand 정보를 확인할 detail surface

같은 구조는 support case queue, finance review queue, content moderation inbox처럼 entity와 lifecycle만 다른 운영 화면에도 적용할 수 있다.
