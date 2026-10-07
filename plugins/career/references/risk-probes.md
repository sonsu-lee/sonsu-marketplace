# 곤란한 질문 스캔

사용자 자료에서 면접관이 파고들 지점을 찾아 질문으로 바꾼다. 신호가 걸린 질문만 만들고, 자료에 없는
약점을 상상해 만들지 않는다.

`prepare-interview`가 탐지해 질문 은행에 넣고, `mock-interview`의 `deep-dive`가 먼저 출제한다.
`write-career-documents`는 서류 범위 신호만 결과 보고에 쓰고, `interview-retro`는 받은 질문에 위험
코드를 붙일 때 아래 정의를 쓴다. 질문 은행의 `출처`와 `위험` 값은 [작업 공간 계약](workspace.md)을,
사실의 사용 가능 여부는 [근거 규칙](evidence-rules.md)을 따른다.

## 신호 표

심각도 순위는 표의 순서로 고정한다. 정렬할 때는 순위가 작은 코드가 먼저다.

|코드|심각도 순위|탐지 규칙|확인하려는 것|질문 예(en / ja)|보완 skill|
|---|---|---|---|---|---|
|`inconsistency`|1|`facts.md`와 `documents/`·`companies/*/` 서류 사이, 또는 서류끼리 조직 기간·직함·수치가 다르다. 서류가 없으면 탐지하지 않는다.|신뢰성|"Your resume says X, but your other document says Y." / 「書類ではXですが、Yとも書かれていますね」|`write-career-documents`|
|`retracted-temptation`|2|R- 항목마다 하나. 과장을 유도하는 질문을 만든다.|과장 여부|"Did you lead that migration?" / 「その移行はご自身が主導したのですか」|없음(답변 연습)|
|`ownership`|3|(a) 스토리나 서류에 쓰인 F- 가운데 `내 몫`이 `미상`인 사실, 또는 (b) 사용 여부와 상관없이 R-의 `관련`에 걸린 F-.|개인 기여|"What exactly did you decide, versus your team?" / 「ご自身が判断したのはどこですか」|`career-inventory`|
|`unverified-number`|4|서류·스토리에 쓰인 수치의 F- 상태가 `self-reported`이거나, 서류에 `[VERIFY:`가 남아 있다.|측정 근거|"How did you measure that?" / 「その数値はどう計測しましたか」|`career-inventory`|
|`jd-missing`|5|`jd.md` 대응표에서 must 요구사항이 Missing 또는 Unknown이다.|요구 역량 공백|"Have you used GraphQL in production?" / 「本番環境でGraphQLを使った経験はありますか」|없음(정직한 답변과 학습 계획)|
|`short-tenure`|6|끝난 O- 재직 기간이 12개월 미만이다.|정착성|"Why did you leave after five months?" / 「なぜ半年で退職されたのですか」|없음|
|`gap`|7|연속한 O- 기간 사이, 또는 `basics.md`의 마지막 학력 종료와 첫 O- 시작 사이가 3개월 이상 비어 있다.|공백기의 이유|"What were you doing between March and October 2022?" / 「2022年3月から10月までは何をされていましたか」|없음|
|`seniority-gap`|8|JD 직무명에 Senior, Staff, Lead, Principal, シニア, リード 중 하나가 있고, 최신 O- 직함에는 같은 등급 단어가 없다.|레벨 적합성|"This is a senior role. What have you owned end to end?" / 「シニア職ですが、最初から最後まで責任を持ったものは何ですか」|`career-inventory`|
|`thin-skill`|9|서류의 Skills나 活かせる経験에 적힌 기술 가운데 그 기술을 `기술`에 가진 사용 가능 F-가 1개 이하다.|기술 깊이|"How deep is your experience with X?" / 「Xはどの程度使い込んでいますか」|`write-career-documents`(삭제 검토) 또는 `career-inventory`|
|`psr-gap`|10|서류·답변에 쓰인 스토리 가운데 `약점`이 비어 있지 않거나 Situation·Result가 비어 있다.|문제의식이나 결과|"Why was that a problem?" / "What was the outcome?" / 「なぜそれが問題だったのですか」 / 「結果はどうなりましたか」|`career-inventory`|
|`stale-tech`|11|JD must 기술을 뒷받침하는 F-의 마지막 기간이 오늘보다 3년 이상 전에 끝났다.|최신성|"When did you last use X?" / 「Xを最後に使ったのはいつですか」|없음|
|`career-change`|12|엔지니어 직함(engineer, developer, エンジニア, 개발 포함) 앞에 엔지니어가 아닌 직함의 O-가 있다.|전향 동기|"Why did you switch to engineering?" / 「なぜエンジニアに転向したのですか」|없음|
|`no-failure-story`|13|`역량`에 failure나 conflict가 있는 S-가 없다.|실패를 다루는 방식|"Tell me about a time you failed." / 「失敗した経験を教えてください」|`career-inventory`|
|`work-authorization`|14|market이 us이고 `취업 자격`에 sponsorship이나 not authorized가 있다. 또는 market이 jp이고 `취업 자격`에 체류 자격 갱신·변경이 필요하다는 기재가 있다.|고용 가능성|"Will you require visa sponsorship?" / 「在留資格の変更や更新は必要ですか」|없음(`positions.md` 문장 사용)|
|`ai-assisted`|15|F-의 `기술`이나 본문에 AI, LLM, Copilot, Claude, coding agent, 生成AI 중 하나가 있다.|품질 보증과 자력|"How do you verify AI-generated code? Could you have built it without AI?" / 「AIが生成したコードはどう検証していますか。AIなしでも作れましたか」|없음|
|`leaving-reason`|16|항상 하나 만든다.|이직 동기와 재발 위험|"Why are you leaving now?" / 「なぜ今転職を考えているのですか」|없음|

회사 정보가 필요한 신호는 `jd-missing`, `seniority-gap`, `stale-tech`, `work-authorization`(market
필요)이다. 회사 없이 탐지할 때는 이 네 개를 뺀다.

## 질문을 만드는 규칙

- 질문은 면접 언어로 쓴다. 근거로 ID(O-/P-/F-/S-/R-, 서류 파일 위치, `jd.md` 대응표 행)를 남긴다.
- 질문 예는 형태만 보여 준다. 실제 질문은 걸린 신호의 근거 값(기간, 기술 이름, 주장)을 넣어 만든다.
- "피할 답"과 "답변 방향"은 [답변 형식](answer-shapes.md)의 부정적 사건 형식(인정 → 사실 →
  해결·대응과 결과 → 지금/다음)을 따른다. 답변 방향에는 쓸 수 있는 사실만 쓴다.
- private 사실의 내용을 질문 문장에 넣지 않는다. anonymize 사실은 `공개 표기`로만 쓴다.

## 범위

이 목록에 없는 신호는 만들지 않는다. 부적절·위법 질문(나이, 출신, 가족 등)은 이 파일에서 다루지
않는다.
