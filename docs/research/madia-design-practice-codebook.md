# Madia Designer 디자인 실무 관찰 코드북

- Codebook version: codebook-v1

## 1. 영상 관련성 `relevance`

| 코드 | 정의 |
| --- | --- |
| `direct_design_work` | 화면을 직접 만들거나 고치거나 특정 화면을 비평 |
| `design_explanation` | 화면 예시로 디자인 개념·원칙을 설명하지만 수정하지 않음 |
| `tool_or_workflow` | Figma 등 도구·작업 흐름 조작 중 디자인 판단이 등장 |
| `not_relevant` | 인터페이스 디자인 판단이 없음 (커리어, 브이로그, 잡담, 광고, 공지, 화면 예시 없는 Q&A) |

## 2. 판단 단계 `decision_stage`

근거 단위마다 하나를 붙인다. 기존 DQ와 1:1이다. 원칙 ID의 약어도 이 표의 순서를 따른다.

| 코드 | DQ | 약어 | 다루는 판단 |
| --- | --- | --- | --- |
| `task_context` | DQ1 | `TC` | 사용자·과업·판단 |
| `information_priority` | DQ2 | `IP` | 정보 우선순위·그룹·읽는 순서 |
| `visual_system` | DQ3 | `VS` | 위계·타이포그래피·색·간격·정렬·그리드·컴포넌트·토큰 |
| `state_content` | DQ4 | `SC` | 상태·실제 콘텐츠·극단값·현지화 |
| `feedback_recovery` | DQ5 | `FR` | 피드백·권한·오류·취소·복구 |
| `environment_accessibility` | DQ6 | `EA` | 기기·입력·접근성 |
| `artifact_structure` | DQ7 | `AS` | Figma 레이어·컴포넌트·변수·전달 구조 |
| `outcome_validation` | DQ8 | `OV` | 사용자 결과 검증 |

## 3. 근거 종류 `evidence_kind`

세 가지만 쓴다.

| 코드 | 조건 |
| --- | --- |
| `demonstrated` | 화면에서 실제로 바꾸는 전·후가 보이고 이유를 디자이너가 말함 |
| `verbalized` | 행동과 이유를 말로 설명했으나 화면에서 실행되지 않음 |
| `inferred` | 이유를 말하지 않아 분석자가 해석함. 화면 변화가 있어도 이유가 말해지지 않았으면 여기에 해당 |

## 4. 맥락 `context`

근거 단위마다 둘 다 필수다.

- `platform`: `web`, `mobile_app`, `desktop_app`, `cross_platform`, `unknown`
- `surface`: `landing_marketing`, `commerce`, `content_feed`, `form_input`, `dashboard_data`, `settings_account`, `navigation`, `component_system`, `portfolio_presentation`, `other`

## 5. 영상 수준 판정

코더 kappa용 판정이다.

- `relevance`: 1번 코드.
- `decision_stage`: 근거 단위 수가 가장 많은 단계. 동률이면 `timestamp_start`가 가장 이른 단위의 단계.
- `evidence_kind`: 근거 단위 수가 가장 많은 종류. 동률이면 약한 쪽을 고르며, 강도는 `inferred` < `verbalized` < `demonstrated`이다.
- 단위가 없는 제외 영상은 `decision_stage`와 `evidence_kind`를 `none`으로 쓴다.

## 6. 제외 사유 접두어

- `not_relevant: `
- `no_design_judgment: ` — 관련 영상이지만 근거 단위가 없는 경우
- `duplicate: ` — 9.2 중복 정리에서만 쓴다

제외는 전체 sheet와 자막을 본 뒤에만 판정한다. 제목만으로 제외하지 않는다.

## 7. 근거 단위 분할

- (문제, 행동) 쌍마다 단위 1개를 만든다. 대상 요소나 문제가 바뀌면 나눈다.
- 좋은 예시를 설명하는 장면도 단위로 남긴다. 이때 `problem`에는 그 선택이 피하려는 문제를 쓴다.
- 단위 ID: `<video_id>:<3자리 순번>`
- `source_locator`: `https://www.youtube.com/watch?v=<video_id>&t=<int(timestamp_start)>s`

## 8. 서술 필드와 발췌

