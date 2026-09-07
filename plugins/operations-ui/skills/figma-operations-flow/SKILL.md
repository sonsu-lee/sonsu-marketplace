---
name: figma-operations-flow
description: 사용자가 Figma를 명시해 운영형 B2B 화면, 상태, overlay와 clickable prototype을 Screen Contract에 연결하고 구현 handoff를 만들라고 요청했을 때만 사용한다. Figma를 언급하지 않은 code-first 설계·재설계, 읽기 전용 코드 감사, marketing design 또는 Figma design-to-code 구현에는 사용하지 않는다.
---

# Figma Operations Flow

Figma가 명시된 운영 화면 요청에만 선택적으로 사용한다. 이 스킬이나 `figma-workflow`가 설치되지 않아도 operations-ui의 code-first 흐름은 독립적으로 동작한다.

## 시작

1. [figma contract](../../references/figma-contract.md)와 [screen contract](../../references/screen-contract.md)을 읽는다.
2. 사용자가 원하는 최종 Figma artifact와 target file/page/selection을 확인한다.
3. 현재 설치된 official Figma skill/tool의 prerequisite를 읽고 실제 capability와 edit permission을 확인한다.

capability가 없을 때 tool 이름을 추정하거나 대체 writer를 만들지 않는다. Figma가 필수 deliverable이면 `blocked`, 선택 사항이면 mutation을 `not_run`으로 보고하고 Screen Contract 기반 specification만 제공한다.

## Figma 작업

capability가 있으면 현재 official Figma 계약과 설치된 `figma-workflow`의 applicable skill을 따른다.

- native Auto Layout은 content/resize intent에 따라 one-axis, wrap 또는 2D grid를 선택한다.
- reusable component, semantic variable, exact icon과 accessible name을 사용한다.
- loading, empty, error, permission, long data와 action feedback state를 frame 또는 variant로 만든다.
- 실제 prototype reaction과 starting point를 연결한다.
- 모든 frame, state와 reaction에 Screen Contract scenario ID를 annotation한다.

## handoff와 종료

Figma node/layout/reaction readback, token mapping, breakpoint/overflow와 icon provenance를 handoff에 남긴다. 이후 `design-operations-ui` 또는 `redesign-operations-ui`의 code implementation으로 돌아간다.

Figma screenshot, node readback이나 prototype playback은 G7 Browser Runtime Evidence를 대체하지 않는다. 실제 target app의 browser gate가 끝나기 전에는 `overall: passed`를 보고하지 않는다.
