# Optional Figma contract

Figma는 사용자가 명시한 경우에만 적용한다. current host가 실제 노출한 Figma MCP/plugin capability,
provider prerequisite와 write permission을 먼저 확인한다. Codex 전용 skill ID는 실제 노출된 경우에만
적용한다. capability가 없으면 필수 Figma 산출물은 `blocked`, 선택 작업은 `not_run`으로 남기고
API나 다른 writer를 추정하지 않는다.

- contract의 scenario ID를 frame, state, component/variant, 요청된 reaction에 연결한다.
- content와 resize intent에 따라 Auto Layout, wrap 또는 grid를 선택한다.
- 제품 디자인 시스템의 component와 semantic variable을 재사용한다.
- contract상 적용되는 상태와 긴 데이터·현지화·overflow를 만든다.
- prototype을 요청했으면 실제 reaction, starting point와 playback을 확인한다.
- DQ7 근거로 node/layout/variable/reaction readback과 resize 결과를 남긴다.

Figma DQ7 통과는 implementation DQ7이나 live DQ8 통과가 아니다.
