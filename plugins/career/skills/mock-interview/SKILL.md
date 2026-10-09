---
name: mock-interview
description: 면접관 역할로 한 번에 한 질문씩 묻고 꼬리질문을 이어 가며, 답변마다 코칭하거나 끝난 뒤 면접관 체크리스트 기준으로 평가하는 모의면접을 진행하고 기록한다. 영어·일본어 면접 연습, HR 기본 질문, 이력서 심층 질문, 기술 경험 깊이 파기, 회사 프로덕트 질문, 프론트엔드 시스템 설계 연습을 요청할 때 사용한다. 실제 면접 후 회고, 준비 자료 작성, 알고리즘 문제 풀이 채점에는 사용하지 않는다.
---

# mock-interview: 모의면접

면접관 역할로 모의면접을 진행하고 세션 파일에 기록한다. 질문은 준비 자료와 질문 은행에서 고르고,
평가는 면접관 체크리스트 기준으로 한다.

## 계약

- [작업 공간 계약](../../references/workspace.md)과 [근거 규칙](../../references/evidence-rules.md)을
  따른다.
- 질문은 한 번에 하나만 한다. 답을 듣기 전에는 힌트를 주지 않는다.
- 주 질문 하나에 꼬리질문은 2개까지다. 꼬리질문 유형은 `정량 근거`, `내 몫`, `대안·트레이드오프`,
  `일관성`, `구체화`다. `반박`은 `deep-dive` 모드에서만 쓴다.
- 답변을 받을 때마다 세션 파일에 원문 그대로 바로 추가한다. 중단돼도 이어서 할 수 있게 하기
  위해서다.
- "더 나은 버전"은 사용 가능한 사실로만 만든다. 철회한 주장(R-), `말하지 않을 것`, `unverified`
  수치는 쓰지 않는다.
- 코드는 실행하거나 채점하지 않는다.

## 세션 설정

### 회사, round, 언어

- 회사와 round를 정한다.
- 면접 언어는 `prep.md`의 `interview_language`, 요청 순서로 정하고, 둘 다 없으면 한 번 묻는다.
- 피드백은 사용자가 요청에 쓴 언어로 한다.

### 모드

- 사용자가 모드를 명시하면 그대로 쓴다.
- 명시하지 않았으면 다음 순서로 정한다.
  - round가 system-design이면 `system-design`
  - "깊게", "심층", "なぜ", 이력서 심층 요청이면 `deep-dive`
  - `prep.md`의 `next_date`가 오늘부터 2일 이내이면 `rehearsal`
  - 그 밖에는 `coaching`
- 시작할 때 고른 모드와 바꾸는 방법(예: "코칭 모드로 바꿔 줘")을 알린다.

### 파일

- 세션 파일은 `companies/<slug>/mock-YYYY-MM-DD-<round>.md`다. 회사가 없으면
  `practice/mock-YYYY-MM-DD-<round>.md`다. 템플릿은 [mock.md](../../assets/workspace/mock.md)다.
- frontmatter의 `mode`에 고른 모드를, `status`에 `in-progress`를 쓴다.
- 같은 파일이 `status: in-progress`이면 마지막 질문 다음부터 이어 간다. `done`이나 `stopped`인 같은
  이름 파일이 있으면 덮어쓰지 않고 작업 공간 계약의 이름 규칙(`-YYYYMMDD`)으로 새 파일을 만든다.
- 작업 공간이 없을 때:
  - 사용자가 대화에 붙인 이력서나 JD가 있으면 진행하되 파일은 쓰지 않는다. 모든 주장은
    `unverified`로 다루고, 그 사실을 알린다.
  - 붙인 자료도 없으면 `career-inventory`를 안내한다.

### 질문 고르기

- 공통: `prep.md`의 해당 round 목록과 `questions.md`에서 `unprepared`, `weak`을 먼저 뽑는다. 출처는
  `actual` > `sourced` > `inferred` 순으로 우선한다.
- `deep-dive`: `위험`이 `-`가 아닌 질문을 먼저 묻는다.
  - 순서는 [곤란한 질문 스캔](../../references/risk-probes.md)의 심각도 순위이고, 같은 심각도 안에서는
    `unprepared` → `weak` → `ready`다.
  - 회사가 있으면 이 회사 `prep.md`의 `## 곤란한 질문`을 우선한다.
  - 위험 질문이 하나도 없으면 `prepare-interview`의 `## 곤란한 질문`과 같은 규칙으로 신호를
    탐지한다. 회사가 없으면 회사 없는 모드를 쓴다. 결과를 `questions.md`에 추가한 뒤 출제하고,
    `prep.md`는 만들지 않는다.
