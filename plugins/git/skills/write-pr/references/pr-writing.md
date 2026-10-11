# PR 제목과 본문

PR 설명은 리뷰어와, 나중에 히스토리에서 이 PR을 찾는 독자가 읽는 영구 기록이다. 문서별 역할과 쓰지 않을 정보는 [문장 형식 기준](../../../references/tracker-prose.md#문서별-역할)을 따른다.

## 양식을 보존한다

사용자 또는 저장소가 지정한 양식이 기본형보다 우선한다. 제목·항목 순서·체크리스트·필수 필드·고정 문구를 유지하고 내용을 해당 위치에 채운다. 기본형의 제목을 추가하거나 여러 양식을 합치지 않는다. 부분 수정에서는 현재 구조와 요청받지 않은 내용을 보존한다.

양식의 HTML comment는 자동화 표식이나 숨은 지침일 수 있으므로 기본적으로 보존한다. 명시적으로 제거·치환하도록 지정한 작성 안내만 바꾼다. 필수 빈 항목과 체크리스트를 일반적인 빈 항목 정리 규칙으로 지우지 않으며 `N/A` 허용 여부도 해당 양식을 따른다. 고정 제목·체크리스트는 번역하지 않고, 채워 넣는 설명만 전달받은 출력 언어로 작성한다.

검토에 꼭 필요한 티켓·검증·주의사항·미디어를 위한 항목이 없으면 가장 가까운 자유 입력란에 쓴다. 추가 항목이 허용될 때만 최소 항목을 더한다. 담을 수 없는 필수 정보는 본문 밖에서 제약으로 알리고 Draft를 유지한다.

기본형 적용 조건과 `unverified` 처리는 [PR 템플릿 규칙](pr-template.md#기본-템플릿-적용-조건을-확인한다)을 따른다. 기본형은 [PR 기본 양식](../assets/templates/pull-request.md)이며, 출력할 때 HTML comment 안내를 지운다.

## 제목

- [커밋 메시지 규칙](../../../references/conventional-commits.md#확장-규칙) E1·E2의 헤더 형식으로 쓴다. squash 병합하면 그대로 커밋 헤더가 된다. 저장소가 PR 제목 규칙을 문서화했으면 그 규칙을 따른다.
- description은 이 PR이 하는 일을 명령형 한 문장으로 쓴다. 히스토리에서 제목만 보고도 다른 PR과 구분되어야 한다.
- 나쁜 예: "Fix bug", "Fix build", "Phase 1", "Move code from A to B".
- 범위는 scope로만 나타내고 다른 태그는 붙이지 않는다.

## 본문 섹션

- Why: 해결하는 문제와 리뷰어가 알아야 할 맥락을 쓴다. 작은 PR도 한두 문장은 쓴다. 티켓은 링크만 하고 내용을 반복하지 않는다. 외부 링크는 나중에 열리지 않을 수 있으므로, 판단에 필요한 맥락은 본문에 남긴다.
- Changes: 어떤 관점과 결정으로 바꿨는지, 이 방식을 택한 이유, 버린 대안을 쓴다. 코드에 드러나지 않는 것만 쓰고 파일은 나열하지 않는다. 구조 변경은 새 경계·흐름·공개 계약을 설계 수준으로 설명하고, 리팩터링은 "기존 방식 → 바꾼 방식 → 근거" 순서로 쓴다.
- Notes(선택): 알려진 한계, 먼저 볼 곳, 스택의 앞뒤 PR, 일부러 범위 밖에 둔 작업과 그 이슈 링크, 배포·마이그레이션 주의를 쓴다.
- Screenshots(보이는 변화가 있을 때만): [화면 자료 규칙](../../../references/media.md)을 따른다.
- Verification(선택): CI가 보여주지 않는 수동 확인 절차와 벤치마크 수치만 쓴다. 좁은 검사 결과를 넓게 일반화하지 않는다. 예를 들어 파서 단위 테스트 통과를 "Excel 호환성 검증 완료"로 쓰지 않는다.
- 빈 선택 절은 지운다. GitHub 이슈를 완료하는 PR이면 마지막 줄에 `Closes #<번호>`를 쓰고, Linear 티켓은 magic word로 연결한다. 연결 문법은 [티켓 연결 규칙](ticket-linking.md)을 따른다.

## PR 경계를 점검한다

- 스스로 완결되는 변경 하나인지, 관련 테스트가 같은 PR에 들어 있는지 확인한다.
- 리팩터링·포맷 변경은 기능 변경과 분리한다. 단, 작은 지역 정리는 같은 PR에 둘 수 있다.
- 새 API는 사용처와 함께 올린다.
- 크기는 판단 신호로만 쓴다. 대략 100줄은 적당하고 1000줄은 지나치게 크다. 생성 파일과 파일 전체 삭제는 셈에서 빼고, 많은 파일에 흩어진 변경은 크게 본다.
- 크면 스택·파일 단위(리뷰어가 다를 때)·수평(계층)·수직(기능) 분할 중 맞는 방법을 제안한다. 스택의 각 PR은 단독으로 빌드가 통과해야 한다. 나눌 수 없으면 그 이유를 Notes에 쓴다.

## 예시

제목 `fix(session): treat requests at the exact expiry time as expired`

```markdown
## Why
A request that arrived in the same millisecond as the session expiry was accepted, so an expired token could be used one more time.

## Changes
`isExpired()` now compares with `<=`, so the expiry instant itself counts as expired. Every caller already goes through this helper, so I fixed the boundary there instead of adding a grace-period option that no caller needs.

## Verification
With the server clock frozen at the token's `exp` (`FAKE_NOW`), the login endpoint returns `401`; one millisecond earlier it still returns `200`.

Closes #128
```

제목 `feat(settings): show the save toast only after the server confirms`

```markdown
## Why
The "Saved" toast appeared as soon as the button was pressed, so users read failed saves as successful.

## Changes
The toast now waits for the save response and is not shown on failure; the failure path keeps the existing inline error. The button shows a spinner while waiting. The form already blocks duplicate submits, so no extra guard was added.

## Screenshots
| Before | After |
| --- | --- |
| ![Before: toast shown while the request is pending](01-before-save-toast.png) | ![After: spinner on the button, no toast yet](01-after-save-toast.png) |

**After** — click Save, wait for the response, then the toast appears.

![](02-after-save-flow.mp4)
```

## 최종 점검

- 리뷰를 반영해 코드가 바뀌면, 병합 전에 제목·본문이 최종 diff와 맞는지 다시 확인한다.
- 제목·본문이 최종 head의 실제 변경 범위와 같은 결과를 설명하는지 확인한다.
