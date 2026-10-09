# PR 시각 증거 규칙

사용자가 screenshot을 요청했거나 변경이 사용자에게 보이는 화면에 영향을 줄 때 필요성을 판단하기 위해 읽는다.

## 필요성을 판정한다

다음 중 하나이면 PR 본문에 시각 증거를 넣는다.

- 사용자가 스크린샷이나 영상 포함을 요청했다.
- PR template이나 contribution 지침이 요구한다.
- diff가 제품 UI의 layout, style, theme, responsive behavior, 문구, interaction이나 화면 상태를 바꾼다.
- accessibility나 visual regression 결과의 실제 차이를 화면으로 설명해야 한다.

리뷰어가 판단할 정보에 따라 매체를 고른다.

| 필요한 정보 | 자료 |
| --- | --- |
| 문구·배치·색상·최종 화면 상태 | 변경부를 마킹한 스크린샷 |
| 클릭 뒤 변화·전환·애니메이션·시간에 따른 흐름 | 실제 애플리케이션 동작 영상 |
| 동작 순서와 정적 세부사항이 각각 중요함 | 영상 + 마킹 스크린샷 |
| 화면과 무관한 변경 | 기본적으로 첨부 없음 |

같은 정보를 반복하는 영상·이미지를 모두 만들지 않는다. 영상에는 볼 지점을 설명하는 caption을 붙이고 여러 구간 중 특정 시점을 찾아야 할 때만 timestamp를 쓴다. 짧은 한 흐름에 timestamp 목록이나 이미지용 마킹을 강제하지 않는다. 정적 캡처를 이어 붙인 파일을 동작 검증 영상으로 보고하지 않는다.

여러 화면에 걸친 문구 일괄 변경은 대표 화면 하나를 마킹하고 나머지는 변경 전후 문구 표로 대신할 수 있다. VRT 산출물이나 GitHub Checks 링크만으로 본문 자료를 대체하지 않는다. VRT의 actual·diff는 마킹 근거나 원본으로 사용할 수 있다.

사용자가 명시적으로 생략을 요청하면 따른다. 저장소 양식이 요구하는데 사용자가 생략을 요청했으면 생략하되 그 충돌을 결과 보고에 남긴다.

