---
name: figma-operations-flow
description: 사용자가 Figma를 명시한 운영형 B2B 화면·상태·overlay·prototype 제작 요청에 사용한다. Figma 없는 코드 구현·읽기 전용 코드 감사·단순 변환에는 자동 선택하지 않는다.
---

# Figma Operations Flow

[공통 디자인 품질 계약](../../references/design-quality.md), [Figma 계약](../../references/figma-contract.md)과
current host가 실제 노출한 Figma MCP/plugin capability와 prerequisite를 먼저 읽는다.
`artifact_scope: figma`인 Design Decision Contract를 작성해 사용자 과업·정보·상태·환경과
native frame/component/variable/reaction을 같은 scenario ID로 연결한다.

- 제품 library의 component와 semantic variable을 우선 사용한다.
- content/resize intent에 맞는 Auto Layout, wrap 또는 grid를 선택한다.
- 계약에 적용되는 상태, 긴 현지화 데이터, overflow와 action feedback을 만든다.
- 요청된 prototype은 실제 reaction, starting point와 playback으로 확인한다.
- node/layout/variable/reaction readback과 resize 결과로 DQ7을 판정한다.
- DQ1–DQ6에는 같은 artifact/contract evaluator run이 최소 하나 필요하며 여러 run이면 최솟값과 divergence를 보존한다.

capability가 없으면 필수 Figma 산출물은 `blocked`, 선택 작업은 `not_run`으로 보고한다. Figma
결과를 browser runtime 또는 live 사용자 성과 증거로 표현하지 않는다.
