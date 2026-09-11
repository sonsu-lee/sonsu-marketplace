# Writing 통합 검증

Fluent Languages를 Writing으로 이전하면서 바뀌는 작성 범위·참조 구조와 Workflow의 독립 실행
경계를 검증한다. 과거 Fluent 평가와 별도 계약이며 원어민 선호나 보편적인 글 품질을 입증하는 실험은 아니다.

## 결정론적 검사

```sh
python3 scripts/render-writing.py --check
python3 scripts/render-continuity.py --check
python3 scripts/render-claude-compat.py --check
python3 -B -m unittest -v evals/writing/test_projection.py
python3 -B -m unittest -v evals/task-continuity/test_runtime.py
claude plugin validate . --strict
claude plugin validate plugins/writing --strict
claude plugin validate plugins/workflow --strict
```

`test_projection.py`는 저장소 밖의 임시 경로에서 생성 CLI를 실행한다. 작성 원본의 바이트 보존,
누락·수동 변경·오래된 생성 파일 감지, `--check`의 무변경, 원본 누락 시 쓰기 전 실패,
source·destination symlink 경계와 실제 두 패키지의 스킬 상대 링크를 확인한다.
생성 사본은 안내 comment 뒤에 정본을 그대로 포함하며, Writing의 MIT 고지도 Workflow에 함께
생성한다. 작성 지침은 Writing에서 고친다.

continuity 검사는 새 namespace의 실행과 이전 Fluent 기록을 자동으로 섞지 않는 경계를 포함한다.
JSON·frontmatter·경로 검사는 내용의 문장 품질이나 실제 스킬 선택 검사가 아니다.

## 작성 사례

[`cases.json`](cases.json)의 10개 입력은 Writing의 짧은 답변, 자유 재작성, 부분 수정, 버그 티켓,
일본어 고정 PR 양식·의미, 영어 README·주석, 동료 메시지와 절차 요약을 다룬다.
[`workflow-cases.json`](workflow-cases.json)의 3개는 Writing 없이 제공된 사실로 초안을 만드는
Workflow, PR 양식 `unverified`와 고정 양식·연결 문법을 다룬다. 실제 원격 대상이 아닌 테스트 자료다.

새 context에서 고정한 패키지의 주 스킬과 선택된 참조를 적용하고 입력마다 실제 출력과 읽은
참조 경로를 남긴다. 생성자에게 아래 판정 기준이나 이전 출력·판정을 주지 않는다.
생성 완료 후 별도 평가자가 사실·형식과 요청 범위를 대조한다. 표현의 정답 문자열을 요구하지 않는다.

| 사례 | 판정 기준 |
| --- | --- |
| ko-short | 한 문장 수정만 반환하고 양식·질문·계획을 추가하지 않는다. |
| ko-rewrite | 자유 초안을 문단으로 재구성하며 두 번 발생·원인 미확인·다른 형식 미확인을 유지한다. |
| ko-partial | 세 제목과 요청 밖의 문구를 그대로 두고 현상 문장만 바꾼다. |
| ko-bug | 현상·재현 정보 기본형, 임시 초안, 원인·방법·완료조건을 만들지 않는다. |
| ja-fixed-pr | 지정 제목·순서·marker·Part of 행과 실기 미확인을 보존하고 기본 제목을 더하지 않는다. |
| ja-meaning | 기록 없음·실제 행위자 불명·배정된 A의 실행 미확인을 서로 다른 사실로 유지한다. |
| en-readme | 용도→전제→명령→결과, Python 3.9+, 원문 명령, 0/1 종료 의미와 입력 무변경을 보존한다. |
| en-comments | 원문 signature와 최초 일치·없으면 None·대소문자 구분을 모두 유지한다. |
| ja-message | 재현 조건 조사 요청과 어제 한 번·원인 미확인을 보존하고 기한·해결책을 만들지 않는다. |
| ko-summary | 실행 절차를 대체하지 않는 개요로 원본 링크·조건·복구 의미를 보존한다. |
| workflow-ticket-only | Writing 미설치로 중단하지 않고 3종 중 버그 기본형으로 알려진 사실만 쓴다. |
| workflow-pr-unverified | 양식 미확인을 부재로 바꾸어 기본형을 확정하지 않고, 실제 UI·첨부 미확인을 유지한다. |
| workflow-pr-fixed | 제공 양식과 marker·Part of URL을 보존하고 미확인 UI를 완료나 생략 가능한 자료로 바꾸지 않는다. |

한 agent가 여러 사례를 수행한 명시적 지침 적용 smoke는 native 자동 선택·참조 읽기 trace나
독립적인 통계 표본이 아니다. 런타임별 선택을 검증하려면 실제 Codex·Claude 세션의 trace로
따로 기록한다. 생성 실패·미완료·오염은 `not_run` 또는 `inconclusive`로 구분한다.
원출력·snapshot·파일 hash·runtime·실행 결과는 저장소 밖이나 무시된 로컬 검증 경로에 보관한다.

패키지 구조 변경에서는 각각 별도 임시 Codex 설정 루트와 Claude 설정 루트에 마켓플레이스를
등록하고 Writing만, Workflow만 설치한다. 설치된 스킬·참조·hook 목록과 패키지 파일을 확인한다.
사용자의 실제 설치 상태를 검증용으로 교체하지 않는다. 설치·inventory 성공은 모델 행동 성공과 구분한다.
