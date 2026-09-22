# Code Review 판단 평가

[`cases.json`](cases.json)은 `code-review` package만 owner로 두고 focused read-only review와
`review-pr`의 ambiguous publish 판단을 평가합니다. 일반 host-native review, implementation lifecycle,
feedback 수신 workflow, red-team, model 이름·추론 수준과 reviewer 수 비교는 범위 밖입니다.

## Cases

| Case | Skill | Observable contract |
| --- | --- | --- |
| `reachable-zero-timeout` | `review-failure-modes` | 유효한 `0`이 default로 바뀌는 실제 경로와 최소 수정 방향 |
| `protected-boundary` | `review-failure-modes` | 이미 소유된 validation/retry를 중복 finding으로 만들지 않음 |
| `maintenance-duplicate-rule` | `review-maintainability` | 같은 정책의 중복 변경 비용을 consumer impact에 연결 |
| `operability-swallowed-context` | `review-operability` | error type/cause와 correlation 손실이 retry/incident에 미치는 영향 |
| `overengineering-current-diff` | `review-overengineering` | 현재 requirement에 불필요한 추상화와 직접 대안 |
| `overengineering-repository-audit` | `audit-overengineering` | reachability를 확인한 삭제 후보와 검증 |
| `review-pr-ambiguous-publish` | `review-pr` | unknown POST + readback unavailable에서 blind repost 금지 |

평가 모델에는 `request`, `files`, `context`, 실제 skill과 package reference만 제공합니다. `id`,
`expected`와 과거 결과는 숨깁니다. 단어 포함만으로 통과시키지 않고 path/trigger/impact, 기존 owner,
최소 방향과 금지된 mutation을 실제 응답에서 확인합니다.

`review-pr` 상태 전이는 model behavior와 별도로
`plugins/code-review/tests/test_review_protocol.py`의 순수 helper unit test가 7개 action을 고정합니다.
Native ownership은 [`../skill-routing/`](../skill-routing/)에서 explicit call과 일반 review negative case를
분리해 확인합니다.

결과는 `pass | fail | blocked | not_run | inconclusive`로 기록합니다. JSON parse, skill 발견 또는 helper
unit pass를 model judgment pass로 확대하지 않습니다. 이 suite는 source, GitHub PR과 외부 상태를
변경하지 않습니다.