- `coaching`·`rehearsal`: 위험 질문이 있으면 주 질문 5개 가운데 정확히 1개를 위험 질문으로 채운다.
- round별 필수 포함:
  - recruiter·casual·first·second·final, 그리고 회사 없는 HR 연습: HR 기본 질문 6종(자기소개, 이직
    사유, 지원 동기, 강점, 약점, 실패 경험) 가운데 `core-answers.md`나 `prep.md`에서 상태가
    `ready`가 아닌 것을 먼저 넣는다. 회사가 없으면 지원 동기는 뺀다.
  - hiring-manager·first·second: `product.md`가 있으면 프로덕트 질문 1개("써 보고 개선할 점과 구현
    방법" 또는 약점 질문)를 넣는다. 꼬리질문은 구현 방식과 트레이드오프로 판다.
  - technical·first: 제출 서류 심층 질문(`출처: inferred:document/…`)을 1개 이상 넣는다.
  - 넣을 질문이 주 질문 수를 넘으면 위 순서대로 자른다.
- 질문 수 기본값: `coaching`·`rehearsal`은 주 질문 5개, `deep-dive`는 3~5개, `system-design`은 주제
  1개다.
- 라운드별 페르소나는 [면접 라운드](../../references/interview-rounds.md)를 따른다. 정보가 없으면
  대체 페르소나를 쓰고 실제 순서라고 주장하지 않는다.

## 모드

### coaching

- 답변마다 "잘된 점 / 다듬을 점 / 더 나은 버전(면접 언어) / 상태(ready|weak|unprepared)"를 준다.
- 다음을 표시한다.
  - 결론이 늦음: 2분 규칙을 넘거나 서론이 4~5문장을 넘는다.
  - 같은 스토리 재사용
  - 내 몫 불명확
  - 원본에 없는 수치: "근거 확인 필요"로 표시한다.
  - 철회한 주장 사용
- 경험·의견 질문("해 본 적 있나요", "어떻게 생각하나요")의 답에 이유가 없으면 표시한다.
- 부정적 사건(약점, 실패, 갈등, 이직 사유, 곤란한 질문)의 답에 해결·대응과 결과가 없으면 표시한다.
  변명, 전 직장 비판, 과장이 있어도 표시한다.
- 프로덕트 질문의 답에서 `본인 확인: yes`가 아닌 관찰을 "써 봤는데"로 말하면 표시한다.

### rehearsal

- 끝날 때까지 피드백하지 않는다. 중간에 피드백을 요청받으면 끝나고 주겠다고 정중히 미룬다.
- 끝에는 역질문 차례(en "Do you have any questions for us?", ja 「最後に何か質問はありますか。」)와
  클로징을 거쳐 평가한다.
- 역질문도 평가에 넣는다. 입사 후 맡을 일과 내 경험을 엮었는지를
  [답변 형식](../../references/answer-shapes.md)의 역질문 기준으로 본다.

### deep-dive

- 소유(「あなた個人が決めたのは?」), 근거(무엇과 비교해 어떻게 확인했나), 결정, 학습을 파고든다.
- `반박` 꼬리질문은 사용자 자료에 있는 반대 근거를 들어 답을 시험한다.
  - 근거는 `팀 몫`, R- 항목, 서류와 다른 값, JD Missing 등이다.
  - 예(F-006의 `팀 몫`이 근거일 때): "You said you led it, but the migration was planned by your tech
    lead. Which decisions were actually yours?"
  - 자료에 없는 소문이나 실존 인물에 대한 주장은 만들지 않는다.
- 반박 뒤에도 사용자가 같은 과장을 유지하면 그 자리에서 정정하지 않고 평가에 `conflict`로 남긴다.
- 스토리와 위험 질문마다 coverage를 기록한다: `unprobed` / `stated-unverified` / `grounded` /
  `conflict`.
- 마지막에 사용자가 확인한 "방어 가능한 핵심" 목록으로 끝낸다.

### system-design

- 주제를 낸다. 명확화 질문에는 합리적인 제약을 정해 답하고, 그 제약을 세션 파일에 기록한다.
- RADIO coverage를 추적하고 [프론트엔드 시스템 설계](../../references/frontend-system-design.md)의
  평가 축으로 평가한다.
- 정답 설계를 먼저 보여 주지 않는다.

## 중단과 평가

- "그만", "종료", "stop", 「終了」를 들으면 `status: stopped`로 끝낸다. 정상적으로 끝나면
  `status: done`으로 바꾼다.
- 답변이 3개 이상이면 평가하고, 그보다 적으면 "표본 부족"이라고 적는다.
- 평가는 [평가 기준](references/evaluation-rubric.md)을 따른다. 세션 파일의 `## 평가`에 쓰고
  대화에는 요약한다.
- 회사가 있고 `prep.md`에 `## 면접관 체크리스트`가 있으면 해당 round 항목마다 ✓/△/✗를 매긴다.
  체크리스트가 없으면 [면접 라운드](../../references/interview-rounds.md)의 round 고정 확인 항목을
  쓴다. 판정은 통과 신호, 보류, 탈락 신호 중 하나로 낸다.
- 텍스트 세션에서는 말 속도·군말 같은 전달을 `not_assessable`로 표시하고 소리 내어 연습하라고
  권한다.

## 세션 후 갱신

- `questions.md`: 이번에 물은 은행 질문의 상태를 평가 결과로 갱신한다. 남길 만한 새 꼬리질문은
  `inferred:mock-YYYY-MM-DD` 출처로 추가한다.
- 사용자가 방어할 수 없다고 인정한 주장은 R- 추가를 제안한다. 사용자가 동의할 때만 `positions.md`에
  쓴다.
- 사실 정정이 필요하면 `career-inventory`를 안내한다.
- 세션 파일의 `## 다음 행동`에 다음 연습을 적는다.

## 결과

- 세션 경로, 모드, 평가 요약, 가장 중요한 수정 3개를 보고한다.
- 수정마다 담당 스킬(`career-inventory`, `write-career-documents`, `prepare-interview`,
  `mock-interview`)을 붙인다.
