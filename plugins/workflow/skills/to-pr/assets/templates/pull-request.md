# PR 기본 양식

적용 조건은 [PR 템플릿 규칙](../../references/pr-template.md#기본-템플릿-적용-조건을-확인한다)을 따른다. 각 항목의 작성 기준은 양식 안 HTML comment와 [PR 작성 지침](../../references/pr-writing.md)을 따른다.

결정된 출력 언어의 제목을 사용하되 항목의 의미와 순서를 유지한다.

| 의미 | English | 한국어 | 日本語 |
| --- | --- | --- | --- |
| Background | Background | 배경 | 背景 |
| Changes | Changes | 변경 사항 | 変更内容 |
| Screenshots and videos | Screenshots and videos | 스크린샷 및 영상 | スクリーンショット・動画 |
| Verification | Verification | 검증 | 検証 |
| Notes | Notes | 참고 | 補足 |
| Related work | Related work | 관련 작업 | 関連作業 |

```markdown
## <Background heading>
<!-- Required: the existing problem or need and why this PR exists, usually 1–3 sentences. -->

<Problem or need, and why it matters>

## <Changes heading>
<!-- Required: resulting behavior first, plus the reason for decisions reviewers may question.
For structural changes, explain the design principle, component responsibilities and flow.
For refactors, state previous approach → new approach → evidence. -->

- <Changed behavior or result>

## <Screenshots and videos heading>
<!-- Conditional: required for product UI or interaction changes. Mark changed regions on images and explain each marker;
give videos timestamp captions that say what to watch. -->

<Marked screenshot with what each marker shows, or video with what to watch at each timestamp>

## <Verification heading>
<!-- Conditional: only checks CI does not cover, reproduction steps the reviewer needs,
or untested risk that affects the merge decision. -->

- <What was checked, where, and the observed result>

## <Notes heading>
<!-- Conditional: rollout or migration order, compatibility, rollback, known limits,
generated paths reviewers can skip as one glob line. -->

- <Reviewer- or operator-relevant constraint>

## <Related work heading>
<!-- Conditional: verified relationships only, using the provider's linking syntax with linked ticket IDs. -->

<Part of #123 | Part of [ENG-123](<canonical Linear issue URL>)>
```

배경과 변경을 한 문단으로 설명할 수 있고 조건부 항목이 모두 비면 제목 없이 그 문단만 쓴다([경량형](../../../../references/tracker-prose.md#경량형)).

완성된 초안에서는 angle-bracket placeholder를 채우고 HTML comment를 포함한 작성 안내와 필수·선택 표시를 제거한다. 빈 조건부 항목과 필요 조건에 해당하지 않는 항목은 제목째 생략하며 `없음`이나 `N/A`로 채우지 않는다. 화면 변경이 있는데 필요한 자료를 준비하지 못했으면 그 사실만 짧게 남기고 준비 절차는 본문 밖에서 보고한다.
