# Figma Workflow 라우팅 평가

`cases.json`은 Figma Workflow와 공식 Figma·FigJam, draw.io가 함께 있거나 일부만 있는 환경에서
요청의 최종 artifact에 맞는 스킬과 도구가 선택되는지 정의합니다.

핵심 경계는 다음과 같습니다.

- 제품 화면, native component·variable와 Auto Layout은 `figma-workflow:figma-product-design`, actual
  reaction과 clickable interaction은 `figma-workflow:figma-prototype-flow`가 Figma Design 안에서 다룹니다.
- 기존 Figma artifact의 읽기 전용 구조·품질 검토는 `figma-workflow:figma-design-audit`가 담당합니다.
- Figma canvas의 agent writer는 registered official MCP 하나이며 실제 `use_figma`에는
  `figma:figma-use` prerequisite가 필요합니다.
- 협업용 초기 journey와 workshop board는 FigJam, AWS·network·UML·ERD와 system architecture는 draw.io가
  담당합니다.
- Figma Desktop companion은 사용자가 직접 실행하며 agent-callable tool이나 fallback writer가 아닙니다.

이 fixture는 모델 기반 routing 평가의 계약입니다. JSON parsing은 fixture 구조만 확인하며 실제 skill
selection이나 canvas 동작을 증명하지 않습니다. 실행하지 않은 case는 `not_run`으로 보고합니다.
