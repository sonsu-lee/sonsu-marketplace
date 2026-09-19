# Evidence contract

근거 종류를 섞지 않는다. schema 검증은 구조, test는 코드 동작, browser receipt는 실제 앱,
Figma readback은 native 디자인 구조, user evidence는 결과를 각각 뒷받침한다.

## Browser receipt

각 task scenario×environment 조합에 다음을 기록한다.

- `scenario_id`, `environment_id`
- 실제 실행 `command`, `build_or_revision`, `url`
- 잠긴 scenario와 동일한 `actions`, `expected`
- 실제 `observed`, `status`
- report 디렉터리 아래 상대경로의 실제 PNG/JPEG/WebP `screenshots`
- 확인한 `console_runtime_errors` 배열

`build_or_revision`은 report의 `artifact.revision`과 일치해야 한다. `passed` receipt에 runtime
오류가 있으면 안 된다. mock, 임의 HTML, Figma, 출처 없는 이미지는 target runtime 근거가 아니다.

실행하지 않았으면 `not_run`, 필수 환경·권한이 없으면 `blocked`, 실행했으나 판단하기 부족하면
`inconclusive`, 결과가 다르면 `failed`다. 없는 근거를 문장으로 대신하거나 뒤 단계 통과로
올리지 않는다.
