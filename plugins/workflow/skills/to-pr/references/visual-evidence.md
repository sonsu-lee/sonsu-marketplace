# PR 시각 증거 규칙

사용자가 screenshot을 요청했거나 변경이 사용자에게 보이는 화면에 영향을 줄 때 읽는다.

## 필요성을 판정한다

다음 중 하나이면 시각 증거를 준비한다.

- 사용자가 screenshot 포함을 요청했다.
- diff가 layout, style, theme, responsive behavior, interaction 또는 사용자에게 보이는 상태를 바꾼다.
- PR template이나 contribution 지침이 요구한다.
- accessibility나 visual regression 결과를 화면으로 설명해야 한다.

backend-only, 내부 refactor, 문서, metadata와 사용자에게 보이는 출력이 없는 configuration 변경에는 기본적으로 만들지 않는다. 필요 없으면 `not_applicable`로 처리하고 빈 `Visual evidence` 섹션을 만들지 않는다.

## capture 환경을 고정한다

application command, route, 상태, test data, viewport, device scale factor, theme, locale, timezone, font와 loading 조건을 확인한다. animation, caret, timestamp, random data와 network-dependent 영역을 안정화하거나 mask한다. 실제 사용자 계정과 production data를 사용하지 않는다.

도구는 다음 순서로 선택한다.

1. repository의 기존 screenshot·visual regression 명령
2. 이미 설치·설정된 Playwright
3. 현재 환경의 browser screenshot 기능
4. 사용할 수 있는 동등한 기존 도구

Playwright, browser binary, image library나 application dependency를 자동 설치하지 않는다. `npx --yes`로 package를 내려받지 않는다. 실행 환경이 없으면 필요한 command, route, 상태와 누락 조건을 포함한 capture plan을 반환한다.