- `problem`, `action`, `rationale`, `visible_effect`, `user_task`는 한국어 300자 이하로 쓴다.
- `speech_excerpt`는 `cues.json` 원문을 그대로 120자 이하로 발췌한다. 요약하지 않는다.
- `verbalized`와 `demonstrated`는 `speech_excerpt`가 필수다.
- `inferred`는 `rationale`을 `[해석] `으로 시작한다.
- `caption_source`가 `none`이면 모든 단위의 `speech_excerpt`는 `null`이다.

## 9. `project_id`

- 영상 안에서 다루는 작업물(제품·서비스·포트폴리오) 하나마다 `<video_id>:p<n>`을 붙인다. 같은 작업물의 여러 화면은 같은 `p<n>`을 쓴다.
- 영상 간 연결은 10.1에서만 한다.

## 10. 화면 근거 `visual_evidence`

모든 단위에 1개 이상 둔다.

- 필드:
  - `frame_time`: 단위 구간 안의 초.
  - `role`: `before`, `after`, `during`, `context` 중 하나.
  - `region`: 전체 프레임 기준 정규화 `[x, y, w, h]`. 지칭 대상이 화면 전체일 때만 `null`.
  - `observation`: 관찰 내용.
  - `legibility`: `clear`, `partial`, `unreadable` 중 하나.
- `demonstrated`는 `before`와 `after`가 각각 1개 이상 있어야 한다.
- before/after 시각 선택:
  1. 단위 구간 안에 있는 `scenes.json` 값 중, 서술한 속성 변화가 처음 보이는 값을 기준으로 삼는다. before는 그 직전 프레임, after는 그 직후 프레임이다.
  2. 구간 안에 장면 변화 값이 없으면, 구간 안의 후보 시각들을 `frame`으로 비교해 변화 직전·직후 프레임을 고르고 그 근거를 `observation`에 적는다.
  3. 어느 경우든 before/after 시각은 구간 안에서 고른다.
- 수치 기록 규칙:
  - 흐리거나 원근·확대로 왜곡된 화면의 숫자·간격·크기는 어떤 필드에도 쓰지 않는다.
  - 영상 픽셀을 CSS px나 Figma 값으로 환산하지 않는다. 편집기 속성 패널에 보이는 값만 그 단위와 함께 적는다.
- 변경 기록 규칙:
  - 배율·확대만 바뀐 전후는 디자인 변경으로 기록하지 않는다.
  - 여러 속성이 동시에 바뀌면 바뀐 속성을 모두 적고, 특정 속성이 효과를 냈다고 쓰지 않는다.

좌표는 유한수 4개이며 `0 ≤ x`, `0 ≤ y`, `0 < w`, `0 < h`, `x + w ≤ 1`, `y + h ≤ 1`을 만족해야 한다.

## 11. `confidence`

| 값 | 조건 |
| --- | --- |
| `high` | 모든 `visual_evidence`가 `clear`이고 대상·변화·발화가 분명함 |
| `medium` | 하나가 부분적으로 불분명함 |
| `low` | 그 외 |

## 12. 용어

`term_ids`는 `docs/research/design-terminology.json`의 `rejected`가 아닌 term ID에서만 고른다. 맞는 용어가 없으면 bundle의 `term_proposals`에 원문 표현과 제안 한국어·영어 명칭을 남긴다.

`term_ids`는 중복 없는 문자열 배열이며 빈 배열도 허용한다. ID는 `term.` 뒤에 소문자 영숫자와 하이픈으로 연결한 단어를 쓴다(`^term\.[a-z0-9]+(?:-[a-z0-9]+)*$`).

## 13. 역할별 작업 지시

아래 지시는 실행 계획 7.3–7.7의 역할별 문장을 그대로 따른다. 지시에서 0단계는 공통 규칙, 7.x는 파일럿 절차, 9.2는 중복 정리, 10.1은 연작 연결을 가리킨다. 공통 규칙과 실행 절차는 `docs/research/madia-design-practice-method.md`에도 정리한다. `<cache>`는 `MADIA_CACHE_DIR`이며, 없으면 `~/.cache/sonsu-marketplace/madia`이다.

### 13.1 coder

