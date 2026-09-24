# Upstream and source notes

## Status

- Plugin version: `0.4.0`
- Source model: locally authored, multi-source guidance
- External files copied: none
- License: not declared; decide before public distribution
- Last reviewed: 2026-09-17

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

### 화면 구성과 동선 보완 (2026-09-11)

designbywani의 릴스 캡션에서 다음 주제를 확인하고 기존 layout·text·interaction 계약의 적용 예시로 해석했다.
영상 전체의 전사나 비공개 DM 자료를 확보한 것은 아니며 문장·프롬프트·Figma asset은 복사하지 않았다.

- [정렬·간격·강약](https://www.instagram.com/reel/Dc3CXUjzjSp/): 작업별 정보 묶음과 읽는 순서
- [텍스트 역할과 스타일](https://www.instagram.com/reel/Dcs0qmTT4u1/): 필요한 역할을 기존 Text Style에 매핑
- [중첩 카드 모서리](https://www.instagram.com/reel/DdEBHpTT_ys/): surface 관계를 검토한 practitioner 사례
- [PRD에서 화면 동선으로](https://www.instagram.com/reel/Dcx5VQ-TbmC/): 목표·화면·권한을 기존 transition에 대응

[Atlassian spacing](https://atlassian.design/foundations/spacing/)의 semantic grouping·proximity와
[WCAG text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)로 간격·대비 해석을 대조했다.
surface와 control의 corner는 기존 component/token과 역할에서 판단하며 하나의 산식을 보편 규칙으로
사용하지 않는다. social tip은 새 차단 gate나 고정 style scale로 승격하지 않는다.

2026-09-17부터 [공통 source map](references/design-quality-sources.md)의 근거 계층과 DQ0–DQ8을
사용한다. Figma 범위는 DQ0–DQ7이며 production runtime·live 사용자 결과와 분리한다. Madia
Designer 공개 영상은 별도 연구 카탈로그에서 직접 관찰·반복·외부 근거·행동 평가를 충족하기 전까지
Figma 차단 규칙으로 사용하지 않는다.
