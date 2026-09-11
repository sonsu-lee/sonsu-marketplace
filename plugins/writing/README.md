# Writing

독자와 목적에 맞춰 업무 글의 문장·문단·정보 순서를 작성하고 다듬는 Codex·Claude Code
플러그인입니다. 한국어·일본어·영어의 표현은 별도 Fluent Languages와 함께 적용할 수 있습니다.

```sh
# Codex
codex plugin add writing@sonsu-marketplace

# Claude Code
claude plugin install writing@sonsu-marketplace
```

## 사용 범위

[`writing:writing`](skills/writing/SKILL.md)은 새 작성, 부분 수정, 전체 재작성과 요약을 구분합니다.
문장 안의 주체·조건·근거 관계, 문단 역할과 정보 순서를 다듬고, 사실·의무 수준·코드·고정 양식과
절차 의미를 보존합니다. README·주석·동료 메시지에는 필요한 장르 지침만 적용합니다.
티켓·PR은 전달된 항목 안에서 설명을 구성하며, 구체적인 양식 정책은 Workflow가 관리합니다.
짧은 답변이나 한 문장 수정에는 별도 계획·질문·작업 파일을 요구하지 않습니다.

## Fluent·Workflow와 함께 사용하기

| 플러그인 | 책임 |
| --- | --- |
| Writing | 공통 문장·문단 구성과 정보 순서, README·주석·메시지의 작성법 |
| Fluent Languages | 한국어·일본어·영어별 어순·표현·어조와 독립적인 보존 기준 |
| Workflow | 티켓·PR 양식과 필수 항목, 실제 변경·근거 확인, 연결 문법·게시·재조회 |

세 플러그인은 각각 설치하고 단독으로 사용할 수 있습니다. Writing은 현재 inventory에 있는
Fluent 언어 스킬을 필요에 따라 적용합니다. Workflow는 자체 양식에 Writing의 구성과 Fluent의
표현 지침을 함께 적용할 수 있습니다. 없는 플러그인을 자동 설치하거나 필수 의존성으로 취급하지 않습니다.

지침은 같은 초안에 한 번씩 반영합니다. Workflow가 이미 호출한 Writing·Fluent를 재호출하거나
Fluent에서 Writing으로 되돌아가는 순환, 스킬마다 완성본을 다시 쓰는 절차를 만들지 않습니다.
지정된 편집 범위와 구조를 함께 전달하고, 표현 수정 뒤에도 고정 양식·사실·연결 문법을 확인합니다.

언어 지침의 정본은 Fluent, 티켓·PR 양식과 작성 지침의 정본은 Workflow에 있습니다.
Writing은 이 파일들을 포함하거나 생성하지 않습니다. 기존 Fluent 설치·호출명·진행 기록을 유지하며
Writing을 사용하려고 Fluent를 제거하거나 기록을 이전할 필요가 없습니다.

## 검증과 출처

[장르별 참조](skills/writing/references/)는 조직·저자의 원문 지침과 로컬 예시를 구분합니다.
번역문을 독립적인 원문 표본으로 세지 않고, 권장 양식을 보편적인 정답이나 생산성 실험으로 취급하지 않습니다.
언어별 원문·출처 기록은 Fluent, 티켓·PR 원문 사례는 Workflow에서 관리합니다.

[조합 검증 자료](../../evals/writing/README.md)는 각각의 단독 설치와 함께 사용하는 경우를 다룹니다.
설치·명시적 지침 적용은 자동 스킬 선택과 원어민 선호 평가를 입증하지 않습니다. Writing은 beta입니다.
라이선스와 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md),
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 보존합니다.

## 컴팩션 후 작업 재개

[`writing:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계의 작성·편집에서 원문·초안,
편집 범위와 완료 구간을 `.sonsu/continuity/`에 기록하고 같은 session의 재개 후 실제 상태와 대조합니다.
다른 작업의 출력 문체만 적용하거나 짧은 문장을 수정할 때는 기록하지 않습니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 스킬로 수동
재개할 수 있습니다. helper는 Python 3.9+와 POSIX 환경을 사용합니다.
[운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
