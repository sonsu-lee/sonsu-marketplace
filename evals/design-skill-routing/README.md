# Design 스킬 라우팅 평가

`cases.json`은 Design 플러그인과 공식 Figma·FigJam, Paper MCP, draw.io가 함께 있거나 일부만
있는 환경에서 요청의 최종 artifact에 맞는 스킬과 도구가 선택되는지 정의합니다.

핵심 경계는 다음과 같습니다.

- 제품 화면, native component·variable와 Auto Layout은 `design:figma-product-design`, actual reaction과
  clickable interaction은 `design:figma-prototype-flow`가 Figma Design 안에서 담당합니다.
- 기존 Figma artifact의 읽기 전용 구조·품질 검토는 `design:figma-design-audit`가 담당합니다.
- 협업용 초기 여정과 workshop board는 FigJam이 담당합니다.
- AWS, network, UML, ERD와 system architecture는 draw.io가 담당합니다.
- HTML/CSS 구조와 code roundtrip 중심의 화면 탐색은 Paper Design이 담당합니다.
- 공식 `figma-design-to-code`와 `figma-generate-library`의 직접 책임은 로컬 Design 스킬이
  가로채지 않습니다.
- Figma 화면·composed view 생성은 로컬 `figma-product-design`의 품질 계약과 공식
  `figma-generate-design`·`figma-use`를 함께 사용합니다.

이 fixture는 모델 기반 실제 routing 평가의 계약입니다. JSON parsing은 fixture 구조만
확인하며 실제 skill selection을 증명하지 않습니다. 모델 평가에는 model, 비용, 반복 횟수와
외부 mutation 범위를 별도로 승인받아야 합니다. 실행하지 않은 case는 `not_run`으로 보고합니다.
