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

공식 참고: [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots), [`looks-same`](https://github.com/gemini-testing/looks-same), [`pixelmatch`](https://github.com/mapbox/pixelmatch)

가능한 산출물은 다음과 같다.

- `after.png`
- 신뢰할 수 있는 경우의 `before.png`
- 변경 pixel을 표시한 `diff.png`
- 변경 cluster를 번호나 경계로 표시한 `annotated-after.png`

OS, browser, font, viewport, scale, animation과 동적 데이터가 안정화되지 않으면 비교를 `inconclusive`로 표시한다. 모든 pixel 차이를 의미 있는 제품 변경으로 해석하지 않는다.

## PR 본문에 배치한다

신뢰할 수 있는 before와 after가 모두 있으면 repository template을 해치지 않는 범위에서 비교 표와 diff를 사용한다.

```markdown
## Visual evidence

| Before | After |
| --- | --- |
| ![Before the change](<before-url>) | ![After the change](<after-url>) |

![Highlighted visual differences](<diff-url>)
```

baseline이 없으면 after만 표시하고 before/after 비교를 하지 못한 이유를 적는다. 업로드 전 draft에는 실제 URL처럼 보이는 값을 만들지 않고 `<!-- attachment: after.png | alt: After the change -->` 같은 placeholder를 사용한다.

## 업로드 전 검사한다

화면에 token, cookie, 개인 email, 고객 정보, 내부 URL, hostname, notification과 다른 application의 내용이 없는지 확인한다. 안전하게 제거할 수 없으면 업로드하지 않는다. 각 이미지에 목적과 변경 위치를 설명하는 alt text를 작성한다.
