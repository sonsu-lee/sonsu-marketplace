# Evidence contract

이 문서의 실행용 계약과 JSON/validator는 운영형 웹 구현·런타임 감사에 적용한다. 제안/Figma-only·일반 UI의 범위·결과는 [산출물별 작업 경계](delivery.md)를 따른다.

## 증거 종류를 섞지 않는다

- deterministic check: schema, type, lint, unit/integration test 결과
- actual browser observation: 실제 app URL에서 수행한 행동과 관찰
- screenshot: 특정 viewport와 state의 시각 증거
- semantic evidence: DOM/accessibility tree, role/name/state 또는 수동 inspection
- Figma evidence: native frame, layout, component, variable, reaction readback

한 종류는 다른 종류를 대신하지 않는다. JSON fixture parse는 routing을 증명하지 않고, screenshot은 interaction이나 console 상태를 증명하지 않으며, Figma는 production browser를 증명하지 않는다.

## Browser Evidence Receipt

각 required scenario×viewport에 다음을 기록한다.

- `scenario_id`
- 실제 실행 `command`
- `build_or_revision`
- `url`
- `viewport_id`
- receipt `status`: `passed`, `failed`, `blocked`, `inconclusive`, `not_run`
- 수행한 `actions`
- `expected`, `observed`
- 한 개 이상의 `screenshots`
- 확인한 `console_runtime_errors` 배열. 오류가 없으면 빈 배열이다.

receipt는 Screen Contract의 scenario와 viewport를 참조해야 한다. 출처가 없는 이미지, design mock, 임의 HTML screenshot은 actual target app 증거로 인정하지 않는다.
receipt의 `actions`와 `expected`는 참조한 scenario 값과 일치해야 하며, contract가 요구하지 않은 scenario×viewport receipt로 coverage를 채울 수 없다.
`overall: passed`인 report의 gate/check evidence와 screenshot은 report 디렉터리 안의 상대경로로 기록한다. 절대경로, `..` 또는 symlink로 디렉터리 밖을 참조할 수 없으며 실제로 존재하는 non-empty file이어야 한다. screenshot은 구조와 정상 종료를 확인할 수 있는 완전한 PNG, JPEG 또는 WebP 파일이어야 하며 signature만 있는 파일은 거부한다. 경로와 형식 검사는 내용의 진실성을 대신하지 않으므로 reviewer는 provenance와 관찰 결과도 대조한다.
`overall: passed`에서는 모든 required receipt의 `status`도 `passed`여야 한다.
`TBD`, `N/A`, `replace-me`, `fixme`, `changeme` 같은 sentinel은 provenance나 observation이 아니며 `overall: passed` report에서 거부한다.

## 정직한 상태

- 실행했고 요구 결과를 확인했으면 `passed`
- 실행했고 불일치가 있으면 `failed`
- 필요한 제품 결정·권한·환경이 없어 진행할 수 없으면 `blocked`
- 실행했으나 결과가 판정하기 부족하면 `inconclusive`
- 실행하지 않았으면 `not_run`

도구 미노출이나 runtime 부재는 실패로 꾸미지도, pass로 간주하지도 않는다.