1. 코드북 전체를 읽는다.
2. `fetch.json`, `cues.json`, `scenes.json`을 모두 읽는다.
3. `sheets/`의 모든 이미지를 순서대로 `read`한다.
4. 근거 단위마다 `python3 scripts/madia_media.py frame`으로 원본 프레임을 뽑아 `read`한다. 시각은 코드북 10번 규칙으로 정한 before/after/context이고, 필요하면 `--crop`을 쓴다.
5. 코드북 규칙대로 `analysis-<coder>.json`을 쓴다. `session_id`는 자기 task 이름이다.
6. `python3 scripts/validate_madia_design_catalog.py --bundle <path>`가 OK일 때까지 고친다.
7. 같은 디렉터리의 다른 `analysis-*.json`, `verification*.json`, `superseded/`는 열지 않는다.
8. 경로와 OK만 보고한다.

### 13.2 adjudicator

1. 두 bundle과 원자료(cues, sheets, 프레임)를 다시 본다.
2. 불일치마다 근거로 지지되는 쪽을 고른다. 평균을 내거나 절충 문장을 만들지 않는다.
3. 다음 입력이 있으면 함께 읽는다.
   - 부분 재판정: superseded verification의 `exclusion_note`와 단위별 `note`
   - 7.9 사람 감사 메모: 메모가 지적한 항목에 한해, 원자료로 확인되면 두 코더 결과와 다르게 확정할 수 있다. 다르게 확정한 항목과 근거는 bundle `term_proposals`가 아닌 adjudication 보고에 남기고, 오케스트레이터가 `<cache>/<id>/adjudication-notes.md`로 저장한다.
4. `analysis-adjudicator.json`을 쓰고 `--bundle`로 검증한다. ratings는 최종 단위에서 계산한다.

### 13.3 verifier

1. 최종 bundle의 각 단위에서 `visual_evidence` 시각과 영역을 `frame`으로 다시 뽑아 `read`한다.
2. 코드북 14번의 다섯 검사를 판정하고, 15번 범위 안에서만 수정한다.
3. 판정 기준:
   - 모두 통과: `confirmed`
   - 허용 범위의 수정으로 맞춤: `corrected`
   - 판단할 수 없음: `held`
   - 원자료가 반박함: `rejected`
4. excluded bundle은 전체 sheet와 자막을 보고 `exclusion_confirmed`를 정한다.
5. 결과를 `<cache>/<id>/verification.json`에 쓴다. `verifier`에는 자기 task 이름을 넣는다. `--bundle <최종 bundle> --verification <cache>/<id>/verification.json`으로 검증한다.

`exclusion_confirmed:false`이면 부분 재판정한다(0단계 파일 교체 규칙). 같은 결과가 다시 나오면 다음과 같이 처리한다.
- 아직 `--pilot`으로 merge하지 않은 영상: 대체한다.
- 이미 `--pilot`으로 merge한 영상(7.8·7.9·8.6의 재코딩 중): 대체하지 않는다. 멈추고 사용자에게 보고한다.

검증 판정 정의는 다음과 같다.

- `target`: 영역 안에 발화·서술이 지칭하는 요소가 있다.
- `change`: 같은 배율·상태에서 전후가 서술대로 다르다.
- `speech`: `speech_excerpt`가 단위 구간 ±2초 cue 원문에 있다.
- `numbers`: `visible_effect`와 `observation`의 숫자가 프레임에서 판독된다.
- `attribution`: 이유의 출처 표기가 맞다.
  - `verbalized`·`demonstrated`: 구간 발화에 이유가 있어야 한다.
  - `inferred`: `rationale`이 `[해석] `으로 시작하고, 이유를 디자이너 발화로 돌리지 않아야 한다.

### 13.4 terminology steward

1. 입력: 이번에 merge한 영상의 카탈로그 단위, 그 영상들 최종 bundle의 `term_proposals`.
2. 원장에서 `occurrence_id`가 그 영상 ID로 시작하는 `observed_expressions`를 먼저 지운다.
3. 각 제안과 단위 `term_ids`를 다음 셋 중 하나로 처리한다. 대상은 카탈로그에 남은 단위뿐이다. verifier가 기각해 merge에서 빠진 단위를 가리키는 제안은 기각으로 처리한다.
   - 기존 term에 연결한다.
   - 새 `candidate` term을 만든다. 값은 다음과 같다.
     - `id`: `term.` + `en`의 kebab-case
     - `label_status`: `internal_preferred`
     - `definition`: `""`
     - `status_reason`: `"출처 확인 전"`
     - `review_by`: 원장 `as_of` + 1년
   - 기각한다. 원장은 바꾸지 않고 `<cache>/waves/<wave>/term-decisions.json`에 기록한다.
