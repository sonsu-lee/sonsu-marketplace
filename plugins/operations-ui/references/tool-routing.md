# Tool routing

## 먼저 대상 저장소를 읽는다

repo instructions, framework, design tokens, component library, Storybook, test scripts, browser/e2e harness와 accessibility tooling을 찾는다. 기존 도구가 있으면 그 경로를 우선 사용한다. 이 플러그인을 위해 dependency를 임의로 추가하지 않는다.

## 용도별 선택

- 파일과 코드 탐색: 저장소의 기본 도구와 `rg`
- deterministic verification: 기존 lint, typecheck, unit/integration, build script
- rendered state: 기존 Storybook 또는 실제 local app
- interaction/browser receipt: 기존 Playwright/Cypress/browser automation 또는 사용 가능한 computer-use/browser 도구
- accessibility: 기존 axe 계열 tooling, browser semantics 또는 명시적인 수동 keyboard/contrast 기록
- 이미지 생성: 제품 데이터 구조와 무관한 장식 asset이 명시적으로 필요한 경우에만 별도 이미지 도구

## Figma 경계

Figma는 사용자가 명시했을 때만 [figma-contract.md](figma-contract.md)를 적용한다. 연결된 official capability와 그 prerequisite를 실제 노출된 schema로 확인한다. 설치되지 않은 Figma 또는 `figma-workflow`를 core dependency로 가정하지 않는다. Figma가 없어도 code-first 설계, 재설계와 감사 계약은 그대로 동작한다.

## 증거 경계

browser tool이 없거나 target app을 실행할 수 없으면 G7은 `not_run` 또는 `blocked`다. static HTML, markdown, schema validation만으로 G7을 통과시키지 않는다. native Codex loader나 model routing 평가를 실행할 수 없으면 self-validation 결과에도 `not_run`으로 분리한다.
