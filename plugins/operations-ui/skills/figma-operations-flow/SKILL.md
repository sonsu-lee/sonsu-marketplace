---
name: figma-operations-flow
description: Figma를 명시한 운영형 B2B 화면·상태·overlay·prototype 제작 요청에서 자동 선택한다. 직접 호출과 Operations UI의 일반 UI 경로에서 조합하는 Figma 제작도 지원하며, 산출물과 업무 유형에 맞춰 인계한다. Figma 없는 코드 작업·읽기 전용 코드 감사·코드 변환만의 요청에는 자동 선택하지 않는다.
---

# Figma Operations Flow

Figma가 명시된 요청에서 사용한다. 직접 호출과 일반 UI 조합에는 산출물 경계의 해당 경로를 적용한다. `figma-workflow`가 없어도 현재 Figma capability와 아래 제작 기준으로 수행한다.

## 시작

1. [산출물 경계](../../references/delivery.md)와 [figma contract](../../references/figma-contract.md)을 읽어 업무 유형과 산출물을 구분한다. Figma는 짧은 명세와 안정적인 scenario ID를 사용한다. 운영형 웹 구현도 요청한 경우에만 [screen contract](../../references/screen-contract.md)의 실행용 JSON을 완성한다.
2. 사용자가 원하는 최종 Figma artifact와 target file/page/selection을 확인한다.
3. 현재 설치된 official Figma skill/tool의 prerequisite를 읽고 실제 capability와 edit permission을 확인한다.

capability가 없을 때 tool 이름을 추정하거나 대체 writer를 만들지 않는다. Figma가 필수 deliverable이면 해당 산출물을 `blocked`, 선택 사항이면 mutation을 `not_run`으로 보고하고 현재 명세를 제공한다. Figma에 의존하지 않는 승인된 작업은 계속할 수 있으며 Figma 완료로 보고하지 않는다.

## Figma 작업

capability가 있으면 현재 official Figma 계약을 따르고, `figma-workflow`가 설치되어 있으면 applicable skill을 함께 적용한다. 없어도 현재 도구의 필수 선행 지침과 아래 기준으로 제작한다.

- native Auto Layout은 content/resize intent에 따라 one-axis, wrap 또는 2D grid를 선택한다.
- reusable component, semantic variable, exact icon과 accessible name을 사용한다.
- 실제 과업에 해당하는 loading, empty, error, permission, long data와 action feedback state를 frame 또는 variant로 만든다.
- prototype을 요청했으면 실제 reaction과 starting point를 연결하고 playback을 확인한다.
- 모든 frame, state와 요청된 reaction에 업무 명세의 안정적인 scenario ID를 annotation한다. 운영형 웹 구현도 요청하면 실행용 Screen Contract에 같은 ID를 연결한다.

## handoff와 종료

Figma node/layout/reaction readback, token mapping, breakpoint/overflow와 icon provenance를 handoff에 남긴다. Figma만 요청했으면 해당 디자인·요청된 prototype의 결과와 미확인을 보고하고 끝낸다. 운영형 웹 구현도 요청했으면 실행용 Screen Contract로 연결한다. 일반 UI나 네이티브 구현은 [산출물 경계](../../references/delivery.md)의 해당 구현·검증 경로로 인계한다.

Figma screenshot, node readback이나 prototype playback은 실제 코드 실행 검증을 대체하지 않는다. 운영형 웹 구현은 actual target app의 G0–G7을 모두 마친 뒤에만 운영형 Quality Report의 `overall: passed`를 보고한다. Figma-only·일반 UI·네이티브 산출물은 각각 실제 확인한 범위와 미확인을 보고하며 운영형 validator 통과로 표현하지 않는다.
