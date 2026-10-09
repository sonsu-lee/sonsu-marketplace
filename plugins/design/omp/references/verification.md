# 디자인 품질 검증

[공통 디자인 품질 계약](design-quality.md)의 DQ0–DQ8을 사용한다. 필수 gate는 각각 통과해야
하며 평균 총점을 만들지 않는다.

1. DQ0에서 계약 revision, traceability와 metric target이 결과 관찰 전에 잠겼는지 확인한다.
   입력의 기존 요구사항 ID·출처·관련 조건과 실제 화면·상태·흐름의 대응을 명세·annotation에서 대조한다. 요청 범위의 누락을 확인하며 ID 없는 출처에 ID를 새로 요구하지 않는다.
   버전 있는 요구 출처는 사용한 리비전 또는 snapshot·범위와 적용되는 승인 근거도 대조한다. 현재 출처의 의미가 바뀌었으면 영향받은 대응·근거를 재검증하고 미확인 연결을 통과시키지 않는다. 기존 고정 입력 참조를 허용하며 버전 없는 출처에 metadata를 요구하지 않는다.
2. DQ1–DQ2에서 대표 과업을 따라 사용자가 올바른 판단에 필요한 must-know 정보를 찾고 설명할 수 있는지 본다.
3. DQ3에서 시각 위계와 강조가 의미·우선순위·대상 디자인 시스템에 연결되는지, 색만으로 의미를 전달하지 않는지 본다.
4. DQ4–DQ5에서 적용 가능한 상태, 긴 콘텐츠·현지화·극단값, action feedback·권한·오류·복구를 확인한다.
5. DQ6에서 contract의 viewport, locale, writing mode, input과 accessibility profile을 실제로 확인한다.
6. DQ7에서 proposal/Figma/code에 맞는 provenance, structure/readback/runtime evidence를 연결한다.
7. DQ8에서 사전 등록 outcome metric과 low/medium/high 위험에 맞는 사용자 증거를 확인한다.

독립 평가자·점수·판정 보류·필수 gate의 통과 조건은
[차원별 합격](design-quality.md#차원별-합격)을 따른다.

레퍼런스를 잠근 작업은 결과를 primary와 나란히 놓고 `borrow`만 반영했는지, `do_not_borrow`·브랜드
자산·레퍼런스의 실제 수치와 문구를 옮기지 않았는지 확인한다. 레퍼런스와 닮았다는 것은 어느 gate의
통과 근거도 아니다.

제안은 실제 시각적 제안과 명세의 일치, Figma는 screenshot·native structure·binding·resize와
요청된 reaction/playback, 코드는 실제 실행 환경의 렌더링·조작·검사 결과를 각각 증명한다.
정적 시안의 버튼을 동작 구현으로, 모의 데이터 이미지를 실제 데이터 검증으로 보고하지 않는다.

실패는 원인이 있는 계약·정보·표현·상태·실행·outcome 단계로 돌린다. 결과 파일/미리보기,
주요 결정·전후 차이, gate별 실제 근거와 `not_run`을 분리해 전달한다.

## 구조 검증 명령

기존 계약·보고서 또는 작성한 결과에 다음 명령을 실행한다. 읽기 전용 감사는 기존 파일만
검사하고 부재·오류를 finding으로 남긴다.

```bash
python3 <design-plugin-root>/scripts/validate_design_quality.py contract <contract.json>
python3 <design-plugin-root>/scripts/validate_design_quality.py report <report.json> <contract.json>
```

`OK: contract`·`OK: report`와 종료 코드 `0`은 구조 검사 통과다. `ERROR:`와 종료 코드 `1`이면
표시한 오류를 수정한 뒤 다시 검사한다. 구조 검사 결과와 실제 화면·동작·사용자 결과의 근거는
구분한다. `DESIGN.md` 검사 명령·상태별 행동은 [공통 절차](design-quality.md#designmd-공통-절차)를 따른다.

운영 화면은 확장 계약과 runtime 이미지 근거도 검사한다.

```bash
python3 <design-plugin-root>/scripts/validate_operations_contracts.py contract <contract.json>
python3 <design-plugin-root>/scripts/validate_operations_contracts.py report <report.json> <contract.json>
```

`Validation passed.`와 종료 코드 `0`이면 구조·파일 검사 통과다. 종료 코드 `1`이면 출력된
오류 목록을 처리한다. 실제 실행을 확인하지 못한 항목은 미확인 상태로 유지한다.
