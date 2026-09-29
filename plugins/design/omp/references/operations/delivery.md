# 산출물별 작업 경계

시작할 때 `artifact_scope`를 `proposal`, `figma`, `implementation`, `live` 중 하나로 고정한다.
여러 산출물을 요청하면 계약과 증거를 범위별로 분리한다. 모드(`greenfield`, `redesign`, `audit`)는
사용자가 부여한 읽기·쓰기 권한을 확대하지 않는다.

| 범위 | 필요한 품질 게이트 | 완료가 의미하는 것 |
| --- | --- | --- |
| proposal | DQ0–DQ6 | 설계 판단과 표현 제안이 현재 계약에서 통과 |
| figma | DQ0–DQ7 | native Figma 구조·resize·요청된 prototype 증거까지 통과 |
| implementation | DQ0–DQ7 | 코드와 실제 runtime 증거까지 통과 |
| live | DQ0–DQ8 | 사전 등록 지표와 위험도에 맞는 사용자 증거까지 통과 |

앞 단계의 `scope_status: passed`는 뒤 단계의 통과가 아니다. live 이전에는
`end_to_end_status: passed`와 `claim_level: validated`를 사용할 수 없다.

일반 콘텐츠·브랜드·에디토리얼 화면은 자동 라우팅에서 일반 UI 스킬을 우선한다. 사용자가 이
플러그인을 직접 지정하면 차이를 밝히고 현재 산출물에 필요한 공통 디자인 판단만 적용한다.
Figma는 명시 요청일 때만 사용하며 코드 구현이나 브라우저 검증의 선행 조건이 아니다.
