> 이 평가는 외부 원본으로 교체하기 전의 자체 제작 Fluent 스킬을 대상으로 한 역사적 snapshot이다. `current`는 당시 후보를 뜻한다.

# 세 Fluent 플러그인 비교 평가

`protocol.md`와 `cases.json`을 고정한 뒤 같은 입력을 `none`, `legacy`, `current`에
반복 적용한다. `legacy`는 분리 전 저장소 commit `e24c1249a64022a77627023a41d1e5e3846ca71e`의
`fluent-languages` 스킬이다. `current`는 세 독립 패키지의 현재 스킬이다.

실제 모델 출력, trace와 판정은 저장소 밖의 실행 디렉터리에 보존한다. 보고서는
실행 snapshot의 hash와 집계 결과를, 외부 실행 디렉터리는 사례별 결과를 포함한다. 이 실험은 지침 본문을 직접 제공하며,
설치된 플러그인의 자동 선택이나 원어민 품질을 측정하지 않는다.

[2026-09-25 실행 결과](results-2026-09-25.md)를 확인한다.
