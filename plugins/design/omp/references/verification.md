# 디자인 품질 검증

[공통 디자인 품질 계약](design-quality.md)의 DQ0–DQ8을 사용한다. 필수 gate는 각각 통과해야
하며 평균 총점을 만들지 않는다.

1. DQ0에서 계약 revision, traceability와 metric target이 결과 관찰 전에 잠겼는지 확인한다.
2. DQ1–DQ2에서 대표 과업을 따라 사용자가 올바른 판단에 필요한 must-know 정보를 찾고 설명할 수 있는지 본다.
3. DQ3에서 시각 위계와 강조가 의미·우선순위·대상 디자인 시스템에 연결되는지, 색만으로 의미를 전달하지 않는지 본다.
4. DQ4–DQ5에서 적용 가능한 상태, 긴 콘텐츠·현지화·극단값, action feedback·권한·오류·복구를 확인한다.
5. DQ6에서 contract의 viewport, locale, writing mode, input과 accessibility profile을 실제로 확인한다.
6. DQ7에서 proposal/Figma/code에 맞는 provenance, structure/readback/runtime evidence를 연결한다.
7. DQ8에서 사전 등록 outcome metric과 low/medium/high 위험에 맞는 사용자 증거를 확인한다.

DQ1–DQ6은 작성자가 아닌 독립 평가자 2명이 0–4점으로 판정한다. 두 점수의 최솟값이 3
이상이어야 하고 차이가 1보다 크면 `inconclusive`다. open critical finding과 hard check 실패는
다른 점수로 상쇄할 수 없다.

제안은 실제 시각적 제안과 명세의 일치, Figma는 screenshot·native structure·binding·resize와
요청된 reaction/playback, 코드는 실제 실행 환경의 렌더링·조작·검사 결과를 각각 증명한다.
정적 시안의 버튼을 동작 구현으로, 모의 데이터 이미지를 실제 데이터 검증으로 보고하지 않는다.

실패는 원인이 있는 계약·정보·표현·상태·실행·outcome 단계로 돌린다. 결과 파일/미리보기,
주요 결정·전후 차이, gate별 실제 근거와 `not_run`을 분리해 전달한다.
