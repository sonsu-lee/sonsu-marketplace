---
name: figma-prototype-flow
description: Figma Design에서 버튼 navigation, modal·drawer·popover, component state, 조건 분기 또는 실제 클릭 가능한 prototype reaction을 생성·수정하고 검증해야 할 때 사용한다. 기존 flow의 읽기 전용 검토, 화면 visual layout만 만드는 작업, FigJam journey, draw.io 시스템 구조도와 Figma-to-code에는 사용하지 않는다.
---

# Figma prototype flow

Figma Design이 제품 interaction의 source of truth일 때 actual control과 native reaction을 연결한다. Executable reaction, 사람이 읽는 annotation, named state topology는 서로 대체하지 않는 세 evidence layer다.

## 작업 연속성

현재 메인 controller가 여러 단계의 작업을 소유하거나 외부 쓰기를 수행할 때에는 같은 플러그인의
[task-continuity](../task-continuity/SKILL.md)를 적용해 시작·중요한 진행 변화·외부 쓰기 전후를 기록한다.
컴팩션·재개 후에는 그 기록과 현재 근거를 대조한다. 짧은 단발 작업, 위임된 subagent와 fresh reviewer는
별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 변경하지 않는다.

## 시작과 실행 선택

1. [tool routing](../../references/tool-routing.md)으로 실제 제품 interaction인지 확인한다. overlay, back/dismiss, error/recovery와 state edge case는 Figma prototype 안에서 정의한다. FigJam과 draw.io diagram은 이를 대체하지 않는다.
2. [capability and evidence](../../references/capability-and-evidence.md)를 읽어 target, permission과 `reaction_write`, `reaction_readback`, `prototype_playback` capability를 각각 기록한다. reaction read/write 전에는 호스트별 공식 Figma prerequisite를 적용한다. motion 등 추가 prerequisite도 현재 설치된 contract가 요구할 때 함께 따른다.
3. 판단형 reaction read/write는 registered official Figma MCP를 유일한 agent writer로 사용한다. direct official MCP와 explicit target을 좁힌 bounded code 모두 official MCP 경로 안에 한정한다. raw MCP, local bridge, second writer 또는 추정한 API 이름을 사용하지 않는다.
4. existing starting point, screen·component states, reactions, variables와 annotations를 읽어 현재 graph를 만든다. Selection이나 node ID가 stale하면 write 전에 정확한 target을 다시 정한다.
5. 기존 Design Decision Contract가 있으면 같은 revision을 사용하고, 없으면
   [공통 디자인 품질 계약](../../references/design-quality.md)으로 사용자 과업·오판 비용·상태·환경과
   prototype scenario를 잠근다. reaction을 보기 좋게 연결하는 것보다 observable success와 recovery를 우선한다.

공식 Figma prerequisite 또는 필요한 capability가 설치·노출되지 않으면 interaction specification을 제공하고 mutation과 playback을 `blocked`, `not_run` 또는 `inconclusive`로 보고한다. tool/API를 추정하거나 우회하지 않는다. companion은 prototype graph를 write하는 도구가 아니다. 수동 companion의 `audit-prototype-links`는 selection 기반의 결정적 integrity evidence만 제공하며 자세한 계약은 [deterministic execution](../../references/deterministic-execution.md)과 [companion README](../../figma-plugin/README.md)를 따른다.

## Interaction 계약

[interaction specification](../../references/interaction-spec.md)의 필드를 각 중요한 transition에 적용한다. 화면 수준 결과는 별도 frame, 반복되는 local state는 이해 가능한 component variant 또는 variable로 표현한다. actual control에 목적에 맞는 native action을 연결하고 overlay dismissal, cancel/back, error와 recovery, loading과 edge case를 포함한다.

같은 prototype graph, 연결된 state frame 또는 selection/current-page context를 수정하는 writer는 하나만 둔다. 다른 작업이 screen structure를 준비했다면 reaction 적용 직전에 최신 node와 destination을 다시 읽고 component·variable·prototype dependency가 겹치면 직렬화하거나 중단한다. annotation은 `Trigger → Result [Condition]` 형식으로 readable하게 남긴다.

## 검증과 결과

readback capability가 있으면 reaction을 다시 읽어 trigger, action, destination, overlay dismissal과 back behavior를 확인한다. playback capability가 있으면 named starting point에서 primary, failure와 recovery path를 실행해 unreachable frame, dead end, 닫히지 않는 overlay와 잘못된 Back을 찾는다. Screenshot은 visible state만, reaction readback은 graph만 증명하므로 둘을 함께 기록한다.

결과에는 starting point, 검증한 path, unresolved branch, annotation coverage와 evidence 상태를 기록한다. reaction write는 성공했지만 destination readback이 실패하거나 지원되지 않으면 해당 path는 `inconclusive`다. write와 readback이 성공해도 playback이 unsupported이면 playback은 `not_run`, 전체 clickable 결과는 `inconclusive`다. live MCP·Desktop 실행을 하지 않은 경우 passed라고 주장하지 않는다.

prototype을 포함한 Figma 산출물은 DQ0–DQ7 report로 판정한다. DQ1–DQ6은 독립 평가자 2명이
평가하고 DQ7은 screenshot, native reaction readback과 요청된 playback의 상태를 분리한다.

## 예시

“Pay를 누르면 확인 modal이 열리고 Confirm 후 성공 또는 오류로 나뉘게 해 줘”라는 요청에서는 Pay에 overlay reaction, modal에 close/cancel, Confirm에 submitting과 결과 branch를 연결한다. 각 transition의 조건과 visible result를 annotation에 남기고 starting point부터 success와 error recovery를 검증한다.
