# Operations visual and interaction principles

Operations UI의 시각 언어는 고정 팔레트·sidebar 폭·row 높이·radius가 아니다. 대상 제품의 기존
디자인 시스템을 먼저 읽고 사용자 판단에 필요한 semantic role로 매핑한다.

## 화면을 구성하는 순서

1. `primary_question`에 답하는 데 필요한 must-know 정보를 먼저 둔다.
2. 비교가 중요한 정보는 공통 축과 일관된 형식으로 배치한다.
3. supporting 정보는 판단을 방해하지 않는 가까운 위치에, on-demand 정보는 detail/overlay에 둔다.
4. primary action은 과업의 다음 단계와 일치시킨다. 위험한 행동은 결과·범위·복구 가능성을 먼저 보여준다.
5. 상태·위험·선택은 색상뿐 아니라 텍스트, 아이콘, 위치 또는 형태 중 적절한 중복 신호를 가진다.

## 디자인 시스템 매핑

- 기존 semantic token과 component가 있으면 값을 복제하지 않고 ID로 매핑한다.
- 시스템이 없으면 필요한 role과 결정 근거부터 정의하되 임의 브랜드 테마를 제품 규칙처럼 강제하지 않는다.
- spacing, density, type, radius는 실제 정보량·입력 방식·접근성·기기에서 검증한다.
- card, border, shadow는 정보 그룹이나 layer를 설명할 때만 쓴다. 모든 영역을 장식적 container로 감싸지 않는다.
- ellipsis는 전체 값에 접근할 경로가 있을 때만 사용한다.

## 환경과 현지화

왼쪽→오른쪽·가로쓰기·desktop을 기본 인간 원칙으로 취급하지 않는다. contract의 locale,
`writing_mode`, 화면 크기, pointer/touch/keyboard/screen reader 입력을 기준으로 읽기 순서와 조작을
검증한다. 좁은 환경에서는 정보를 숨기는 대신 과업 우선순위에 따라 reflow, disclosure, scroll,
detail access 중 하나를 선택하고 must-know 정보가 유실되지 않는지 확인한다.
