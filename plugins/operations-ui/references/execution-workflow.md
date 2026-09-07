# Execution workflow

## 신규 설계

```text
inspect target repository
if request is not operational/admin/data-work UI: stop as near miss
build complete Screen Contract
if unresolved decision exists: blocked -> contract clarification
select one primary screen pattern
map every requirement, action, permission, risk and view state to evidence scenarios
implement actual states in the existing stack
run deterministic checks
collect Browser Evidence Receipts
evaluate G0..G7
while a required gate is not passed:
  route contract gaps to Screen Contract
  route IA/visual/layout gaps to design mapping
  route state/interaction/runtime gaps to implementation
  route missing evidence to browser collection
  fix and rerun affected plus regression scenarios
return passed only when every required gate is passed
```

## 재설계

```text
inventory current feature/state/action/permission/data-shape
assign preserve or change to every inventory id
if any decision or evidence is missing: blocked
build Change Contract
map every inventory id to implementation target and browser scenario
if mapping coverage is not 100%: blocked
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

같은 원인이 반복되면 증거를 유지한 채 근본 단계로 되돌아간다. 시도 횟수 때문에 gate를 완화하지 않는다.
