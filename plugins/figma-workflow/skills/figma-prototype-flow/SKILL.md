---
name: figma-prototype-flow
description: Figma Design에서 버튼 navigation, modal·drawer·popover, component state, 조건 분기 또는 실제 클릭 가능한 prototype reaction을 생성·수정하고 검증해야 할 때 사용한다. 기존 flow의 읽기 전용 검토, 화면 visual layout만 만드는 작업, FigJam journey, draw.io 시스템 구조도와 Figma-to-code에는 사용하지 않는다.
---

# Figma prototype flow

Figma Design이 제품 interaction의 source of truth일 때 actual control과 native reaction을 연결한다. Executable reaction, 사람이 읽는 annotation, named state topology는 서로 대체하지 않는 세 evidence layer다.

## 시작과 실행 선택

1. [tool routing](../../references/tool-routing.md)으로 실제 제품 interaction인지 확인한다. overlay, back/dismiss, error/recovery와 state edge case는 Figma prototype 안에서 정의한다. FigJam과 draw.io diagram은 이를 대체하지 않는다.
2. [capability and evidence](../../references/capability-and-evidence.md)를 읽어 target, permission과 `reaction_write`, `reaction_readback`, `prototype_playback` capability를 각각 기록한다. provider가 Figma tool 전에 prerequisite skill을 요구하고 그것이 설치되어 있으면 현재 계약을 먼저 따른다.
3. 판단형 reaction read/write는 registered official Figma MCP를 유일한 agent writer로 사용한다. direct official MCP와 explicit target을 좁힌 bounded code 모두 official MCP 경로 안에 한정한다. raw MCP, local bridge, second writer 또는 추정한 API 이름을 사용하지 않는다.
4. existing starting point, screen·component states, reactions, variables와 annotations를 읽어 현재 graph를 만든다. Selection이나 node ID가 stale하면 write 전에 정확한 target을 다시 정한다.

reaction write capability가 없으면 interaction specification을 제공하고 mutation과 playback을 `not_run`으로 보고한다. companion은 prototype graph를 write하는 도구가 아니다. 수동 companion의 `audit-prototype-links`는 selection 기반의 결정적 integrity evidence만 제공하며 자세한 계약은 [deterministic execution](../../references/deterministic-execution.md)과 [companion README](../../figma-plugin/README.md)를 따른다.

## Interaction 계약

[interaction specification](../../references/interaction-spec.md)의 필드를 각 중요한 transition에 적용한다. 화면 수준 결과는 별도 frame, 반복되는 local state는 이해 가능한 component variant 또는 variable로 표현한다. actual control에 목적에 맞는 native action을 연결하고 overlay dismissal, cancel/back, error와 recovery, loading과 edge case를 포함한다.

같은 prototype graph, 연결된 state frame 또는 selection/current-page context를 수정하는 writer는 하나만 둔다. 다른 작업이 screen structure를 준비했다면 reaction 적용 직전에 최신 node와 destination을 다시 읽고 component·variable·prototype dependency가 겹치면 직렬화하거나 중단한다. annotation은 `Trigger → Result [Condition]` 형식으로 readable하게 남긴다.

## 검증과 결과

readback capability가 있으면 reaction을 다시 읽어 trigger, action, destination, overlay dismissal과 back behavior를 확인한다. playback capability가 있으면 named starting point에서 primary, failure와 recovery path를 실행해 unreachable frame, dead end, 닫히지 않는 overlay와 잘못된 Back을 찾는다. Screenshot은 visible state만, reaction readback은 graph만 증명하므로 둘을 함께 기록한다.

결과에는 starting point, 검증한 path, unresolved branch, annotation coverage와 evidence 상태를 기록한다. reaction write는 성공했지만 destination readback이 실패하거나 지원되지 않으면 해당 path는 `inconclusive`다. write와 readback이 성공해도 playback이 unsupported이면 playback은 `not_run`, 전체 clickable 결과는 `inconclusive`다. live MCP·Desktop 실행을 하지 않은 경우 passed라고 주장하지 않는다.

## 예시

“Pay를 누르면 확인 modal이 열리고 Confirm 후 성공 또는 오류로 나뉘게 해 줘”라는 요청에서는 Pay에 overlay reaction, modal에 close/cancel, Confirm에 submitting과 결과 branch를 연결한다. 각 transition의 조건과 visible result를 annotation에 남기고 starting point부터 success와 error recovery를 검증한다.
