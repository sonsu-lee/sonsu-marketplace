# 일본어 문어 지침 A/B 사전 측정 계약

2026-09-06. 생성 실행 전에 fixture, 두 스킬 snapshot, 러너, 판정 rubric과 이 계약의 hash를 고정한다. 이 평가는 연구에 근거해 작성한 **고정 사전등록 세트**이며 held-out 세트가 아니다. 구현자와 문항 작성자는 규칙과 문항을 열람할 수 있었다.

## 표본과 실행

- 신규 문항은 8개 family별 5개, 합계 40개다. 그중 유지 16개, 모호성 보존 8개를 포함한다. 기존 generation 10개를 더해 총 50개다.
- 8개 family: 보조동사/본동사, 형식명사/실질명사, 한자·허용 표기·분야 용어, 한자어/고유어와 문체, 한국어와 일본어의 어의, `的`과 품사, `する`·자타·조사, 모호성과 보호 문자열.
- `gpt-5.6-sol`, 요청 reasoning `medium`, 각 문항·각 arm 2회로 총 200회 생성한다. 같은 문항의 두 반복은 AB/BA 순서를 상쇄하며 문항 순서는 고정 seed로 무작위화한다. 동시 실행은 최대 4개다.
- 모델에는 prompt/evidence와 해당 arm의 컴파일된 SKILL 본문만 평가 입력으로 제공한다. 숨긴 expectations/review_points/target_ok는 판정 단계에만 제공한다.
- 호스트가 공통으로 넣는 기본 스킬 설명과 global AGENTS가 남으면 두 arm의 공통 context hash가 일치해야 한다. 다른 Fluent 본문이 섞이거나 생성 중 tool call이 발생하면 inconclusive다. 이를 순수 격리라고 부르지 않는다. debug 입력 검사는 실제 서비스에 전송된 exec 전체 입력의 byte-level 증명이 아니다.
- native 자동 선택·파일 로딩은 따로 두 routing 사례로 측정한다. 주입 A/B 결과와 합산하지 않는다.

## 판정과 합산

- 같은 고정 LLM rubric으로 3회 독립 실행한다. 사람 평가자 3명이 아니며 모델 오류가 상관될 수 있다. judge 모델과 effort도 `gpt-5.6-sol`, `medium`이다.
- 각 판정의 X/Y 위치를 seed로 섞고, 실제 arm명·스킬 본문·출처 식별자는 judge에게 주지 않는다. case prompt/evidence, hidden 의미·대상 rubric, 두 출력만 전달한다.
- `semantic_ok`: 제공된 의미·귀속·조건·극성·불확실성·의무가 보존됐는가. `target_ok`: 해당 문항의 용례·표기·문체 목표를 충족했는가. `overcorrection`: 원문에 맞는 표현을 불필요하게 바꿔 의미·기능·표기 계약을 손상했는가. 의미가 같은 다른 문장은 정답으로 허용한다.
- 유효한 세 판정의 이진 항목은 2표 이상으로 정한다. 선호도는 X/Y/tie 중 2표 이상이 없으면 uncertain이다. 판정 실패·누락을 부정적인 품질 결과로 치환하지 않는다.
- **주 지표**는 문항별 target_ok이다. 문항마다 두 반복의 target_ok 합(0–2)을 arm별로 구하고, candidate 합이 크면 win, 작으면 loss, 같으면 tie로 분류한다. 양쪽 반복의 판정이 모두 있는 문항만 합산한다. decisive 문항만 분모로 양측 exact sign test를 계산하고, tie·누락 수를 별도로 보고한다.
- 전체 선호는 보조 지표다. 두 반복 모두 candidate 우세면 candidate win, 모두 baseline 우세면 baseline win, 그 밖은 tie/반복 불일치다. 반복 결과를 독립 문항 100개로 세어 추론하지 않는다.
- judge 선호의 pairwise agreement와 만장일치 수를 보고한다. 충돌은 majority/tie 규칙으로 남기며 사후 재판정으로 유리한 결과만 선택하지 않는다.

## 채택·회귀 기준

- 코드·literal·제목·marker 순서·code block의 exact 검사는 별도 hard gate다. semantic 오류와 함께 신규 candidate 위반이 하나라도 있으면 회귀 후보를 원문과 대조하고 미해결 위반을 통과로 쓰지 않는다.
- 각 family에서 candidate의 overcorrection 수가 baseline보다 늘면 해당 family의 회귀를 표시한다. 신규 위반을 해결하려면 새 candidate hash로 새 실험을 시작한다. 이미 생성한 결과는 그대로 보존한다.
- 개선이 통계적으로 확인됐다는 표현은 주 지표에서 win > loss, 양측 p < 0.05이고 신규 미해결 exact/semantic 위반 및 family별 overcorrection 증가가 없을 때만 쓴다. 그렇지 않으면 관측 차이·동률·판정 한계를 보고한다. 명시된 연구 근거가 있다는 사실만으로 출력 개선을 주장하지 않는다.
- 이 표본은 목적에 맞춰 구성한 작은 진단 세트다. p 값이 작아도 일본어 전체의 선호나 일반적인 생산성 향상을 증명하지 않는다. 원어민 검토가 없으면 beta를 유지한다.

## 실패·재실행

- timeout은 최대 600초, process group을 종료한다. 빈 최종 출력, 종료 실패, 완료 event 누락, 도구 사용 또는 판정 JSON 오류는 각각 실행 오류·timeout·inconclusive로 남긴다. 행동 pass율의 분모에 실패 실행을 넣지 않는다.
- 자동 재시도는 하지 않는다. 별도 재실행이 필요하면 원래 실패 기록을 보존하고 새로운 manifest/run directory에서 수행한다. 완료되지 않은 측정을 pass라고 표시하지 않는다.
- raw JSONL·출력·명령·시간·usage·판정은 저장소 밖에 보존한다. 요청한 모델/effort와 관측 metadata를 분리하며, 관측되지 않은 값은 unknown이다. 토큰 합계를 구독 quota 사용률로 해석하지 않는다.