backend-only, 내부 refactor, 문서, metadata와 configuration 변경에는 기본적으로 자료를 만들지 않는다. 다운로드 파일·이메일·API 응답·CLI 출력처럼 화면 밖 결과는 리뷰 판단에 새 정보를 주는 관찰만 `참고` 또는 해당 설명에 남긴다([검증 보고 기준](pr-writing.md#검증은-다시-실행해-확인할-수-없는-것만-쓴다)). 자료가 필요 없으면 `not_applicable`로 처리하고 빈 화면 자료 섹션을 만들지 않는다.

## capture 환경을 고정한다

application command, route, 상태, test data, viewport, device scale factor, theme, locale, timezone, font와 loading 조건을 확인한다. 정적 비교에서는 animation·caret·timestamp·random data·network-dependent 영역을 안정화하거나 mask한다. 동작 영상에서는 판단 대상인 전환·대기·타이밍을 제거하거나 바꾸지 않는다. 실제 사용자 계정과 production data를 사용하지 않는다.

도구는 다음 순서로 선택한다.

1. repository의 기존 스크린샷·visual regression 명령
2. 이미 설치·설정된 Playwright
3. 현재 환경의 브라우저 스크린샷 기능
4. 사용할 수 있는 동등한 기존 도구

이미 있는 동등 도구를 우선한다. 필요한 캡처·마킹 도구나 실행 환경이 없으면 [도구 준비 규칙](media-attachments.md#로컬-산출물을-준비한다)에 따라 이유와 환경별 설치·실행 조건을 본문 밖에 안내한다. 프로젝트 지정 도구가 있으면 그 설치 방법을, 없으면 환경에 맞는 최소 도구를 제안한다. 승인 없이 설치·업그레이드하거나 `npx --yes`로 내려받지 않는다. command·route·상태와 누락 조건을 포함한 capture plan은 실제 생성 완료와 구분한다.

공식 참고: [Playwright screenshots](https://playwright.dev/docs/screenshots)

## before와 after를 구분한다

`after.png`는 현재 변경 결과다. 전후 비교가 필요하고 base의 같은 화면을 같은 조건으로 안전하게 실행할 수 있을 때만 `before.png`를 만든다. current working tree를 checkout하거나 사용자 변경을 제거하지 않는다.

baseline이 없으면 실제 after만 사용하고 비교했다고 주장하지 않는다. after를 복제하거나 서로 다른 viewport·data·browser를 비교하지 않는다. baseline 미확보 사실은 준비 보고에 남기되 리뷰 판단에 중요하지 않으면 PR 본문에 절차 설명을 추가하지 않는다.

## diff와 변경 위치를 표시한다

다음 순서로 기존 도구를 사용한다.

1. repository의 기존 visual diff 산출물
2. Playwright의 actual·expected·diff
3. 이미 사용 가능한 `looks-same`의 `diffBounds`, `diffClusters`와 highlighted diff
4. 이미 사용 가능한 `pixelmatch`의 pixel-level diff mask

`looks-same`은 cluster·bounding 정보가 필요한 경우, `pixelmatch`는 pixel mask가 필요한 경우에 적합하며 필수 dependency는 아니다. 마킹에는 아래의 확인된 DOM overlay도 사용할 수 있다. 필요한 기능을 제공하는 기존 도구가 전혀 없으면 원본과 준비 미완료 이유를 구분해 보고하고 위 도구 준비 규칙에 따라 필요한 설치를 제안한다.

## 첨부 이미지에 마킹한다

첨부 이미지는 애니메이션 GIF를 포함해 변경 위치를 바로 찾을 수 있도록 마킹한 사본이어야 한다. 원본은 비교·재작성을 위해 로컬에 보존하며 기본적으로 첨부하지 않는다. GIF는 변경을 보여 주는 관련 frame에서 marker가 유지되어야 한다. 신뢰할 수 없으면 동작 증거가 필요한 경우 실제 영상으로, 정적 판단이면 마킹 이미지로 대체하거나 미완료로 보고한다.

- 변경 영역 주위에 대비가 충분한 경계나 반투명 highlight를 두고, 여러 영역이면 `1`, `2`, `3`처럼 번호를 붙인다. 색만으로 의미를 구분하지 않는다.
- marker는 변경된 text·control·상태를 가리지 않는다. 번호를 쓴 경우 legend 또는 alt text로 각 번호를 설명한다. alt text에는 목적과 변경 위치를 쓰고 원본과 마킹 사본을 구분한다.
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

OS, 브라우저, font, viewport, scale, animation과 동적 데이터가 안정화되지 않으면 비교를 `inconclusive`로 표시한다. 모든 pixel 차이를 의미 있는 제품 변경으로 해석하지 않는다.

## PR 본문에 배치한다

외부 양식의 지정 위치를 우선한다. 기본형에서는 자료가 하나면 해당 설명 바로 뒤에 볼 지점의 caption과 첨부를 둔다. 여러 자료를 구분할 때만 화면 자료 제목을 쓴다. 영상과 스크린샷이 함께 필요하면 각각 동작 순서와 정적 세부사항 중 무엇을 판단할 자료인지 설명한다.

단일 정적 변경의 로컬 초안 예시:

```markdown
저장 버튼이 수행하는 행동을 분명하게 표현하도록 라벨을 바꿨습니다.

마킹한 영역에서 바뀐 버튼 문구를 확인할 수 있습니다.
<!-- attachment: annotated-after.png | alt: 저장 버튼의 변경된 문구를 표시한 영역 -->
```

before/after 비교가 꼭 필요하면 신뢰할 수 있는 자료만 나란히 배치하거나 하나의 비교 이미지로 합친다. 같은 차이를 보여 주는 before·after·diff를 기본 세트로 붙이지 않는다. 업로드·URL 배치·중복 제거는 [미디어 첨부 규칙](media-attachments.md)을 따른다.

위 비경로 placeholder는 로컬 검토용이며 실제 URL이 아니다. 게시할 final body에서는 실제 caption·순서 설명으로 바꾸거나 제거하고 원격 Draft PR에 남기지 않는다. 자료가 미준비이면 이유와 필요한 설치·실행 조건은 본문 밖에 알리고, 검토에 중요한 증거 미확보 사실만 본문에 한 번 남긴다.
