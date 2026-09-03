# Upstream and source notes

## Status

- Plugin version: `0.1.0`
- Source model: locally authored, multi-source guidance
- External files copied: none
- License: not declared; decide before public distribution
- Last reviewed: 2026-09-03

이 플러그인은 외부 skill이나 문서를 파일 단위로 가져온 fork가 아닙니다. 공식 tool contract와
공개된 실무 자료에서 확인한 개념을 현재 Sonsu Marketplace의 독립 plugin 정책에 맞게 새로
작성했습니다. 원문의 문장, 코드 또는 asset을 복사하지 않습니다.

## Authoritative product sources

### Figma

- Figma MCP Server: <https://developers.figma.com/docs/figma-mcp-server/>
- Tools and prompts: <https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/>
- Write to the canvas: <https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/>
- Create skills: <https://developers.figma.com/docs/figma-mcp-server/create-skills/>
- Auto Layout: <https://help.figma.com/hc/en-us/articles/360040451373-Explore-auto-layout-properties>
- Auto Layout and CSS Flexbox: <https://help.figma.com/hc/en-us/articles/42031586813719-Use-auto-layout-with-CSS-Flexbox-in-mind>
- Component properties: <https://help.figma.com/hc/en-us/articles/5579474826519-Explore-component-properties>
- Slots, instance swaps and variants: <https://help.figma.com/hc/en-us/articles/38741465279895-The-difference-between-slots-instance-swaps-and-variants>
- Variables: <https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes>
- Prototype flows: <https://help.figma.com/hc/en-us/articles/360039823894-Create-and-manage-prototype-flows>
- Dev Mode: <https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode>
- MCP Server Guide snapshot: <https://github.com/figma/mcp-server-guide/tree/ae7e5e5f80da20f1dd7445e0c6ae5ac58a5b0bce>

Figma source material is referenced for behavior and capability facts. The bundled official plugin identifies
its license as `LicenseRef-Figma-Developer-Terms`; no Figma skill text is copied into this plugin.

### Paper Design

- MCP documentation: <https://paper.design/docs/mcp>
- Tokens: <https://paper.design/docs/tokens>
- Roadmap: <https://paper.design/roadmap>
- Build log: <https://paper.design/build-log>
- Agent plugin snapshot: <https://github.com/paper-design/agent-plugins/tree/f6d4f13343dd924fabaadd0898725f1b8718459d>

The Paper agent-plugin snapshot declares `"license": "MIT"` in its plugin manifest, but the reviewed repository
root did not contain a GitHub-recognized `LICENSE` file. Treat the exact distribution license as unresolved rather
than inferring permission from the manifest field. No file from it is copied; this plugin relies on the MCP
capability available in the running environment.

### OpenAI Codex

- Codex models: <https://developers.openai.com/codex/models/>
- Codex configuration: <https://developers.openai.com/codex/config-reference/>

Model roles and availability are time-sensitive. The execution reference records the local runtime catalog seen
on 2026-09-03 and labels Figma-specific recommendations as provisional; it does not turn general model guidance
into a Figma benchmark claim.

## Practitioner and community references

The following sources informed examples, counterexamples and evaluation cases. They are references rather
than dependencies or imported content.

- Joey Banks, Auto Layout: <https://newsletter.baselinedesign.com/baseline-25-using-auto-layout-in-figma/>
- Joey Banks, Constraints: <https://newsletter.baselinedesign.com/baseline-23-using-constraints-in-figma/>
- Joey Banks, variables: <https://www.baselinedesign.com/posts/baseline-22-how-i-organize-variables-in-figma>
- Joey Banks, multi-edit: <https://www.baselinedesign.com/posts/baseline-16-everything-to-know-about-multi-editing-in-figma>
- Zeplin, when not to use Auto Layout: <https://blog.zeplin.io/collaboration/when-and-when-not-to-use-auto-layout-in-figma/>
- Brenno Pellegrini, iconography: <https://brennopellegrini.com/articles/iconography/>
- Alima prototype-to-Figma snapshot: <https://github.com/alima-max/prototype-to-figma-skill/tree/6e2e1bef74f33450804da0799640a388c772351d>
- Owl Listener designer skills snapshot: <https://github.com/Owl-Listener/designer-skills/tree/20e34c492474534327494e3b8f75ad1d9d43e4d3>
- Minoan Paper skill snapshot: <https://github.com/tdimino/claude-code-minoan/blob/712b12a7d69eeec344d6d761dba650dc8ac2416f/skills/design-media/paper-design/SKILL.md>
- Junhan Sim, Paper and Claude Code: <https://medium.com/design-bootcamp/i-tried-paper-with-claude-code-587e9a46f459>

Repository popularity, stars and issue counts are not treated as quality proof. Current provider documentation
and the actual connected tool schema take precedence over community examples.
