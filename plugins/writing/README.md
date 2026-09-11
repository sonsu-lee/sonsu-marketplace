# Writing

한국어·일본어·영어로 답변과 업무 문서를 작성하고, 문장·문단·정보 순서를 다듬는 Codex·Claude Code
플러그인입니다. Fluent Languages의 언어별 표현 지침을 글쓰기 공통 지침과 장르별 작성법 안으로 이전했습니다.

```sh
# Codex
codex plugin add writing@sonsu-marketplace

# Claude Code
claude plugin install writing@sonsu-marketplace
```

## 사용 범위

[`writing:writing`](skills/writing/SKILL.md)은 새 작성, 부분 수정, 전체 재작성과 요약을 구분합니다.
자유 초안의 구성은 요청에 맞게 바꾸고, 사실·의무 수준·고정 양식·절차 의미는 보존합니다.
짧은 답변이나 문장 수정에는 장르 선택을 위한 질문이나 별도 작업 파일을 요구하지 않습니다.

| 작성 대상 | 제공하는 지침 |
| --- | --- |
| 티켓 | 일반 작업·버그·조사 3종, 항목별 내용, 관찰·요청·합의와 미확인 정보 구분 |
| PR | 변경 이유와 결과, 기존 기본 양식, 근거·관련 작업·시각 자료를 둘 위치 |
| README | 독자·용도, 실행까지의 경로, 전제와 기대 결과, 상세 문서 연결 |
| 주석 | API 호출 계약, 비자명한 구현 이유, workaround·TODO에 남길 맥락 |
| 동료 메시지 | 요청·결정·보고·인계에 필요한 정보와 순서 |

사용자·팀·저장소 양식이 있으면 그 항목에 내용을 담습니다. 새 완료조건이나 해결 방법을
빈칸 채우기처럼 만들지 않습니다. 표현 지침은 출력 언어에 맞춰 필요한 참조만 읽습니다.

## Workflow와 함께 사용하기

Writing은 글의 내용 배치와 표현을 담당합니다. Workflow의 `to-ticket`과 `to-pr`은 실제 사실·diff와
유효한 원격 양식·필수 필드를 확인하고, 연결 문법·게시 권한·첨부·재조회를 담당합니다.
Writing으로 다듬은 초안만으로 게시 조건이 충족되지는 않습니다.

Workflow는 단독으로 설치해도 작성할 수 있습니다. Writing의 티켓·PR 지침과 기본 양식을
[`scripts/render-writing.py`](../../scripts/render-writing.py)가 Workflow 내부에 포함하므로 런타임
의존성과 수동 사본이 생기지 않습니다. Writing의 MIT 고지도 Workflow에 함께 포함합니다.
생성 파일 대신 Writing의 정본을 고친 다음 저장소 루트에서 아래 명령을 실행합니다.

```sh
python3 scripts/render-writing.py
python3 scripts/render-writing.py --check
```

## Fluent Languages에서 이전하기

마켓플레이스를 최신 버전으로 갱신한 뒤 `writing`을 설치하고 기존 `fluent-languages`를 제거합니다.
마켓플레이스의 이름 변경이 이미 설치된 플러그인을 자동 교체하지는 않습니다. 두 패키지를 계속
활성화하면 같은 출력에 이전 Fluent 지침과 Writing 지침이 함께 선택될 수 있습니다.
기존 명시 호출 `fluent-languages:fluent-korean`, `fluent-japanese`, `fluent-english`는
`writing:writing`과 요청할 출력 언어로 바꿉니다. 예: “writing으로 일본어 PR 설명을 다듬어 줘.”

기존 Fluent의 진행 중인 편집 기록은 자동 이동·삭제하지 않습니다. 필요하면 기존 패키지에서
원문·초안·완료 구간을 복구한 뒤, 실제 자료와 대조해 Writing의 새 작업 기록으로 인계합니다.
Writing helper는 다른 플러그인 이름으로 저장된 기록을 자동 복구하지 않습니다.

## 검증과 근거의 범위

[장르별 참조](skills/writing/references/)는 각 조직·저자가 제시한 원문 작성법과 로컬 예시를
구분합니다. 번역문을 한·일·영 원문 표본으로 세지 않으며, 조직의 권장 양식이 모든 글의 정답이거나
생산성 개선을 입증한 실험이라고 주장하지 않습니다.

[Writing 검증 자료](../../evals/writing/README.md)는 패키징·독립 실행 경계와 제한된 작성 사례를
다룹니다. 기존 [한국어 비교 자료](../../evals/language-style/README.md),
[일본어 평가](../../evals/fluent-japanese/README.md), [영어 fixture](../../evals/fluent-english/README.md)는
이전 계약을 보존한 자료이며 새 진입점의 선택·참조 로딩이나 원어민 품질을 입증하지 않습니다.
일본어의 여섯 문어·번역 규칙은 이전 main에 포함된 내용을 유지합니다. 과거 채택 보류 판정과
현재 파일 포함 여부는 별개이며, 모델 평가만으로 beta 상태를 해제하지 않습니다.

라이선스와 이전 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md),
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 보존합니다.

## 컴팩션 후 작업 재개

[`writing:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계의 작성·편집에서 원문·초안,
편집 범위와 완료 구간을 `.sonsu/continuity/`에 기록하고 같은 session의 재개 후 실제 상태와 대조합니다.
다른 작업의 출력 문체만 적용하거나 짧은 문장을 수정할 때는 기록하지 않습니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달합니다. 설치 후 CLI의
`/hooks`에서 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 스킬로 수동
재개할 수 있습니다. helper는 Python 3.9+와 POSIX 환경을 사용합니다.
[운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.