4. 처리 결과:
   - 원장에 새 term을 추가한다.
   - 연결된 (term, 단위) 중 `verification.status ∈ {confirmed, corrected}`인 단위마다, `speech_excerpt`나 화면 문구에서 실제로 쓰인 표현을 `observed_expressions`에 추가한다. `held` 단위는 추가하지 않는다.
   - 이번 영상들의 단위별 최종 `term_ids`를 `term_assignments` curation 파일 `<cache>/waves/<wave>/terms.json`으로 쓴다. 카탈로그에 있는 단위만 넣는다.
5. 오케스트레이터가 다음을 순서대로 실행한다.
   1. `python3 scripts/validate_design_terminology.py docs/research/design-terminology.json` (교차 검사 없이 원장 구조만 검증)
   2. `--apply-curation <cache>/waves/<wave>/terms.json`
   3. 0단계 용어 동기화
6. 앞 단계가 실패하면 뒤 단계는 실행하지 않는다. 5의 어느 단계든 실패하면 되돌린 뒤, 오류 출력을 준 새 steward 세션으로 1회 재실행한다.
   - 되돌리기: 오케스트레이터는 7.7 시작 시 원장, 카탈로그 JSON, 카탈로그 요약 MD를 `<cache>/waves/<wave>/before-<n>/`에 복사해 둔다(`n`은 같은 웨이브 안의 7.7 실행 순번). 재실행 전에 세 파일을 모두 복원한다.
   - 재실행도 실패하면 멈추고 사용자에게 보고한다.

`<wave>`는 파일럿에서 `pilot`, 본 분석에서 `wave-<NN>`이다. 단일 영상 re-merge 뒤에도 그 영상만 입력으로 이 7.7을 실행한다.

## 14. 검증 판정 정의

- `target`: 영역 안에 발화·서술이 지칭하는 요소가 있다.
- `change`: 같은 배율·상태에서 전후가 서술대로 다르다.
- `speech`: `speech_excerpt`가 단위 구간 ±2초 cue 원문에 있다.
- `numbers`: `visible_effect`와 `observation`의 숫자가 프레임에서 판독된다.
- `attribution`: 이유의 출처 표기가 맞다.
  - `verbalized`·`demonstrated`: 구간 발화에 이유가 있어야 한다.
  - `inferred`: `rationale`이 `[해석] `으로 시작하고, 이유를 디자이너 발화로 돌리지 않아야 한다.

`confirmed`·`corrected` 단위의 `checks`에는 항상 `target`·`attribution`, `demonstrated`이면 `change`, 발췌가 있으면 `speech`, `visible_effect`나 어떤 `observation`에 숫자가 있으면 `numbers`를 넣는다. `checks`는 비어 있지 않은 고유 검사명 배열이다. `corrected`·`held`·`rejected` 판정은 메모가 필수다. 카탈로그에는 기각된 단위를 남기지 않는다.

## 15. verifier가 수정할 수 있는 범위

- `timestamp_start`, `timestamp_end`
- `evidence_kind`: 낮추기만 가능
- `confidence`: 낮추기만 가능
- `rationale`: `"[해석] " + 원문`으로 바꾸기만 가능
- `speech_excerpt`: cue 원문과 같게 맞추기
- `visual_evidence`: 원소 수와 role 순서를 유지한 채 `frame_time`, `region`, `legibility`, `observation`만 바꾸기
- `term_ids`

이 밖의 수정이 필요하면 `held`와 메모로 남긴다.

## 개정 이력

16번 규칙: 버전, 날짜, 정의가 바뀐 코드 또는 규칙 번호, 이유, 재코딩 범위를 기록한다. 개정할 때 코드 식별자(1–4번의 코드값)는 추가·변경·삭제하지 않고, 정의와 규칙만 바꾼다. 검증기 enum은 그대로 유지된다.

| 버전 | 날짜 | 코드·규칙 | 이유 | 재코딩 범위 |
| --- | --- | --- | --- | --- |
| codebook-v1 | 2026-10-03 | 1–16 최초 정의 | 전편 화면·발화·맥락 분석과 독립 검증 기준 확정 | 최초 코딩 대상 전편 |
