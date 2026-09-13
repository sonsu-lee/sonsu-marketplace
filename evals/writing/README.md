# Writing·Fluent·Workflow 분리와 조합 검증

Writing의 공통 구성, Fluent의 한국어·일본어·영어 표현, Workflow의 티켓·PR 양식·운영을
각각 단독으로 사용하거나 함께 적용할 때의 범위를 검증한다. 원어민 선호나 일반적인 품질 개선을
입증하는 실험은 아니다. 과거 Fluent의 고정 protocol·snapshot·결과도 새 조합의 근거로 재표기하지 않는다.

## 결정론적 검사

```sh
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 scripts/render-continuity.py --check
python3 -B -m unittest -v evals/task-continuity/test_runtime.py evals/plugin-compat/test_compat.py evals/language-style/test_eval.py evals/fluent-japanese/test_eval.py
```

JSON·frontmatter와 세 패키지의 스킬/참조 상대 경로를 확인한다. Fluent의 한국어 지침은 기존 언어별 규칙과 의미·조건·적용 범위를 대조한다.
원어 용례·보호 문자열과 법적 고지는 기존 main의 바이트를 기준으로 보존 여부를 확인한다. Workflow의 티켓 3종 본문도 기존 main과 같아야 한다.
PR 기본 양식과 `unverified` 시 기본형을 확정하지 않는 정책, marker·연결 문법은 별도로 검토한다.
continuity 검사는 각각의 Fluent·Writing 기록을 실제 helper로 만들고 서로 대신 복구하지 않는지 확인한다.

Fluent 내부 스킬 생성기와 공통 continuity 생성기는 유지한다.
Writing에서 Workflow로 지침·양식을 복사하는 생성기는 없다.
양식 수정은 Workflow에서, 언어 지침 수정은 Fluent에서 한다. 각 플러그인의 링크·경로와
생성 결과 검사는 실제 모델의 지침 적용을 증명하지 않는다.

## 명시적 지침 적용 사례

- [`cases.json`](cases.json): 10개. Writing 단독 7개, Fluent 단독 3개.
- [`workflow-cases.json`](workflow-cases.json): Workflow 단독 3개.
- [`composition-cases.json`](composition-cases.json): Writing+Fluent 5개, Workflow+Fluent 2개,
  Workflow+Writing 1개, 세 플러그인 함께 1개.

각 사례의 `installed_plugins`를 해당 실행의 유일한 관련 inventory로 취급한다. 고정한 패키지에서
`entry_skill`과 실제 필요한 참조를 읽고 요청을 수행한다. 제공된 양식·조회 결과는 테스트 fixture이며
추가 원격 조회·게시·설치는 하지 않는다. 각 사례의 실제 출력과 적용한 스킬·참조 경로를 남기고,
생성자에게 아래 판정 기준이나 과거 출력·판정을 주지 않는다.

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

모든 조합에서 없는 플러그인을 설치하거나 필수 조건으로 요구하지 않고, 각 지침을 같은 초안에
반영한다. 파일 읽기 횟수 자체를 적용 횟수로 세지 않는다. 사실·형식·의미·범위를 직접 읽어 판정하고,
정답 문장이나 문장 수를 임의로 고정하지 않는다.

한 agent가 여러 사례를 수행한 명시적 지침 적용 smoke는 native 자동 선택이나 독립적인 통계
표본이 아니다. 보고한 참조 목록도 실제 runtime selection trace와 구분한다. 자동 선택은
별도 native 세션의 trace가 있어야 판정할 수 있다. 생성 미완료·오염·실패는 `not_run` 또는
`inconclusive`로 남긴다. 원출력·snapshot·hash·실행 정보는 Git에서 제외한 검증 경로에 보관한다.

## 패키지 설치

별도의 임시 Codex 설정 루트에 로컬 마켓플레이스를 등록하고 Writing만, Fluent만, Workflow만,
세 플러그인을 함께 설치한다. 설치된
패키지·스킬·참조·hook 목록을 확인한다. 실제 사용자 설치·설정은 검증용으로 교체하지 않는다.
설치·inventory 성공, 명시적 작성 사례, 자동 선택·원어민 평가를 구분해 보고한다.
