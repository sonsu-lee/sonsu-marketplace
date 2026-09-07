# Optional Figma contract

이 계약은 사용자가 Figma 결과물을 명시한 경우에만 적용한다. code-first 작업의 암묵적 선행 단계가 아니다.

## capability

현재 설치된 official Figma skill과 tool의 prerequisite를 먼저 읽는다. write capability가 없으면 tool/API 이름을 추정하지 않는다. Figma가 필수 deliverable이면 `blocked`, 선택 deliverable이면 mutation을 `not_run`으로 보고하고 Screen Contract 기반 specification만 제공한다.

## native 구조

- content와 resize intent에 따라 one-axis flow, wrap 또는 2D grid를 선택한다.
- 반복되는 운영 pattern은 component와 semantic variable로 만든다.
- icon은 exact component/asset, accessible name과 intended size를 확인한다.
- loading, empty, error, permission과 action feedback state를 별도 frame/variant로 표현한다.
- interaction은 실제 prototype reaction, starting point와 annotation으로 연결한다.

## handoff

각 Figma frame/state/reaction은 Screen Contract scenario ID를 가져야 한다. 구현에 필요한 flex/grid intent, overflow, breakpoint, token mapping과 icon provenance를 남긴다.

Figma readback이 통과해도 code implementation으로 돌아가 실제 browser에서 G0–G7을 판정한다. Figma screenshot이나 prototype playback은 G7 Browser Runtime Evidence가 아니다.
