# 원본과 출처

Writing은 정보 선별·문서 배치와 글의 구성을 다루는 독립 플러그인이다.
Engineering·Research·Fluent Languages·Workflow와 함께 사용할 수 있으며, 각 플러그인의
설치·호출명·전문 지침과 외부 작업 경계를 그대로 유지한다.

업무 문서 진입점은 [`skills/writing/SKILL.md`](skills/writing/SKILL.md)이다. 공통
[구성 지침](skills/writing/references/composition.md)과 [보존 지침](skills/writing/references/integrity.md),
대상에 맞는 README·주석·동료 메시지 참고 자료를 읽는다. Fluent 표현 지침은 사용할 수 있는
스킬 중에서 선택적으로 적용한다. 플러그인 사이에 생성해 공유하는 사본은 없다.

개발자 블로그 진입점은
[`skills/write-developer-blog/SKILL.md`](skills/write-developer-blog/SKILL.md)이다. 글의 모드별
골격과 기술 근거·직접 검증 절차를 독립된 참고 자료에서 선택해 읽는다.

## 로컬 공통 지침의 유래

공통 구성 원칙은 이 마켓플레이스의 Fluent Languages
`sources/core/communication.md`(`91b4a0efc4d4bb031a9d04fcdb6eb88a873ed736`)에서 시작했다.
Writing은 이를 문장 관계·문단 역할·정보 순서 지침으로 확장했다. 이 로컬 지침은 `im-not-ai`에서
복사하거나 그 프로젝트에 귀속한 내용이 아니다. 보존 지침은 고정 구조와, 요청된 편집 범위 안에서
재구성할 수 있는 자유 설명을 구분한다. 문서 배치 지침은 이 저장소의 기존 문서 영향 판단과
사용자 요청에서 정리한 로컬 정책이다. 작업별 README 누적을 줄이는 목적이며, 아래 외부 출처가
이 정책 전체나 실제 효과를 검증했다는 뜻은 아니다.

Fluent는 언어별 원본·독립적인 보존 규칙·기존 출처를 유지한다. Writing은 초기 구현에서 이어받은
[MIT 라이선스](LICENSE)와 [제삼자 고지](THIRD_PARTY_NOTICES.md)를 보존한다.
고지 보존이 해당 언어 규칙의 포함을 뜻하지는 않는다.

## 업무 문서 구성의 출처 (2026-09-11)

Banksalad·Toss의 한국어 원문, LINEヤフー의 일본어 원문, Go의 영어 원문을
[readme.md](skills/writing/references/readme.md), [comments.md](skills/writing/references/comments.md),
[messages.md](skills/writing/references/messages.md)에서 짧게 인용하고 분석했다. 정확한 링크는
해당 지침·예시 옆에 있다. 티켓·PR 지침과 그 출처인 Mozilla, Google Engineering Practices,
Wantedly, Woowahan 자료는 현재 Workflow가 양식과 함께 독립적으로 관리한다.

이 자료는 저자·조직의 권장 사례이며 가독성·생산성을 측정한 통제 실험이 아니다. 번역본은
별개의 원어 표본으로 세지 않고, 로컬 예시는 따로 표시한다. 원문 전체나 외부 양식을 복사해
포함하지 않았다.

과거 Fluent 평가의 이름·프로토콜·결과는 기존 정체성을 유지한다. 이를 Writing의 자동 선택·
스킬 조합 동작·원어민 선호의 근거로 사용하지 않는다. 현재 [검증 범위](../../evals/writing/README.md)를 참고한다.

## 개발자 블로그 작성의 출처 (2026-09-16)

[kdy1의 Write Blog Post](https://github.com/kdy1/kdy1-scripts/blob/main/skills/write-blog-post/SKILL.md)에서
사용자 자료와 제안·미확인 질문을 분리하고, 저자의 경험·동기·인과관계를 만들지 않는 경계를
참고했다. 로컬 스킬은 사용자가 허용한 repository 자료, 1차 출처와 안전한 직접 검증도 근거로
사용한다는 점에서 범위가 다르다.

Julia Evans의 [어려움에서 주제 찾기](https://jvns.ca/blog/2021/05/24/blog-about-what-you-ve-struggled-with/)와
[실제 코드에서 예제 만들기](https://jvns.ca/blog/2021/07/08/writing-great-examples/)에서 독자의
구체적인 막힘을 출발점으로 삼고 실제 코드의 무관한 부분을 덜어 내는 방식을 참고했다.
[Simon Willison의 AI writing policy](https://simonwillison.net/2026/Mar/1/ai-writing/)에서 AI가
저자를 대신해 1인칭 의견과 이유를 만들지 않는 경계를 참고했다.

[SSGOI 공개 저장소](https://github.com/meursyphus/ssgoi)와
[release 기록](https://github.com/meursyphus/ssgoi/releases)은 별도 블로그 작성 스킬의 원문이
아니며, 실제 구현 조건·재현·검증 범위를 설명하는 개발 기록의 관찰 사례로만 사용했다.
[Josh Comeau의 블로그 구현 글](https://www.joshwcomeau.com/blog/how-i-built-my-blog-v2/)은 코드와
상호작용 예제가 설명을 보강할 수 있다는 선택지를 참고했으며 모든 글에 MDX나 interactive demo를
요구하지 않는다.

외부 문구·템플릿·예제를 복사하지 않았다. 위 자료는 서로 다른 저자의 공개 방법과 사례이며,
고정된 제목 수·단계 수, SEO 지표나 생산성 효과를 보편적인 규칙으로 채택하지 않았다. 로컬
스킬의 네 가지 골격, 흐름 의사코드와 evidence 상태는 사용자 요구와 이 저장소의 검증 경계를
종합한 지침이다.
