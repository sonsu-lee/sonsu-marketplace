# Upstream and source notes

## Status

- Plugin version: `0.1.0`
- Source model: locally authored, multi-source guidance
- External files copied: none
- License: not declared; decide before public distribution
- Last reviewed: 2026-09-04

이 plugin은 외부 skill이나 문서를 파일 단위로 가져온 fork가 아닙니다. official tool contract와 공개 실무 자료에서 확인한 개념을 Sonsu Marketplace의 독립 plugin 정책에 맞게 새로 작성했습니다. 원문의 문장, code, asset을 복사하지 않습니다.

## Consulted authoritative sources

### Figma

- Figma MCP Server: <https://developers.figma.com/docs/figma-mcp-server/>
- Tools and prompts: <https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/>
- Write to the canvas: <https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/>
- Create skills: <https://developers.figma.com/docs/figma-mcp-server/create-skills/>
- Auto Layout: <https://help.figma.com/hc/en-us/articles/360040451373-Explore-auto-layout-properties>
- Auto Layout and CSS Flexbox: <https://help.figma.com/hc/en-us/articles/42031586813719-Use-auto-layout-with-CSS-Flexbox-in-mind>
- Grid Auto Layout: <https://help.figma.com/hc/en-us/articles/31289469907863-Use-the-grid-auto-layout-flow>
- Component properties: <https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties>
- Slots, instance swaps and variants: <https://help.figma.com/hc/en-us/articles/38741465279895-The-difference-between-slots-instance-swaps-and-variants>
- Variables: <https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes>
- Prototype flows: <https://help.figma.com/hc/en-us/articles/360039823894-Create-and-manage-prototype-flows>
- Dev Mode: <https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode>
- MCP Server Guide snapshot: <https://github.com/figma/mcp-server-guide/tree/ae7e5e5f80da20f1dd7445e0c6ae5ac58a5b0bce>

Figma source는 behavior와 capability fact 확인에만 consulted했다. bundled official plugin의 license는 `LicenseRef-Figma-Developer-Terms`로 식별되지만, 이 plugin에는 Figma skill text나 code가 복사되지 않았다. current connected schema와 required prerequisite가 문서보다 실제 tool 실행의 우선 근거다.

### OpenAI Codex

- Codex models: <https://developers.openai.com/codex/models/>
- Codex configuration: <https://developers.openai.com/codex/config-reference/>

model role과 availability는 time-sensitive다. 이 plugin은 일반 model recommendation을 Figma benchmark claim으로 바꾸지 않으며 session model을 자동 변경하지 않는다.

## Consulted practitioner sources

다음 source는 example, counterexample과 evaluation case를 위해 consulted했으며 dependency나 imported content가 아니다.

- Joey Banks, Auto Layout: <https://newsletter.baselinedesign.com/baseline-25-using-auto-layout-in-figma/>
- Joey Banks, Constraints: <https://newsletter.baselinedesign.com/baseline-23-using-constraints-in-figma/>
- Joey Banks, variables: <https://www.baselinedesign.com/posts/baseline-22-how-i-organize-variables-in-figma>
- Joey Banks, multi-edit: <https://www.baselinedesign.com/posts/baseline-16-everything-to-know-about-multi-editing-in-figma>
- Zeplin, when not to use Auto Layout: <https://blog.zeplin.io/collaboration/when-and-when-not-to-use-auto-layout-in-figma/>
- Brenno Pellegrini, iconography: <https://brennopellegrini.com/articles/iconography/>
- Alima prototype-to-Figma snapshot: <https://github.com/alima-max/prototype-to-figma-skill/tree/6e2e1bef74f33450804da0799640a388c772351d>
- Owl Listener designer skills snapshot: <https://github.com/Owl-Listener/designer-skills/tree/20e34c492474534327494e3b8f75ad1d9d43e4d3>

repository popularity, stars와 issue count는 quality proof로 취급하지 않는다. current provider documentation과 actual connected tool schema가 community example보다 우선한다.
