# Writing

독자와 목적에 맞춰 업무 문서와 개발자 블로그의 내용을 선별하고, 문서 배치와 글의 흐름을
다듬는 Codex 플러그인이다. 업무 문서는 기존 문서를 우선 갱신하고, 개발자 블로그는 저자의
경험·코드·출처·검증 결과를 구분해 구성한다.

[마켓플레이스를 등록](../../README.md#설치)한 뒤 설치한다.

```sh
codex plugin add writing@sonsu-marketplace
```

## 사용 범위

[`writing:writing`](skills/writing/SKILL.md)은 새 작성, 부분 수정, 전체 재작성과 요약을 구분한다.
문장 안의 주체·조건·근거 관계와 문단·정보 순서를 다듬고, 사실·의무 수준·코드·고정 양식과
절차의 의미를 보존한다. 부분 수정은 지정 범위에 한정하고, 짧은 답변이나 한 문장 수정은 바로 작성한다.

영속 문서를 다룰 때는 이후에도 찾아볼 내용인지 판단하고 해당 주제의 기존 문서를 우선 갱신한다.
README는 용도·주요 기능·첫 사용·중요한 제약·탐색 경로가 바뀔 때 수정한다. 주석·동료 메시지는
해당 참고 지침을 적용하고, 티켓·PR은 전달된 항목 안에서 설명을 구성한다.

예를 들어 “이 변경에서 문서에 남길 내용을 골라 기존 문서를 갱신해 줘” 또는
“이 README의 주요 안내는 남기고 상세 설정은 기존 가이드로 정리해 줘”라고 요청할 수 있다.

[`writing:write-developer-blog`](skills/write-developer-blog/SKILL.md)은 개발자 블로그, TIL,
디버깅 회고와 기술 선택 글을 기획·작성·수정·검토한다. 본문 전에 독자·문제·핵심 답·절의 순서·
근거·결말을 흐름 의사코드로 정하고, 저자의 1인칭 경험이나 의사결정 이유를 자료 없이 만들지 않는다.
핵심 주장을 안전한 local test나 격리된 fixture로 확인할 수 있으면 최소 검증을 수행하고,
`observed`, `source-confirmed`, `inference`, `unknown`, `not_run`을 구분한다.

예를 들어 “이 장애를 재현해서 디버깅 회고 글로 써 줘”, “오늘 알게 된 내용을 짧은 TIL로 정리해
줘” 또는 “두 기술을 비교해 선택한 근거를 글로 써 줘”라고 요청할 수 있다. README·업무 문서와
티켓·PR은 기존 `writing:writing`과 Workflow의 책임이며, 블로그 작성법 자체의 다중 출처 조사는
Research가 담당한다.

## Engineering·Research·Fluent·Workflow와 함께 사용하기

| 플러그인 | 책임 |
| --- | --- |
| Writing | 업무 문서의 정보 선별·배치와 개발자 블로그의 흐름·근거 구성 |
| Engineering | 글과 별개로 수행해야 하는 제품 결함의 진단·수정과 구현 검증 |
| Research | 글의 결론을 좌우하는 외부 다중 출처 조사와 교차 검증 |
| Fluent Languages | 한국어·일본어·영어별 어순·표현·어조와 독립적인 보존 기준 |
| Workflow | 티켓·PR 양식과 필수 항목, 실제 변경·근거 확인, 연결 문법·게시·재조회 |

각 플러그인은 단독으로 사용할 수 있다. 함께 설치하면 같은 초안에 필요한 지침을 적용한다.
정본과 인계 방식은 [스킬 라우팅 문서](../../docs/architecture/skill-routing.md#writingfluentworkflow-조합)를 참고한다.

## 검증과 출처

[장르별 참조](skills/writing/references/)는 조직·저자의 원문 지침과 로컬 예시를 구분한다.
원문은 저자·조직이 권장하는 사례이며 보편적인 정답이나 생산성 실험의 결과가 아니다.
언어별 원문·출처 기록은 Fluent, 티켓·PR 원문 사례는 Workflow에서 관리한다.

[조합 검증 자료](../../evals/writing/README.md)는 단독 설치와 함께 사용하는 경우를 다룬다.
설치·명시적 지침 적용, 자동 스킬 선택, 원어민 선호 평가는 각각 별도의 근거가 필요하다. Writing은 beta다.
라이선스와 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md),
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 보존한다.

## 컴팩션 후 작업 재개

[`writing:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계의 작성·편집에서 원문·초안,
편집 범위와 완료 구간을 `.sonsu/continuity/`에 기록하고 같은 session의 재개 후 실제 상태와 대조한다.
다른 작업의 출력 문체만 적용하거나 짧은 문장을 수정할 때는 기록하지 않는다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달한다. 설치 후 CLI의
`/hooks`에서 정의를 검토하고 신뢰해야 실행된다. hook을 사용할 수 없으면 위 스킬로 수동
재개한다. helper는 Python 3.9+와 POSIX 환경을 사용한다.
[운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고한다.
