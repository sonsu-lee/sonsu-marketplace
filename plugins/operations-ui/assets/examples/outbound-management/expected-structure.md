# Outbound management example

이 디렉터리는 WMS가 플러그인의 기본 도메인이라는 뜻이 아니라, 사용자가 제공한 사례를 Screen Contract와 Quality Report로 옮긴 **구조 예시**다.

`quality-report.json`은 모든 gate와 check를 `not_run`, `browser_receipts`를 빈 배열로 둔 형식 예시이며 실제 실행 증거가 아니다. 이 파일이 validator를 통과한다는 사실도 target UI, browser behavior나 gate 통과를 증명하지 않는다. 실제 작업에서는 각 상태를 실제 판정과 evidence로 교체해야 한다.

예상 화면 구조는 다음과 같다.

1. dark persistent navigation과 compact topbar
2. page context와 primary action
3. lifecycle status summary
4. high-frequency filter bar
5. selection-aware batch actions
6. dense data table
7. drawer 또는 route 기반 detail surface

같은 구조는 support case queue, finance review queue, content moderation inbox처럼 entity와 lifecycle만 다른 운영 화면에도 적용할 수 있다.
