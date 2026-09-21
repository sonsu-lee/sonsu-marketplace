# Writing·개발자 블로그·Fluent·Workflow 분리와 조합 검증

Writing의 정보 선별·문서 배치·공통 구성과 개발자 블로그의 흐름·근거 구성, Fluent의
한국어·일본어·영어 표현, Workflow의 티켓·PR 양식·운영을 각각 단독으로 사용하거나 함께 적용할
때의 범위를 검증한다. 원어민 선호나 일반적인 품질 개선을 입증하는 실험은 아니다. 과거 Fluent의
고정 protocol·snapshot·결과도 새 조합의 근거로 재표기하지 않는다.

## 결정론적 검사

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/writing/skills/write-developer-blog
find .agents plugins evals -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 scripts/render-agent-policy.py --check
python3 scripts/render-continuity.py --check
python3 evals/language-style/eval.py validate
python3 -B -m unittest -v evals/task-continuity/test_runtime.py evals/plugin-compat/test_compat.py evals/language-style/test_eval.py evals/fluent-japanese/test_eval.py
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
git diff --check
```

JSON·frontmatter와 세 패키지의 스킬/참조 상대 경로를 확인한다. Fluent는 언어별 독립 정본을 대조한다. 한국어 확장판의 효과는 [한국어 평가](../fluent-korean/README.md)에서 별도로 확인한다.
원어 용례·보호 문자열과 법적 고지는 기존 main의 바이트를 기준으로 보존 여부를 확인한다. Workflow의 티켓 3종 본문도 기존 main과 같아야 한다.
PR 기본 양식과 `unverified` 시 기본형을 확정하지 않는 정책, marker·연결 문법은 별도로 검토한다.
continuity 검사는 각각의 Fluent·Writing 기록을 실제 helper로 만들고 서로 대신 복구하지 않는지 확인한다.

Fluent는 언어별 SKILL을 직접 관리한다. 작업 재개용 공통 continuity 생성기는 유지하며 언어 표현 규칙을 생성하지 않는다.
Writing에서 Workflow로 지침·양식을 복사하는 생성기는 없다.
양식 수정은 Workflow에서, 언어 지침 수정은 Fluent에서 한다. 각 플러그인의 링크·경로와
생성 결과 검사는 실제 모델의 지침 적용을 증명하지 않는다.

## 명시적 지침 적용 사례

- [`cases.json`](cases.json): 19개. Writing 단독 16개, Fluent 단독 3개.
- [`workflow-cases.json`](workflow-cases.json): Workflow 단독 3개.
- [`composition-cases.json`](composition-cases.json): 10개. Writing+Fluent 6개, Workflow+Fluent 2개,
  Workflow+Writing 1개, 세 플러그인 함께 1개.
- [`developer-blog-cases.json`](developer-blog-cases.json): Writing의 개발자 블로그 명시 적용 10개.

각 사례의 `installed_plugins`를 해당 실행의 유일한 관련 inventory로 취급한다. 고정한 패키지에서
`entry_skill`과 실제 필요한 참조를 읽고 요청을 수행한다. 제공된 양식·조회 결과는 테스트 fixture이며
추가 원격 조회·게시·설치는 하지 않는다. 각 사례의 실제 출력과 적용한 스킬·참조 경로를 남기고,
생성자에게 아래 판정 기준이나 과거 출력·판정을 주지 않는다. 사례 ID는 정답을 암시하지 않는
opaque ID로 바꾼다. `installed_plugins`와 `entry_skill`은 명시적 적용 실행의 설정이며,
평가 파일 전체를 프롬프트에 붙이지 않는다.

| 사례 | 생성 후 확인할 계약 |
| --- | --- |
| ko-short | Fluent만으로 한 문장 수정만 반환하고 계획·설치·양식을 요구하지 않는다. |
| ko-rewrite | Writing이 자유 초안을 문단으로 재구성하고 두 번 발생·원인 미확인·다른 형식 미확인을 유지한다. |
| ko-partial | 제목 3개와 요청 밖의 문구를 그대로 두고 현상 문장만 바꾼다. |
| ko-bug | 주어진 사실로 문단 초안을 만들고 원인·방법·완료조건·저장소 양식을 확정하지 않는다. |
| ja-fixed-pr | 지정 제목·순서·marker·Part of 행과 실기 미확인을 보존한다. |
| ja-meaning | Fluent만으로 미기록·실제 행위자 불명·배정된 A의 실행 미확인을 구분한다. |
| en-readme | 용도·전제·명령·결과, Python 3.9+, 원문 명령, 종료값 0/1과 입력 무변경을 보존한다. |
| en-comments | Fluent만으로 signature와 최초 일치·없으면 None·대소문자 구분을 모두 유지한다. |
| ja-message | 조사 요청·어제 한 번·원인 미확인을 보존하고 기한·해결책을 만들지 않는다. |
| ko-summary | 실행용 절차가 아닌 개요로 원본 링크·조건·복구 의미를 보존한다. |
| workflow-ticket-only | 다른 플러그인 없이 자체 버그 기본형으로 알려진 사실만 쓴다. |
| workflow-pr-unverified | 양식 미확인을 부재로 바꾸지 않으며 실제 UI·첨부 미확인을 유지한다. |
| workflow-pr-fixed | 제공 양식·marker·Part of URL과 미확인 UI를 보존한다. |
| writing-fluent-* | 대응하는 단독 사례의 의미·형식 계약을 유지하고 해당 출력 언어 지침을 한 번 적용한다. Fluent가 허용된 재구성을 이전 구조로 되돌리지 않는다. 한국어 요약의 생략 범위와 영어 자유 개요의 번호 제거도 확인한다. |
| workflow-fluent-* | Writing 없이 Workflow 양식과 Fluent 표현을 함께 적용하고 고정 제목·연결 문법·미검증 상태를 보존한다. |
| workflow-writing-unverified | Fluent 없이 구성 지침을 적용하고 Workflow의 양식 확정 경계를 유지한다. |
| all-three-ja-fixed-pr | Workflow가 정한 양식 안에서 Writing·일본어 Fluent를 중복·순환 없이 적용한다. |

### 개발자 블로그 사례

개발자 블로그 사례는 `writing:write-developer-blog`를 명시적으로 적용한다. 본문 전에 나타나는
흐름 의사코드와 실제 초안, 근거 상태, 사용한 명령·출력을 함께 보관한다. 흐름 의사코드의 제목이나
문장 자체를 고정 문자열로 비교하지 않고 독자·문제·핵심 답·전개·근거·결말이 서로 연결되는지
읽어서 판정한다. 다만 여섯 필드는 이름이 공개 출력 계약이므로 본문 작성 사례에서 각각의 값이
제시됐는지 확인한다.

| 사례 | 생성 후 확인할 계약 |
| --- | --- |
| blog-author-gap | 1인칭 경험·선택 이유를 만들지 않고 가능한 각도, 흐름과 필요한 질문에서 멈춘다. |
| blog-til-sufficient | 짧은 흐름과 TIL 초안을 같은 응답에 제공하며 저자가 제공한 실행을 `observer: author`, 현재 작업 재실행을 `false`로 남기고 미확인 버전과 구분한다. |
| blog-debug-counterevidence | 격리 fixture에서 허용된 명령만 실행하고 예상·관찰을 나눈다. 결과가 최초 `.strip()` 가설과 다르면 실제 동작에 맞춰 논지를 바꾼다. |
| blog-decision-tradeoff | 선택 기준·대안·기각 이유·부담한 비용·현재 상태·재검토 조건을 보존한다. |
| blog-production-not-run | production 결제·고객 데이터 접근을 수행하지 않고 원인 미확인과 `not_run`을 남긴다. |
| blog-draft-only | 채팅 초안만 반환하고 파일·Git·원격 상태를 변경하지 않으며 local `tsc`의 범위만 쓴다. |
| blog-source-is-not-experience | 출처가 확인한 API 동작을 저자의 사용 경험이나 채택 이유로 바꾸지 않는다. |
| blog-writing-standalone | Research·Fluent·Engineering을 설치하지 않고 Writing만으로 관찰·추론·미실행을 구분한다. |
| blog-revise-scoped | 지정 문장과 필요한 연결만 수정하고 제목·나머지 문단·코드·링크·주장 순서를 보존한다. |
| blog-audit-read-only | 원문을 재작성하지 않고 현재 흐름을 기준으로 위치·근거·영향·최소 수정 방향이 있는 finding을 반환한다. |

`blog-debug-counterevidence`의 파일은 실행별 임시 디렉터리에 배치하고 source repository 밖에서
`allowed_command`만 실행한다. 원출력, exit code와 임시 경로를 기록하고 실행 뒤 임시 디렉터리를
정리한다. production·유료 서비스·고객 데이터 사례는 실제 연결을 제공하지 않는다.

등록된 사례를 아직 실행하지 않았다면 `not_run`이다. JSON 파싱과 skill frontmatter 검증은
저자성 보존, 상황별 초안 진행이나 반례에 따른 논지 변경을 입증하지 않는다.

### 문서 배치 사례

아래 사례도 기존 `id`·`prompt`·`installed_plugins`·`entry_skill` 형식을 사용한다. 이 디렉터리에는
사례를 자동 실행하는 runner가 없으며, 파일 시나리오는 `prompt` 안에 현재 문서와 변경 사실을
담는다. `### <상대 경로>` 뒤의 `markdown` 코드 블록을 실행별 임시 루트에 파일로 배치한 뒤
같은 요청을 수행한다. 입력은 테스트용 자료이며 실제 제품 코드나 명령의 실행 근거로 삼지 않는다.
새 framework나 실제 저장소의 문서를 fixture로 만들지 않는다.

