# Execution workflow

## 신규 설계

```text
inspect target repository
if request is not operational/admin/data-work UI: stop as near miss
build structurally valid Screen Contract with unresolved areas recorded
hold only tasks depending on unresolved areas; clarify unknown impact boundaries
select one primary screen pattern
map every requirement, action, permission, risk and view state to evidence scenarios
implement actual states in the existing stack
run deterministic checks
collect Browser Evidence Receipts
evaluate G0..G7
while a required gate failed and repair is actionable and task repair attempts < 5:
  route contract gaps to Screen Contract
  route IA/visual/layout gaps to design mapping
  route state/interaction/runtime gaps to implementation
  route missing evidence to browser collection
  fix and rerun affected plus regression scenarios
return passed only when every required gate is passed
otherwise return remaining failures, blocked dependencies and valid partial evidence
```

## 재설계

```text
inventory current feature/state/action/permission/data-shape
assign preserve or change to every inventory id
hold inventory items with missing decisions/evidence and their dependent tasks
build Change Contract
map every inventory id to implementation target and browser scenario
validate ready independent scope without discarding unresolved full inventory
implement approved changes
run preserved and new browser scenarios
if preserved behavior regresses: failed -> inventory/mapping or implementation owner
evaluate G0..G7 using the same completion rule
```

## 읽기 전용 감사

감사는 file, DOM, rendered visual 읽기와 scroll, focus, route/tab 이동처럼 application data를 바꾸지 않는 navigation만 허용한다. submit, create/update/delete, persisted toggle, test-data creation은 하지 않는다. 상태 변경이 필요한 검사는 `not_run` 또는 `inconclusive`로 남긴다. 결과는 finding과 Quality Report이며 대상 코드를 수정하지 않는다.

## 선택형 Figma

사용자가 Figma를 명시하지 않으면 Figma 단계는 적용하지 않는다. 명시했고 official capability가 있으면 현재 설치된 Figma prerequisite를 따라 Screen Contract scenario와 native frame, component, state, reaction을 연결한다. capability가 없으면 Figma가 필수 artifact일 때 `blocked`, 선택 사항일 때 `not_run`으로 보고하고 specification만 제공한다. 이후에도 code implementation과 Browser Gate를 거쳐야 한다.

## 반환 경로

| 실패 | 돌아갈 단계 |
| --- | --- |
| 요구사항, 권한, 상태 결정 누락 | Screen Contract |
| pattern, hierarchy, token, density 문제 | design mapping |
| state, action, runtime 동작 문제 | implementation |
| screenshot, trace, console 결과 누락 | browser evidence collection |
| Figma structure/reaction 문제 | optional Figma flow |

### 재시도와 종료

같은 논리 작업의 자동 수정·재검증은 누적 최대 5회다. 조정자는 기존 작업 기록에 작업 ID,
소비 횟수와 남은 횟수를 유지하고, 다른 스킬·에이전트·세션·부분 계약으로 전환해도 초기화하지
않는다. 상위 작업이 더 엄격한 상한을 이미 정했다면 그 남은 예산을 따른다. 이 계약은 조정자의
실행 규칙이며 JSON validator가 실제 시도 횟수나 에이전트 실행을 강제하는 것은 아니다.

같은 원인이 반복되면 증거를 유지한 채 소유 단계에서 원인을 다시 판단한다. 새 근거나 다른
해결 전략이 없으면 같은 호출을 반복하지 않는다. 필수 제품 결정·권한·실행 환경이 없으면 해당
작업을 `blocked` 또는 `not_run`으로 남기고 독립적으로 가능한 작업만 계속한다. 상한에 도달하면
유효한 결과, 미해결 항목, 실패 근거와 필요한 다음 결정을 보고한다. 상한 도달을 통과로 바꾸거나
게이트를 완화하지 않는다. 영향이 없는 기존 근거를 재수집하는 형식적 반복은 하지 않는다.
