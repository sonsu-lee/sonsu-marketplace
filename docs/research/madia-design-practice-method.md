# Madia Designer 디자인 실무 관찰 방법

- Status: Active research protocol
- Last reviewed: 2026-09-17

## 목적과 경계

Madia Designer의 공개 영상을 하나씩 관찰해 디자이너가 실제로 무엇을 보고, 어떤 판단을 하고,
무엇을 바꾸며, 결과를 어떻게 확인하는지 분해한다. 이 코퍼스는 개인 실무 관찰 자료이며 UX 표준이나
제품별 정답이 아니다. 제목·설명·썸네일만으로 원칙을 만들지 않고, 영상 전체와 화면 수정 전후를
확인하지 않은 항목은 `pending`으로 유지한다.

공개 채널의 무료 영상만 대상으로 한다. 유료·멤버십·비공개 자료를 우회하지 않으며 전체 자막,
영상, 썸네일을 저장하지 않는다. 저장하는 근거는 짧은 요약, timestamp와 공개 URL뿐이다.

## 분석 단위

영상 하나를 곧바로 원칙 하나로 바꾸지 않는다. 영상 안에서 다음 항목이 함께 관찰되는 구간을
`evidence_unit` 하나로 기록한다.

1. `project_id`: 화면이나 작업 흐름이 속한 프로젝트를 구분하는 안정적인 연구 식별자
2. `problem`: 디자이너가 발견한 문제
3. `action`: 실제로 수행한 수정 또는 작업
4. `rationale`: 그 행동을 선택한 이유
5. `visible_effect`: 수정 뒤 화면이나 과업에서 확인되는 변화
6. `user_task`: 변화가 지원하는 사용자 과업
7. `decision_stage`: 정보, 표현, 상태, 상호작용 등 판단 단계
8. `evidence_kind`: `verbalized`, `demonstrated`, `inferred`, `metadata_only`

`timestamp_start`, `timestamp_end`, `source_locator`를 필수로 남긴다. 말로 설명한 내용과 화면에서
직접 보여준 행동을 구분하고, 분석자의 해석은 `inferred`로 낮춘다. `metadata_only`와 `inferred`는
원칙 반복 횟수에 포함하지 않는다.

## 실행 순서

1. `shared/design-quality/madia-source-manifest.json`에 고정한 채널 ID·canonical URL·uploads
   playlist·공개 관련 playlist를 discovery 계약으로 사용한다. uploads와 채널 feed 항목은 해당
   채널 소유로 검증하고, 관련 playlist에만 있는 영상은 watch page의 `externalChannelId`가
   manifest의 채널 ID와 일치할 때만 합친다. 카탈로그의 `channel`과 `discovery_sources`도 이
   manifest와 정확히 일치해야 한다.
2. 20개 파일럿은 long-form, short, 시청자 첨삭, 따라 만들기, 도구·정보 영상이 섞이도록
   층화한다. 선택 규칙과 목록을 분석 전에 기록한다.
3. 두 코더가 파일럿을 독립적으로 분류한다. 관련성, `decision_stage`, `evidence_kind`의 Cohen's
   kappa가 0.70 미만이면 코드북을 고치고 파일럿을 다시 코딩한다.
4. 본 분석은 frozen queue 순서로 진행한다. 관련 영상은 전체를 보고 evidence unit을 남기며,
   비관련·중복 영상은 이유와 함께 `excluded`, 접근 불가는 이유와 함께 `blocked`로 남긴다.
5. 본 분석의 20% 이상을 독립적으로 이중 코딩한다. 합의 전 kappa가 0.75 미만이면 승격을
   중단하고 코드북과 이미 분석한 영향 범위를 재검토한다. M3를 통과시킬 때는 계산값뿐 아니라
   코더별 판정, 불일치, 합의 전 값과 계산 결과가 담긴 `pilot_evidence`와
   `production_evidence` 파일을 함께 남긴다. 각 파일은 `madia-coder-evidence-v1` JSON이며
   `phase`, 정확히 두 코더, `population_size`, 고유 `unit_id`별 `relevance`·`decision_stage`·
   `evidence_kind`의 코더별 판정을 기록한다. validator는 세 차원의 Cohen's kappa를 다시 계산해
   그 최솟값을 선언한 kappa와 비교하고, 본 분석 레코드 수를 `population_size`로 나누어 이중
   코딩 비율을 다시 계산한다. 임의의 텍스트 파일이나 선언값만으로는 M3를 통과할 수 없다.
6. 반복되는 행동을 원칙 후보로 묶되 동일 영상·동일 프로젝트의 반복 편집을 독립 사례로 세지 않는다.
7. 후보를 외부 표준·heuristic·제품 연구와 대조하고, 적용 조건·예외·검증 행동으로 변환한다.
   외부 근거는 `id`, `title`, canonical HTTPS `url`, `source_type`을 가진 레코드로 기록한다.
   같은 카탈로그 영상이나 그 영상의 다른 URL을 외부 근거로 재사용하지 않는다. 외부 근거는
   후보를 만든 직접 관찰과 독립된 출처에서 조건·예외·검증 행동을 뒷받침해야 한다.