공식 참고: [Playwright screenshots](https://playwright.dev/docs/screenshots)

## before와 after를 구분한다

`after.png`는 현재 변경 결과다. `before.png`는 base의 같은 화면을 동일한 환경과 상태로 안전하게 실행할 수 있을 때만 만든다. current working tree를 checkout하거나 사용자 변경을 제거하지 않는다.

신뢰할 수 있는 baseline이 없으면 after만 제공하고 그 사실을 적는다. after를 복제하여 before로 만들거나, 서로 다른 viewport·data·browser의 이미지를 비교하지 않는다.

## diff와 변경 위치를 표시한다

다음 순서로 기존 도구를 사용한다.

1. repository의 기존 visual diff 산출물
2. Playwright의 actual·expected·diff
3. 이미 사용 가능한 `looks-same`의 `diffBounds`, `diffClusters`와 highlighted diff
4. 이미 사용 가능한 `pixelmatch`의 pixel-level diff mask

`looks-same`은 cluster와 bounding 정보가 필요한 경우에 적합하지만 필수 dependency가 아니다. `pixelmatch`는 작은 pixel mask에 적합하며 bounding box에는 추가 처리가 필요하다. 도구가 없으면 설치하지 않고 원본 screenshot과 미생성 이유를 제공한다.

## 첨부 이미지에 마킹한다

PR에 증거로 첨부하는 이미지는 애니메이션 GIF를 포함하여 리뷰어가 변경 위치를 바로 찾을 수 있도록 마킹한 사본이어야 한다. 원본 screenshot은 비교와 재작성을 위해 로컬에 보존하되 기본적으로 첨부하지 않는다. GIF는 변경을 보여 주는 모든 관련 frame에서 marker가 유지되어야 하며 신뢰할 수 없으면 마킹된 정적 이미지나 비디오로 대체한다.

- 변경 영역 주위에 대비가 충분한 경계나 반투명 highlight를 두고, 여러 영역이면 `1`, `2`, `3`처럼 번호를 붙인다. 색만으로 의미를 구분하지 않는다.
- marker는 변경된 text, control과 상태를 가리지 않으며 legend 또는 alt text가 각 번호의 의미를 설명해야 한다.
- 신뢰할 수 있는 before와 after가 있으면 같은 변경 영역에 같은 번호를 사용한다. layout이 달라 좌표 대응이 불확실하면 억지로 같은 경계를 복사하지 않고 각 이미지의 근거를 따로 기록한다.
- 기존 visual diff의 cluster·bounding box, Playwright diff, `looks-same`의 `diffBounds`·`diffClusters`, `pixelmatch` mask에서 계산한 경계 또는 확인한 DOM element를 마킹 근거로 사용한다.
- browser에서 확인한 DOM element에 layout을 바꾸지 않는 overlay를 넣고 capture하는 방식도 가능하다. 제품 UI가 원래 marker를 포함한 것처럼 오해하지 않도록 marker 모양과 legend를 분명히 구분한다.
- 변경 위치를 신뢰할 수 없거나 마킹 도구가 없으면 임의의 위치를 표시하지 않는다. 이 경우 이미지는 준비 미완료로 보고하고, screenshot이 필수인 non-draft PR은 게시하지 않는다.

diff mask나 이미 번호가 붙은 annotation 자체가 변경 위치를 분명히 보여 주면 별도의 중복 marker를 추가하지 않는다.

공식 참고: [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots), [`looks-same`](https://github.com/gemini-testing/looks-same), [`pixelmatch`](https://github.com/mapbox/pixelmatch)

가능한 산출물은 다음과 같다.

- `annotated-after.png`
- 신뢰할 수 있는 경우의 `annotated-before.png`
- 변경 pixel을 표시한 `diff.png`

OS, browser, font, viewport, scale, animation과 동적 데이터가 안정화되지 않으면 비교를 `inconclusive`로 표시한다. 모든 pixel 차이를 의미 있는 제품 변경으로 해석하지 않는다.

## PR 본문에 배치한다

신뢰할 수 있는 before와 after가 모두 있고 browser attachment, 이미 게시된 URL 또는 공개에 안전한 in-place rewrite를 사용하는 경우에는 repository template을 해치지 않는 범위에서 비교 표와 diff를 사용할 수 있다.

```markdown
## Visual evidence

| Before | After |
| --- | --- |
| ![Marked baseline for the changed regions](<before-url>) | ![Marked result for the changed regions](<after-url>) |

![Highlighted visual differences](<diff-url>)
```

GitHub CLI의 안전한 기본 append 흐름에서는 마킹된 before와 after를 하나의 comparison image로 합친다. repository template이 허용하면 `Visual evidence`를 마지막 section으로 둔다. template 순서가 고정되어 visual section이 중간에 있으면 attachment로 얻은 remote URL을 해당 section에 넣어 body를 다시 기록하고, body 끝의 중복 URL을 제거한다. 어느 경우든 각 이미지의 순서와 marker를 text로 설명하고 local path placeholder로 비교 표를 만들지 않는다.

baseline이 없으면 after만 표시하고 before/after 비교를 하지 못한 이유를 적는다. 로컬 검토용 draft에는 실제 URL처럼 보이는 값을 만들지 않고 `<!-- attachment: annotated-after.png | alt: Marker 1 shows the changed navigation -->` 같은 비경로 placeholder를 사용할 수 있다. `gh pr create --draft`에 전달할 final body에서는 이를 실제 caption·순서 설명으로 바꾸거나 제거하며 원격 Draft PR에는 placeholder를 남기지 않는다.

## 업로드 전 검사한다

화면에 token, cookie, 개인 email, 고객 정보, 내부 URL, hostname, notification과 다른 application의 내용이 없는지 확인한다. 안전하게 제거할 수 없으면 업로드하지 않는다. 각 이미지에 목적, marker 번호와 변경 위치를 설명하는 alt text를 작성하고 원본과 마킹 사본을 혼동하지 않는다.
