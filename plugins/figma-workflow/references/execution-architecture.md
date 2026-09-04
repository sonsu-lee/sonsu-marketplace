# Execution architecture

이 문서는 design policy와 execution configuration을 구분한다. model catalog와 provider schema는 시간에 따라
바뀌므로 live task 전에 재확인한다.

| layer | 책임 | 소유하지 않는 것 |
| --- | --- | --- |
| design skill | routing, quality contract, evidence, stop condition | model 변경, provider 설치 |
| Codex profile | 사용자가 고른 model/reasoning effort | artifact permission |
| official Figma MCP | current Figma context와 native canvas I/O | product policy, unsupported claim |
| Desktop companion | allowlisted deterministic transformation/audit | open-ended design judgment, agent write |

skill은 session model이나 reasoning effort를 조용히 바꾸지 않는다. 판단형 canvas 작업의 agent writer는
official Figma MCP 하나이며, concurrent write는 [capability and evidence](capability-and-evidence.md)의 conflict
domain rule을 따른다. Desktop companion은 사용자가 직접 실행하는 별도 tool이다.

local companion은 반복 빈도가 있고, input·target·unchanged area·output을 결정적으로 검증할 수 있으며,
preview와 bounded failure/readback이 가능한 작업에만 후보가 된다. open-ended layout, UX judgment, visual direction,
reaction graph write는 official Figma workflow에 남긴다. 현재 companion의 허용 범위는
[deterministic execution](deterministic-execution.md)과 package README가 정한 operation뿐이다.

model/effort, multiple agent, live mutation scope, target file과 cleanup은 각각 사용자 승인 또는 현재 session의
명시된 authority가 필요하다. 이러한 live 비교·Desktop 실행을 실제로 하지 않았다면 결과는 `not_run`이다.
