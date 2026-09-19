# Tool routing

대상 저장소의 instruction, framework, component library, semantic tokens, Storybook, test script,
browser/e2e harness와 accessibility tooling을 먼저 찾는다. 플러그인 계약을 맞추기 위해 dependency를
임의로 추가하지 않는다.

- 구조·코드 탐색: 저장소 기본 도구와 `rg`
- 결정적 검증: 기존 lint, typecheck, unit/integration, build
- rendered state: 실제 앱 또는 기존 Storybook
- interaction: 기존 Playwright/Cypress 또는 사용 가능한 browser/computer-use
- 접근성: 기존 자동 검사와 keyboard·semantics·contrast의 실제 관찰
- Figma: 사용자가 명시했고 official capability가 있을 때만

runtime이 없으면 DQ7은 `not_run` 또는 `blocked`다. 정적 HTML, markdown, schema parse로 실제 앱
실행을 통과시키지 않는다.
