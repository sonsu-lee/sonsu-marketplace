# Design tool routing

최종 artifact를 소유할 product를 먼저 고른다. 사용할 수 있는 tool이 있다는 이유로 다른 product로
작업을 옮기지 않는다.

| 작업 | 정본 product | 보조 수단 | 피할 것 |
| --- | --- | --- | --- |
| 제품 화면, responsive layout, visual state | Figma Design | official Figma MCP와 품질 계약 | draw.io 또는 FigJam을 최종 화면으로 쓰기 |
| 버튼 navigation, modal·drawer·popover, state flow | Figma Design | `figma-prototype-flow`, native reactions | static arrow만으로 클릭 가능하다고 주장하기 |
| 초기 journey 탐색과 workshop | FigJam | 현재 환경의 official FigJam capability | 제품 prototype의 정본으로 쓰기 |
| AWS, network, UML, ERD, service/data flow | draw.io | architecture icon library와 native `.drawio` | Figma product frame으로 구조도 대체하기 |
| component/library authoring | Figma Design | `figma:figma-generate-library` | 화면 작업 중 무단 library API 변경 |
| Figma-to-code | Figma Design | `figma:figma-design-to-code` | 화면 설계 skill이 code implementation을 대신하기 |
| 반복적인 exact rename, icon swap, selection audit | 수동 Desktop companion | versioned allowlist JSON | companion을 agent writer나 general canvas editor로 쓰기 |

Figma 제품 화면과 prototype은 Figma 안에서 완결한다. FigJam board와 draw.io diagram은 각각 탐색과
시스템 설명의 deliverable이며 reaction, overlay, state와 interaction evidence를 대체하지 않는다.

화면·composed view 작업에서는 local quality skill과 현재 환경의 official Figma workflow를 함께 사용한다.
official tool 전 required prerequisite skill이 설치되어 있으면 반드시 먼저 따른다. live schema가 cached
문서와 다르면 현재 schema만 capability 근거로 사용하고 tool/API 이름을 추정하지 않는다. 실행 경계와
companion contract는 [deterministic execution](deterministic-execution.md)을 읽는다.