| 사례 | 생성 후 확인할 계약 |
| --- | --- |
| ko-docs-mixed-change | 명령 사용법에 `--summary`의 빈 값 조건·예제를 반영하고 기존 구조 설명을 현재 처리 방식에 맞춘다. README에는 주요 기능과 사용 경로만 반영하며 클래스명·수정 횟수·검사 결과를 누적하지 않는다. 기본 실행·입력 무변경·Python 조건을 유지한다. |
| ko-docs-existing-option | 기존 옵션 참조에 기본값 20·범위 1~200·전체 검사 후 출력 제한·오류 문자열·종료 코드 2를 반영한다. README와 기존 `--verbose` 계약은 유지하고 새 문서를 만들지 않는다. |
| ko-docs-internal-fix | 영속 문서를 변경하거나 새로 만들지 않는다. 버퍼 수정과 제공된 검증 결과는 작업 보고에서만 다룬다. |
| ko-docs-new-topic | 운영자가 별도로 찾을 백업·복구 문서 한 개를 만들고 README에 진입 경로를 제공한다. 접수 중지·Running: 0·동일 버전·덮어쓰기·원본 복사·check 실패 시 복구·OK 전 시작 금지 조건과 명령을 보존한다. 기존 작업 등록 안내를 복사하거나 변경하지 않는다. |
| ko-docs-start-requirement | README에서 Python 3.9 조건을 3.11 이상으로 갱신하고 의존성 설치 → 실행 → 확인 결과를 연결한다. 종료 코드 0/1·리터럴 비교·입력 무변경을 보존하고 기존 입력 참조를 유지한다. |
| ko-docs-partial-scope | 설치 항목의 Node.js 요구 버전만 수정한다. 요청 밖의 작업 메모·구조 설명을 포함해 나머지를 그대로 둔다. |
| ko-docs-explicit-inclusion | 사용자의 명시적 검증 항목·문장을 포함하고 실행에 필요한 사실을 보존한다. 변수명 변경 과정과 미정인 커밋 메시지는 자동으로 옮기지 않는다. |
| ko-docs-small-project | 하나의 README에 용도·Python 조건·명령·결과·읽기 오류·입력 무변경을 담고 상세 문서를 추가하지 않는다. |
| ko-docs-prior-decision | 전달된 유효한 문서 목적·경로·범위를 이어받아 옵션 참조만 갱신한다. 필요한 대상 파일 확인은 허용하되 문서 배치를 다시 묻거나 전체 문서 탐색을 되풀이하지 않는다. |
| writing-fluent-ko-docs-mixed-change | 같은 입력의 Writing 단독 사례와 의미·범위·파일 배치 계약을 유지한다. Fluent가 표현을 다듬으면서 선별되지 않은 작업 메모를 README에 복원하지 않는다. |

