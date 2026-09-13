# Writing

독자와 목적에 맞춰 업무 글의 문장·문단·정보 순서를 작성하고 다듬는 Codex
플러그인이다. 한국어·일본어·영어 표현은 별도 Fluent Languages 지침과 함께 다듬을 수 있다.

```sh
codex plugin add writing@sonsu-marketplace
```

## 사용 범위

[`writing:writing`](skills/writing/SKILL.md)은 새 작성, 부분 수정, 전체 재작성과 요약을 구분한다.
문장 안의 주체·조건·근거 관계, 문단 역할과 정보 순서를 다듬고, 사실·의무 수준·코드·고정 양식과
절차의 의미를 보존한다. README·주석·동료 메시지는 해당 참고 지침에 따라 작성하고,
티켓·PR은 전달된 항목 안에서 설명을 구성한다. 짧은 답변이나 한 문장 수정은 바로 작성한다.

## Fluent·Workflow와 함께 사용하기

| 플러그인 | 책임 |
| --- | --- |
| Writing | 공통 문장·문단 구성과 정보 순서, README·주석·메시지의 작성법 |
| Fluent Languages | 한국어·일본어·영어별 어순·표현·어조와 독립적인 보존 기준 |
| Workflow | 티켓·PR 양식과 필수 항목, 실제 변경·근거 확인, 연결 문법·게시·재조회 |

세 플러그인은 각각 설치하고 단독으로 사용할 수 있다. Writing은 사용할 수 있는 Fluent 지침을
필요에 따라 적용한다. Workflow는 자체 양식에 Writing의 구성과 Fluent의 표현 지침을 보탤 수 있다.
다른 플러그인이 없어도 설치된 플러그인의 담당 지침으로 작업을 진행한다.

함께 사용할 때는 이미 적용 중인 지침에 필요한 지침만 보탠다. 독자·목적·사실·출력 언어·편집 범위와
정해진 구성을 공유해 같은 초안에 반영하고, 완성한 글의 고정 양식·사실·연결 문법을 대조한다.

언어 지침의 정본은 Fluent, 티켓·PR 양식과 작성 지침의 정본은 Workflow에서 관리한다.
Writing에는 다른 플러그인 지침의 생성본이 없다. 기존 Fluent 설치·호출명·진행 기록은 그대로 유지한다.

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
