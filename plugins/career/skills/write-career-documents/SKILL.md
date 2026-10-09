---
name: write-career-documents
description: 경력 원본의 확인된 사실만으로 미국식 영문 resume, 履歴書, 職務経歴書를 작성·JD 맞춤·검토하고, 지원처가 요구할 때만 スキルシート를 만든다. 개발자 지원 서류를 새로 만들거나 특정 공고에 맞게 고치거나 기존 서류의 사실 근거·형식을 점검할 때 사용한다. 지원 서류가 아닌 일반 영어·일본어 문장 윤문, 경력 사실 수집, 면접 답변 준비에는 사용하지 않는다.
---

# write-career-documents: 지원 서류 작성

경력 원본에서 사용할 수 있는 사실만으로 지원 서류를 만들고, JD에 맞추고, 검토한다. 사실을
새로 만들지 않고 강조 순서와 단어 선택만 바꾼다.

## 계약

- [작업 공간 계약](../../references/workspace.md)과 [근거 규칙](../../references/evidence-rules.md)을
  따른다. 서류를 제출하지 않는다.
- 루트나 `facts.md`가 없으면 작성·맞춤 모드는 `blocked`로 멈추고 `career-inventory`로 경력
  원본부터 만들자고 안내한다.
- 검토 모드는 작업 공간 없이도 진행하되 결과에 `fact_trace: not_run`을 표시한다.
- 서류에는 독자가 둘이다. 모든 작성·검토는 두 독자를 함께 만족시켜야 한다.
  - 1차 독자는 서류 심사를 하는 HR이다. 개발을 잘 모르고, 개발팀에서 받은 요구사항
    체크리스트와 서류 문구가 일치하는지만으로 통과를 정한다.
  - 2차 독자는 1차 기술 면접관(현직 개발자)이다. 면접 직전이나 면접 중에 서류를 펼쳐 보고
    거기서 질문을 고른다.

## 요청 판정

문서 종류를 정한다.

- 요청에 문서 이름이 있으면 그대로 따른다.
- "이력서"만 있으면 미국·영문 맥락은 `resume-en`, 일본 기업·일본어 맥락은 `rirekisho-ja`와
  `shokumu-keirekisho-ja`로 정한다. 맥락이 없으면 한 번 묻는다.

모드를 정한다.

- 작성: JD가 없다. `documents/<document>.md`에 쓴다.
- 맞춤: JD나 회사가 주어졌다. `companies/<slug>/<document>.md`에 쓴다. 붙여넣은 JD는
  `jd.md`가 없을 때만 [jd.md 템플릿](../../assets/workspace/jd.md)으로 저장한다.
- 검토: 기존 서류가 주어졌다. 결과만 내고, 고쳐 달라고 할 때만 수정한다.

문서 파일 이름은 `resume-en`, `rirekisho-ja`, `shokumu-keirekisho-ja`, `skill-sheet-ja` 네 가지로
고정한다. 같은 이름의 파일이 있으면 작업 공간 계약의 덮어쓰기 금지 규칙을 따른다.

## スキルシート 조건

다음 중 하나에 해당할 때만 スキルシート를 만든다.

- (a) 사용자가 명시적으로 요청했다.
- (b) `jd.md`나 사용자가 준 응모 안내에 スキルシート, 技術経歴書, 指定フォーマット 제출이
  요구된다.
- (c) 사용자가 SES·フリーランス 案件 지원이라고 밝혔다.

(b)를 다른 서류를 맞추는 중에 발견하면 スキルシート도 함께 만들고, 결과에 그 근거 문장을
인용한다. 회사 지정 양식(열 목록이나 파일)이 있으면 그 열과 순서를 그대로 쓰고, 없으면
[スキルシート 기준](references/jp-skill-sheet.md)의 기본 구성을 쓴다.

## 근거 모으기

`facts.md`, `stories.md`, `basics.md`, `positions.md`를 읽고 사용 가능 집합을 만든다. 사용
가능 여부는 근거 규칙을 따른다. 제외한 사실과 제외 이유(unverified, private, 철회, 말하지 않을
것)를 따로 모아 결과에 보고한다.

## JD 대응표

맞춤 모드에서만 만든다.

- 요구사항을 must/nice로 나누고, `JD 표기`(공고 문구 그대로)와 `연수 요구`(없으면 `-`)를 적는다.
- 각 요구사항을 Matched(F-/S-), Missing, Unknown으로 판정한다. 인접 경험을 Matched로 올리지
  않는다.
- 결과를 `jd.md`의 `## 요구사항 대응`에 쓴다. 이미 있으면 갱신한다.

## HR이 보는 자리에 일치를 드러낸다

Matched 요구사항은 `JD 표기` 그대로의 단어가 HR이 훑는 자리에 최소 한 번 보여야 한다.

- HR이 훑는 자리:
  - `resume-en`: Summary, Skills, 최근 직무의 첫 bullet 2개
  - `shokumu-keirekisho-ja`: 職務要約, 活かせる経験・知識・技術
  - `rirekisho-ja`: 志望動機, 免許・資格
- 사용자의 표기가 다르면 JD 표기를 함께 쓴다. 예: "Core Web Vitals (INP)". 사실이 뒷받침하는
  범위에서만 쓴다.

연수 요구가 있는 기술과 문서의 주력 기술에는 경험 연수를 적는다.