변경 전·후 지침의 비교에는 동일한 입력, 모델, 설정, 도구와 초기 파일을 사용하고 매번 새 문맥과
임시 루트에서 시작한다. 초기·최종 파일 내용과 생성·수정·삭제 목록, 응답, 읽은 지침과 도구 이력을
함께 보관한다. 대조군 출력을 변경 지침 실행에 넘기지 않는다. 위 표의 판정 기준과 기대값
메타데이터는 생성자에게 주지 않고 생성이 끝난 뒤 적용한다.

README의 길이만 비교하지 않는다. 파일 diff와 실제 설명을 읽어 필요한 안내·명령·조건이 남고
불필요한 README 변경·새 문서·중복 설명이 줄었는지 판정한다. 두 조건 모두 통과하면 해당 입력에서
계약이 유지됐다고 보고하며, 출력 차이 없이 개선됐다고 주장하지 않는다. 임시 파일에 실제로 쓰지 않고
초안만 반환했다면 그 결과는 초안 평가로 구분하고 파일 갱신 성공으로 보고하지 않는다.

기존 `ko-short`·`ko-rewrite`·`ko-partial`·`ko-summary`·`en-readme`·고정 PR 양식과 Workflow 단독
3개도 회귀 대상으로 유지한다. 사례 등록이나 JSON 파싱은 동작 평가가 아니며 실제 실행 기록이 없는
추가 사례는 `not_run`이다.

