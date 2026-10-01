# PR 기본 양식

기본형을 적용하기로 정해진 PR 초안에 사용한다. 실제 대상 공간의 양식 조회와 기본형 사용 가능 여부는 Workflow가 확인한다. 주어진 양식이 있으면 이 기본형을 덧붙이지 않는다.

결정된 출력 언어의 제목을 사용하되 항목의 의미와 순서를 유지한다.

| 의미 | English | 한국어 | 日本語 |
| --- | --- | --- | --- |
| Background | Background | 배경 | 背景 |
| Changes | Changes | 변경 사항 | 変更内容 |
| Screenshots and videos | Screenshots and videos | 스크린샷 및 영상 | スクリーンショット・動画 |
| Verification | Verification | 검증 | 検証 |
| Notes | Notes | 참고 | 補足 |
| Related work | Related work | 관련 작업 | 関連作業 |

| 항목 | 구분 | 작성 기준 |
| --- | --- | --- |
| Background | 필수 | 기존 문제·필요와 이 PR이 필요한 이유. 보통 1–3문장이다. |
| Changes | 필수 | 달라지는 동작·결과와 리뷰어가 물을 만한 결정의 이유. 구조를 바꿨으면 설계 원칙과 구성 요소의 책임·흐름, 리팩터링이면 기존 방식 → 바꾼 방식 → 근거. |
| Screenshots and videos | 조건부 | 제품 화면·상호작용이 바뀌었을 때 필수. 변경 위치를 마킹한 스크린샷과 마커 설명, 또는 확인할 시점을 밝힌 timestamp caption이 붙은 영상. |
| Verification | 조건부 | [검증 포함 기준](../../references/pr-writing.md#검증은-ci가-대신할-수-없는-것만-쓴다)에 해당하는 확인 결과·재현 절차·남은 위험만. |
| Notes | 조건부 | 배포·migration 순서, 호환성, 롤백 방법, 알려진 제한, 리뷰에서 제외해도 되는 생성 파일(glob으로 묶은 한 줄)처럼 리뷰어나 운영자가 알아야 하는 사항. |
| Related work | 조건부 | 확인된 티켓·PR·문서와의 관계. 티켓은 [연결 규칙](../../references/ticket-linking.md)의 문법과 링크를 사용한다. |

```markdown
## <Background heading>
<!-- Required: the existing problem or need and why this PR exists. -->

<Problem or need, and why it matters>

## <Changes heading>
<!-- Required: resulting behavior first. For structural changes, explain the design principle,
component responsibilities and flow. For refactors, state previous approach → new approach → evidence. -->

- <Changed behavior or result>

## <Screenshots and videos heading>
<!-- Conditional: required for product UI or interaction changes. Images must be marked; videos need timestamp captions. -->

<Marked screenshot with what each marker shows, or video with what to watch at each timestamp>

## <Verification heading>
<!-- Conditional: only checks CI does not cover, reproduction steps the reviewer needs,
or untested risk that affects the merge decision. -->

- <What was checked, where, and the observed result>

## <Notes heading>
<!-- Conditional: rollout order, compatibility, rollback, known limits, generated paths reviewers can skip. -->

- <Reviewer- or operator-relevant constraint>

## <Related work heading>
<!-- Conditional: verified relationships only, using the provider's linking syntax. -->

<Part of #123 | Part of [ENG-123](<canonical Linear issue URL>)>
```

완성된 초안에서는 angle-bracket placeholder를 채우고 HTML comment를 포함한 작성 안내와 필수·선택 표시를 제거한다. 빈 조건부 항목과 필요 조건에 해당하지 않는 항목은 제목째 생략하며 `없음`이나 `N/A`로 채우지 않는다. 화면 변경이 있는데 필요한 자료를 준비하지 못했으면 그 사실만 짧게 남기고 준비 절차는 본문 밖에서 보고한다. 주어진 저장소 양식의 필수 항목·HTML comment에는 이 기본형의 삭제 규칙을 적용하지 않는다.