- 계산: 그 기술이 `기술 환경`에 있는 P-의 기간과 `기술`에 있는 F-의 기간을 합집합으로 더한다.
  겹치는 달은 한 번만 센다. 진행 중이면 오늘까지 센다.
- 표기: en은 내림한 연수로 "N+ years", 1년 미만은 "N months"로 쓴다. ja는 「N年Mヶ月」로 쓴다.

Missing과 Unknown은 문구를 넣어 채우지 않는다. 맞춤이 아닌 작성 모드에서는 일반 명칭(React,
TypeScript 등)과 주력 기술의 연수를 같은 자리에 둔다.

## 작성

문서마다 해당 기준을 먼저 읽고 템플릿에서 시작한다.

|문서|기준|템플릿|
|---|---|---|
|`resume-en`|[미국식 resume](references/us-resume.md)|[resume-en](assets/resume-en.md)|
|`rirekisho-ja`|[履歴書](references/jp-rirekisho.md)|[rirekisho-ja](assets/rirekisho-ja.md)|
|`shokumu-keirekisho-ja`|[職務経歴書](references/jp-shokumu-keirekisho.md)|[shokumu-keirekisho-ja](assets/shokumu-keirekisho-ja.md)|
|`skill-sheet-ja`|[スキルシート](references/jp-skill-sheet.md)|[skill-sheet-ja](assets/skill-sheet-ja.md)|

- 근거 규칙의 `<!-- facts: … -->` 주석과 `[VERIFY: …]` 규칙을 지킨다.
- 기술 면접관을 위해 프로젝트와 주요 bullet마다 문제, 판단 이유(왜 그 방법을 골랐나),
  해결·대응, 결과가 보이게 쓴다. 판단 이유가 사실에 없으면 지어내지 않고 결과 보고에 "면접 전
  이유 정리 필요"로 남긴다.
- 문서 맨 위에 frontmatter를 둔다.
  - `type: career-document`
  - `document`: 네 가지 파일 이름 중 하나
  - `target`: `base` 또는 회사 slug
  - `created`: `YYYY-MM-DD`
  - `facts`: 사용한 ID 목록
  - `review`: `passed` · `findings` · `not_run`

## 검토 게이트

초안을 쓴 뒤 [검토 체크리스트](references/review-checklist.md)를 적용한다.

- 호스트가 하위 에이전트를 지원하면 새 검토 에이전트에게 초안 경로, `profile/` 파일 경로,
  체크리스트 경로만 넘긴다. 작성 과정의 대화는 넘기지 않는다.
- 하위 에이전트를 쓸 수 없으면 같은 세션에서 체크리스트를 순서대로 적용하고, 결과에 "독립 검토
  아님"을 적는다.

맞춤 모드에서는 HR 스크리닝 시뮬레이션을 항상 수행한다.

- 별도 검토 에이전트(없으면 같은 세션)에게 두 가지만 준다. `jd.md` 대응표에서 만든
  체크리스트(`JD 표기`, must/nice, `연수 요구`)와 frontmatter·HTML 주석을 지운 서류 본문이다.
  경력 원본과 작성 대화는 주지 않는다.
- 지시: "개발을 모르는 채용 담당자로서, 서류에 그 단어와 연수가 글자로 보일 때만 ✓를 준다.
  추론해서 ✓를 주지 않는다."
- 출력: 표 `항목 | ✓/✗ | 찾은 위치`.
- Matched인데 ✗인 항목은 `## HR이 보는 자리에 일치를 드러낸다`의 규칙으로 고치고 다시 돌린다.
  Missing은 ✗로 남겨 보고한다.
- 통과 기준: must 요구사항 가운데 Matched인 항목이 모두 ✓다.

검토 지적을 처리한다.

- 사실·형식 위반은 고친다. 판단이 필요한 지적은 사용자에게 넘긴다.
- 수정과 재검토는 최대 2회까지 하고, 남은 지적은 보고한다.
- 결과에 맞게 frontmatter의 `review`를 갱신한다.

## 결과

다음 내용을 보고한다.

- 만든 파일 경로, 사용한 사실, 제외한 사실과 이유, 남은 `[VERIFY:]`, JD에서 Missing인 항목
- `self-reported` 수치를 썼다면 "면접에서 측정 근거 질문에 대비할 것"
- PDF로 변환하기 전에 `<!-- facts: … -->` 주석과 frontmatter를 지워야 할 수 있다는 안내
- 검토 결과와 검토가 독립적이었는지 여부. 맞춤 모드에서는 HR 스크리닝 표도 붙인다.
- スキルシート를 (b) 조건으로 만들었다면 근거 문장 인용
- "이 서류가 부를 곤란한 질문"
  - 만들거나 검토한 서류에 [곤란한 질문 신호](../../references/risk-probes.md)의 서류 범위 신호를
    적용한다. 서류 범위 신호는 `inconsistency`, `retracted-temptation`, `ownership`,
    `unverified-number`, `thin-skill`, `psr-gap`이고, 맞춤 모드에서는 `jd-missing`이 더해진다.
  - 항목마다 코드, 근거 위치, 질문 한 줄을 적는다.
  - `questions.md`에는 쓰지 않고, 반영하려면 `prepare-interview`를 쓰라고 안내한다.
- 다음 행동 제안. 예: `career-inventory`로 F-005 확인.