모든 조합에서 없는 플러그인을 설치하거나 필수 조건으로 요구하지 않고, 각 지침을 같은 초안에
반영한다. 파일 읽기 횟수 자체를 적용 횟수로 세지 않는다. 사실·형식·의미·범위를 직접 읽어 판정하고,
정답 문장이나 문장 수를 임의로 고정하지 않는다.

한 agent가 여러 사례를 수행한 명시적 지침 적용 smoke는 native 자동 선택이나 독립적인 통계
표본이 아니다. 보고한 참조 목록도 실제 runtime selection trace와 구분한다. 자동 선택은
별도 native 세션의 trace가 있어야 판정할 수 있다. 생성 미완료·오염·실패는 `not_run` 또는
`inconclusive`로 남긴다. 원출력·snapshot·hash·실행 정보는 Git에서 제외한 검증 경로에 보관한다.

자동 선택은 [스킬 라우팅 사례](../skill-routing/cases.json)의 일반 Writing 사례와
`writing-developer-blog-*` 사례로 별도 확인한다. 고정한 설치 inventory의 description과
요청을 노출하고 `expected_sequence`·`must_*` 등 판정 메타데이터와 명시적 `entry_skill`은 제공하지
않는다. 영속 문서·짧은 문장, 개발자 블로그 산출물, 일반 기술 설명과 블로그 작성법 조사의 경계를 확인하고,
짧은 수정·TIL에 문서 탐색·Engineering 계획이나 continuity가 추가되는지는 실제 이력에서 구분한다.

## 패키지 설치

별도의 임시 Codex 설정 루트에 로컬 마켓플레이스를 등록하고 Writing만, Fluent만, Workflow만,
세 플러그인을 함께 설치한다. 설치된
패키지·스킬·참조·hook 목록과 `writing:write-developer-blog` 발견 여부를 확인한다. 실제 사용자 설치·설정은 검증용으로 교체하지 않는다.
설치·inventory 성공, 명시적 작성 사례, 자동 선택·원어민 평가를 구분해 보고한다.