8. 실제 스킬에 넣기 전 behavior fixture에서 기대 행동과 금지 행동을 평가한다. P3에는
   fixture·run·artifact revision, 기대 행동, 금지 행동, 실제 관찰과 근거 파일을 묶은 실행 receipt가
   있어야 하며 선언만으로 M7을 통과시키지 않는다. receipt의 `observed`는 모든 `expected`를
   포함해야 하고 금지 행동 `must_not`과 겹치면 안 된다. 즉 `expected ⊆ observed`이면서
   `observed ∩ must_not = ∅`인 실행 결과만 `passed`로 인정한다. `failed`·`blocked`·
   `inconclusive` receipt는 실제 실패 관찰을 그대로 보존하며 성공 oracle을 충족한 것처럼 꾸미지
   않는다.

현재 카탈로그의 대부분은 게시일이 없어 임의의 연대순을 만들 수 없다. 파일럿 이후 본 분석 queue는
JSON 원장의 배열 순서를 고정하고, 목록 갱신으로 새 영상이 추가되면 기존 순서를 바꾸지 않고 뒤에
추가한다. 새 영상이 발견되면 코퍼스 완결성 주장이 깨지므로 M0–M8을 모두 `not_run`으로 되돌리고,
기존 승격 후보는 P0·`validation_status: not_run`으로 내리며 production reliability 근거도
무효화한다. queue 규칙을 바꾸면 변경 이유와 영향 범위를 별도 근거로 남긴다.

## 원칙 승격 수준

| 수준 | 필요한 근거 | 사용 범위 |
| --- | --- | --- |
| P0 | 하나 이상의 후보 관찰 | 연구 메모만 가능 |
| P1 | 비중복 직접 관찰 3건 이상, 서로 다른 프로젝트 2개 이상 | 사례·검토 질문으로만 사용 |
| P2 | P1과 독립된 표준·연구·제품 근거 | 조건부 heuristic 후보 |
| P3 | P2, trigger·inspect·decide·act·verify·예외, behavior 평가 통과 | 스킬의 실행 규칙 또는 gate 후보 |

P1·P2는 조언이나 탐색 질문으로는 쓸 수 있지만 차단 규칙으로 사용하지 않는다. P3도 모든 제품의
보편 법칙이 아니며 Design Decision Contract의 사용자·과업·환경·위험과 충돌하면 적용하지 않는다.
`independent_projects`는 작성자가 적는 주장으로만 인정하지 않고, 직접 관찰 evidence unit의 고유
`project_id` 수와 정확히 일치해야 한다.

## M0–M8 연구 게이트

| Gate | 합격 조건 |
| --- | --- |
| M0 | discovery가 완료되고 모든 목록 항목이 `analyzed`, `excluded`, `blocked` 중 하나로 닫힘 |
| M1 | 모든 `analyzed` 영상에 timestamped evidence unit이 있음 |
| M2 | 승격 근거가 metadata-only가 아니며 직접 관찰과 추론이 구분됨 |
| M3 | 파일럿 20개 이상, pilot kappa ≥ 0.70, 본 분석 이중 코딩 ≥ 20%, production kappa ≥ 0.75이며 코더 단위 근거 파일이 있음 |
| M4 | P1 이상 후보마다 직접 관찰 3건과 서로 다른 프로젝트 2개 이상 |
| M5 | P2·P3 후보마다 식별자·제목·canonical HTTPS URL·출처 유형이 있는 독립 외부 근거가 있음 |
| M6 | P3 후보가 trigger·inspect·decide·act·verify와 예외로 실행 가능하게 표현됨 |
| M7 | P3 후보의 behavior fixture 실행 receipt가 기대 행동을 유도하고 금지 행동을 피했음을 입증함 |
| M8 | 직접 관찰·추론·미확인을 과장하지 않는 최종 provenance audit를 통과함 |

게이트는 평균 점수로 상쇄하지 않는다. 필수 조건 하나라도 충족하지 않으면 해당 원칙의 승격을
중단한다. `accepted_risk`는 통과가 아니며, 접근 차단이나 미확인은 그대로 남긴다.
P1은 M0–M4, P2는 M0–M5, P3는 M0–M8이 모두 `passed`여야 한다. 따라서 전체 목록이 닫히기 전에는
관찰 후보를 기록할 수는 있어도 승격 원칙으로 게시하지 않는다.

## 스킬 반영 계약

P3 후보를 반영할 때는 “예쁜 결과” 같은 문장 대신 `trigger → inspect → decide → act → verify`로
작성한다. 같은 변경에 다음을 함께 추가한다.

- 적용되는 Design Quality gate와 실패 상태
- behavior fixture의 기대 행동과 금지 행동
- 직접 관찰 occurrence ID, 독립 근거와 예외
- 기존 스킬 규칙과 충돌할 때의 우선순위

카탈로그와 요약은 다음 명령으로 정합성을 검사한다.

```bash
python3 scripts/validate_madia_design_catalog.py docs/research/madia-design-practice-catalog.json
python3 scripts/update_madia_design_catalog.py --check
```
