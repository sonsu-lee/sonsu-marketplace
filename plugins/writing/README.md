# Writing

독자와 목적에 맞춰 업무 문서와 개발자 블로그의 내용을 선별하고, 문서 배치와 글의 흐름을 다듬습니다.

## 설치

[마켓플레이스를 등록](../../README.md#설치)한 뒤 설치합니다.

```sh
codex plugin add writing@sonsu-marketplace
claude plugin install writing@sonsu-marketplace
omp plugin install writing@sonsu-marketplace
```

omp에서는 기본 구성에 들지 않는 opt-in 패키지이므로 필요할 때 직접 설치합니다.

단독으로 사용할 수 있고, Dev Workflow·Research·Fluent·Git·Tickets와 함께 설치하면 필요한 지침을 같은 초안에 적용합니다. 담당 구분은 [협업과 언어 선택](references/collaboration.md)과 [스킬 라우팅 문서](../../docs/architecture/skill-routing.md#writingfluentgittickets-조합)에 있습니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| [`writing`](skills/writing/SKILL.md) | 답변·업무 문서·README·주석·동료 메시지를 쓰거나 고치거나 요약할 때, 주어진 양식 안에서 티켓·PR 설명을 쓸 때 | 편집 범위·사실·양식을 유지한 글, 영속 문서는 담당 문서의 갱신 결과 |
| [`write-developer-blog`](skills/write-developer-blog/SKILL.md) | 개발자 블로그·TIL·디버깅 회고·기술 선택·how-to·회고·의견글을 기획·작성·수정·검토할 때 | 요청 유형(`plan`·`draft`·`revise`·`audit`)에 맞는 흐름·본문·수정본 또는 finding |

## 사용 예시

요청: “이번에 추가한 `--dry-run` 옵션을 문서에 반영해 줘.”

`writing`은 옵션 설명을 담당하는 기존 문서를 찾아 갱신하고, README는 첫 사용이나 중요한 제약이 바뀔 때만 수정합니다. 일회성 작업 과정은 문서 대신 작업 보고에 남깁니다.

요청: “오늘 확인한 `git log --follow` 동작을 TIL로 써 줘.”

`write-developer-blog`는 독자·핵심 답·근거·한계를 흐름으로 먼저 정한 뒤, 제공된 관찰 범위 안에서 본문을 씁니다. 저자의 경험이나 선택 이유는 저자 자료로 확인합니다.

## 구성

[작업 연속성 참고 자료](references/continuity.md)는 여러 단계의 작성·편집에서 원문·초안·편집 범위·완료 구간을 `.sonsu/continuity/`에 기록하고, 같은 session의 재개 후 실제 상태와 대조합니다. 다른 작업의 출력 문체만 적용하거나 짧은 문장을 수정할 때는 기록 없이 진행합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 참고 자료·기록 경로만 전달합니다. 설치 후 CLI의 `/hooks`에서 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 참고 자료로 수동 재개합니다. helper는 Python 3.9+와 POSIX 환경을 사용합니다. [운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

장르별 참조는 조직·저자의 원문 지침과 로컬 예시를 구분합니다. 원문은 저자·조직이 권장하는 사례이며 보편적인 정답이나 생산성 실험의 결과가 아닙니다. 언어별 원문·출처 기록은 Fluent, 티켓·PR 원문 사례는 Workflow에서 관리합니다. Writing은 beta입니다. 라이선스와 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있습니다.

## 검증

```sh
python3 scripts/validate_refactor_inventory.py check --plugin writing
python3 scripts/render-continuity.py --check
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py'
```

모델 적용 사례와 판정 기준은 [조합 검증 자료](../../evals/writing/README.md)에 있습니다. 설치·명시적 지침 적용, 자동 스킬 선택, 원어민 선호 평가는 각각 별도의 근거가 필요합니다.
