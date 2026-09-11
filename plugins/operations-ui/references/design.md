# Precision Operations Console

## 목적

Precision Operations Console은 운영자가 많은 데이터와 상태를 빠르게 읽고, 위험을 구분하고, 다음 행동을 정확하게 선택하게 하는 단일 디자인 언어다. 산업명보다 다음 조건으로 적용 여부를 판단한다.

- 반복적으로 처리할 엔터티와 lifecycle이 있다.
- 상태, 예외, SLA 또는 위험이 의사결정에 영향을 준다.
- 검색, 필터, 표, 대량 작업 또는 상세 확인이 핵심이다.
- 잘못된 행동의 운영 비용이 있어 권한과 피드백이 중요하다.

마케팅, 콘텐츠 감상, 브랜드 스토리텔링이나 감성적 탐색이 주목적인 화면에는 적용하지 않는다.

## 시각 문법

### 구조

- standalone console은 `240px` dark sidebar, `48px` topbar, light workspace를 기본 shell로 사용한다.
- content padding은 `24px`, section gap은 `16px`를 기준으로 한다.
- dashboard summary는 장식이 아니라 클릭 가능한 상태 필터 또는 명시적인 읽기 전용 KPI여야 한다.
- list workspace의 기본 순서는 `page context → status summary → filters → batch actions → data table → detail surface`다.
- 표는 기본 `48px` row, form control은 `36px`, compact control은 `32px`다.

Screen Contract의 `primary_decision`을 기준으로 먼저 읽을 정보와 다음 행동을 정하고 이 순서를 배치에 반영한다.
예를 들어 상태명과 건수, label과 입력값은 가까이 묶고, 필터 묶음과 결과 표 사이에는 더 큰 간격을 둔다.
같은 정보 묶음의 제목·설명·control은 읽기 방향의 시작선을 맞추되 숫자 열은 비교하기 쉬운 끝선 정렬을 유지한다.
간격은 기존 spacing token에서 골라 관계를 표현하며 모든 요소에 같은 gap을 주거나 새 card로 감싸서 구분하지 않는다.

### 색상

- canvas `#F4F6F8`, surface `#FFFFFF`, border `#E1E7EF`
- sidebar `#1D2B3C`, hover `#24364A`
- primary/selection `#356BD6`, hover `#2858BA`, subtle `#EAF1FF`
- text primary `#0F172A`, secondary `#64748B`, disabled `#94A3B8`
- success `#26734D`/`#E8F5EE`, warning `#9A6700`/`#FFF2CC`, danger `#D92D20`/`#FDECEC`

색은 의미를 대신하지 않는다. status에는 text 또는 icon label을 함께 둔다. contrast를 맞추기 위한 파생 shade는 허용하지만 semantic role과 hierarchy를 바꾸지 않고 Quality Report에 근거를 남긴다.

### 형태와 깊이

- default radius는 `10px`, small radius는 `6px`다.
- border와 surface contrast를 먼저 사용하고 shadow는 floating overlay나 구분이 꼭 필요한 shell에만 제한한다.
- gradient, glass, glow, oversized illustration은 기본 문법이 아니다.
- map/control-tower처럼 공간 정보가 작업의 핵심일 때만 dark content surface를 쓸 수 있다. 일반 table/list 화면을 dark theme로 바꾸지 않는다.

면 안에 면이 균일한 간격으로 들어갈 때에는 모서리의 관계를 함께 본다. 원호형 모서리라면
`inner radius = max(0, outer radius - inset)`을 출발점으로 검토한다. inset은 CSS border를 포함한 두 윤곽 사이의
거리다. 예를 들어 radius `10px`인 면에서 border와 padding을 합친 inset이 `4px`라면 내부는 기존 small radius
`6px`와 맞는다. 이 예시는 기본 padding이나 token을 바꾸는 지시가 아니다. pill, 독립된 내부 버튼, 비대칭 여백이나
다른 곡선 형태는 기존 component를 우선하고, 중첩 면의 국소 조정은 실제 렌더링으로 확인한다.

### 타이포그래피와 밀도

- 숫자, 상태, 식별자는 빠르게 훑을 수 있게 tabular alignment와 일관된 weight를 사용한다.
- 화면 제목, section 제목, cell 본문, control label, 보조 설명의 역할을 기존 typography style에 매핑한다. 같은
  역할은 같은 style을 재사용하고 필요한 역할이 없을 때만 보완한다. 크기를 전부 키우기보다 정보 관계, 간격,
  weight와 label/value 대비로 계층을 만들며 보조 설명에도 실제 배경에서 읽을 수 있는 대비를 유지한다.
- density를 높이되 primary action, destructive action, status와 selection은 주변 정보와 분명히 구분한다.
- ellipsis는 접근 경로가 있을 때만 허용한다. tooltip, drawer, detail page 또는 expandable cell 중 하나를 제공한다.

## 기존 시스템과의 관계

대상 코드베이스에 token과 component가 있으면 먼저 읽고 semantic role을 매핑한다. 값이 다르다는 이유만으로 전면 교체하지 않는다. 단, 매핑 결과가 이 디자인 언어의 대비, 상태 의미, 밀도나 hierarchy를 훼손하면 차이를 기록하고 최소한의 derived token 또는 component change를 제안한다.

## 판정

이 문서의 값과 시각 문법은 [quality-contract.md](quality-contract.md)의 G2에서 실제 렌더링과 token mapping으로 검증한다.
기존 G1의 `information-hierarchy`에는 먼저 읽을 정보와 다음 행동이 드러나는지를, G2의 `density-and-components`에는
반복되는 정보 묶음·텍스트 역할·중첩 면이 일관되는지를 연결한다. Screen Contract에 선언된 viewport와 긴 번역문에서도 이 관계를 확인하고
텍스트 대비는 G6의 기존 `contrast` 근거로 판정한다. 문서나 Figma만 존재하고 실제 UI가 없으면 G2와 G7은 통과할 수 없다.
