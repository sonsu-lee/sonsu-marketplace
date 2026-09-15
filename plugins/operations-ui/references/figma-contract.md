# Optional Figma contract

이 계약은 사용자가 Figma 결과물을 명시한 경우에만 적용한다. code-first 작업의 암묵적 선행 단계가 아니다.

## capability

현재 설치된 official Figma skill과 tool의 prerequisite를 먼저 읽는다. write capability가 없으면 tool/API 이름을 추정하지 않는다. Figma가 필수 deliverable이면 해당 산출물을 `blocked`, 선택 deliverable이면 mutation을 `not_run`으로 보고하고 현재 명세를 제공한다. 독립적으로 가능한 승인 작업은 계속하되 Figma 완료로 보고하지 않는다.

## native 구조

- content와 resize intent에 따라 one-axis flow, wrap 또는 2D grid를 선택한다.
- 반복되는 운영 pattern은 component와 semantic variable로 만든다.
- icon은 exact component/asset, accessible name과 intended size를 확인한다.
- 실제 과업에 해당하는 loading, empty, error, permission과 action feedback state를 별도 frame/variant로 표현한다.
- 요청된 interaction은 실제 prototype reaction, starting point와 annotation으로 연결한다.

## handoff

각 Figma frame/state/reaction은 업무 명세의 scenario ID를 가져야 한다. Figma-only는 실행용 Screen Contract JSON이 필요하지 않다. 구현에 필요한 flex/grid intent, overflow, breakpoint, token mapping과 icon provenance를 남긴다.

Figma-only는 native 구조·화면·resize와 요청된 reaction/playback을 확인하고 끝낸다. 운영형 웹 구현도 요청했으면 실행용 Screen Contract로 연결하고 실제 browser에서 G0–G7을 판정한다. 일반 UI·네이티브 구현은 [산출물 경계](delivery.md)의 해당 프로젝트·실행 검증 경로로 이어 간다. Figma 검증을 코드 실행 검증으로, 일반 UI 검증을 운영형 Quality Report 통과로 표현하지 않는다.
