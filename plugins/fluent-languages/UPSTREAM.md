# 원본 출처

Fluent Languages의 언어별 SKILL.md와 참고 자료는 직접 편집하는 독립 지침이다.

## 한국어

- [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean/tree/ce8683f0eba8cddb91de4dcd151425ff73e60498)의 한국어 output style을 SKILL.md에 복사하고 적용 범위·예시를 수정했다.
- [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/tree/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7)의 Codex용 humanize-korean 절차와 quick-rules·taxonomy·playbook·문헌·검증 자료를 references에 복사해 수정했다.

충돌하는 처방과 호스트 전용 절차는 [한국어 커스텀 기준](skills/fluent-korean/references/customization.md)에 따라 조정했다. 두 원본은 MIT이며 [저작권·라이선스 고지](THIRD_PARTY_NOTICES.md)를 유지한다. 원본의 문헌·코퍼스 주장을 로컬에서 독립 재현한 것은 아니다.

## `fluent-japanese`

- 저장소: <https://github.com/sonsu-lee/fluent-languages>
- 원본 commit: [`d53bf65057445b3556efb6d7d011d49ed8a5aac7`](https://github.com/sonsu-lee/fluent-languages/commit/d53bf65057445b3556efb6d7d011d49ed8a5aac7)
- 참고한 파일:
  - [`plugins/fluent-languages/skills/fluent-japanese/SKILL.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/plugins/fluent-languages/skills/fluent-japanese/SKILL.md)
  - [`docs/research/japanese-language-characteristics.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/docs/research/japanese-language-characteristics.md)
- 반영한 범위: 문맥에 따른 주어 생략, 행위자 전환 시 역할명 명시, 조사·서술어·논항 관계, 수식 범위, 문장 구조에 맞는 문장부호, 격식·용어 선택과 조건에 따른 명사화·수동태 점검이다.
- 로컬 변경: 행위자를 만들어 내거나 근거 없는 해석을 택하던 모호한 전후 비교 예시를 제거했다. 해당 언어의 보존 기준을 우선하며 기술·일반 일본어 설명문 모두에 적용한다.
- 제외한 범위: 코딩 전용 분리, 하위 에이전트 전용 절차, 고정 문장 길이, 일률적인 주어 복원과 능동태·동사형 우선 규칙이다.
- 검증 상태: 원본은 원어민 검토 전의 베타였다. 이 로컬 지침도 대표 모델 출력에 대한 일본어 원어민 검토를 마칠 때까지 베타 상태를 유지한다.

## `fluent-english`

- 저장소: <https://github.com/sonsu-lee/fluent-languages>
- 원본 commit: [`d53bf65057445b3556efb6d7d011d49ed8a5aac7`](https://github.com/sonsu-lee/fluent-languages/commit/d53bf65057445b3556efb6d7d011d49ed8a5aac7)
- 참고한 파일:
  - [`plugins/fluent-languages/skills/fluent-english/SKILL.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/plugins/fluent-languages/skills/fluent-english/SKILL.md)
  - [`docs/research/english-language-characteristics.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/docs/research/english-language-characteristics.md)
- 반영한 범위: 요청된 출력 언어에 따른 선택, 행위자·행동·대상 관계, 독자와 소프트웨어의 역할 구분, 대명사 지시 대상, 조건에 따른 능동태·직접적인 동사 사용, 명사 나열과 한정 수식어의 범위, 영어 변종·격식 보존, 문맥에 맞는 불완전 문장, 국제 독자 고려와 프로젝트 용어 일관성이다.
- 로컬 변경: 언어 공통 정보 순서는 Writing이 담당하고 영어 스킬은 자체 보존 기준을 유지한다. 코딩 전용 분리와 하위 에이전트 전용 표현을 제거해 기술·일반 영어 설명문 모두에 적용한다.
- 제외한 범위: 고정 SVO 출력, 일률적인 능동태·2인칭 사용, 기존 정보 우선·결과 우선을 영어 고유 규칙으로 취급하는 방식, 문장·수식어 수 제한, 특정 영어 변종 강제와 어휘만으로 작성 주체·품질을 판단하는 방식이다.
- 검증 상태: 원본은 원어민 검토 전의 베타였다. 이 로컬 지침도 대표 모델 출력에 대한 영어 원어민 검토 또는 동등한 편집 검토를 마칠 때까지 베타 상태를 유지한다.

## `no-ai-slop`

- 저장소: <https://github.com/petergyang/no-ai-slop>
- 원본 commit: [`000650b156983f5159695b441477f4e63b25dc85`](https://github.com/petergyang/no-ai-slop/commit/000650b156983f5159695b441477f4e63b25dc85)
- 참고한 파일:
  - [`skills/no-ai-slop/SKILL.md`](https://github.com/petergyang/no-ai-slop/blob/000650b156983f5159695b441477f4e63b25dc85/skills/no-ai-slop/SKILL.md)
  - [`skills/no-ai-slop/eval.md`](https://github.com/petergyang/no-ai-slop/blob/000650b156983f5159695b441477f4e63b25dc85/skills/no-ai-slop/eval.md)
- 반영한 범위: 요청된 어조 보존과 조건에 따른 최종 점검이다. 내용 없는 도입, 근거 없는 중요성·출처 표현, 같은 개념을 가리키는 동의어 교체, 상투적 대조, 제기되지 않은 반론, 쓰이지 않는 대안, 중복 결말과 두드러진 반복을 점검한다.
- 로컬 변경: 이 패턴은 작성 시점의 문맥에 따라 판단한다. 개별 단어·문장부호·구문 자체를 실패로 취급하지 않으며 의미, 실제 대안, 의도적인 반복, 안전 안내와 정착된 용어의 보존을 우선한다.
- 제외한 범위: 편집·탐지 모드, 필수 질문, 금지어 목록, 일률적인 능동태 사용, 무생물 주어 제한, `show, don't tell`의 절대 규칙화, 다른 문맥에 그대로 옮길 수 있는지 보는 검사, 문장부호 수 기준, 필수 `What changed` 출력과 반복 재작성 절차다.
- 근거 범위: 원본 `eval.md`는 자체 검토 목록이다. 실제 모델 출력이나 사람의 선호 연구 결과를 저장한 자료가 아니므로 그 존재만으로 동작 품질을 입증하지 않는다.

## `no-ai-slop-ja`

- 저장소: <https://github.com/53able/no-ai-slop-ja>
- 원본 commit: [`1773df932be3a13d576bfe15cc116720e6788323`](https://github.com/53able/no-ai-slop-ja/commit/1773df932be3a13d576bfe15cc116720e6788323)
- 해당 프로젝트가 명시한 원본: [`petergyang/no-ai-slop@d30eddb9e04562234f2070b5ee63ca4649d9a05e`](https://github.com/petergyang/no-ai-slop/tree/d30eddb9e04562234f2070b5ee63ca4649d9a05e)
- 참고한 파일:
  - [`skills/no-ai-slop-ja/SKILL.md`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/skills/no-ai-slop-ja/SKILL.md)
  - [`NOTICE`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/NOTICE)
  - [`tests/evaluation/README.md`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/tests/evaluation/README.md)
- 반영한 범위: 수동태, `こと`, 연속하는 `の`, 동사성 명사, 추상적인 가타카나어, 수식 범위, 드러나지 않는 행위자 변경, 과도한 경어와 반복 종결어미를 문맥 없이 오류로 취급하지 않는 기준이다. 최종 점검에는 상투적인 도입, 근거 없는 중요성 자평과 새 정보가 없는 결말에 대한 검토도 반영했다.
- 제외한 범위: 편집·탐지 모드, AI 작성 여부 판단, 필수 변경 요약, 점수 산정과 여러 단계의 재작성 절차다.

## `natural-japanese`

- 저장소: <https://github.com/coji/natural-japanese>
- 원본 commit: [`0f1cc1c5a4e2aa7590598c88a15c213a60d9545a`](https://github.com/coji/natural-japanese/commit/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a)
- 참고한 파일:
  - [`readability-principles.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/skills/natural-japanese/references/readability-principles.md)
  - [`writing-constitution.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/skills/natural-japanese/references/writing-constitution.md)
  - [`skill-eval-findings.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/corpus/reports/skill-eval-findings.md)
- 반영한 범위: 조건에 따른 수식어 순서, 실제 문장 구조의 경계에 맞춘 문장부호와 독자·정착된 용법에 따른 용어 선택이다.
- 제외한 범위: 결론 우선 구성, 결론을 담는 제목, 고정된 문단 역할, 수치형 문체 기준, 문서 유형 모드, lint 점수, 수렴할 때까지 반복하는 절차와 필수 결론 지시다.
- 근거 범위: 도입 당시 `natural-japanese`가 인용한 일본어 작문 서적과 정확한 페이지를 독립적으로 확인하지 않았다. 반영한 지침은 해당 저장소에 귀속하며, 서적에서 직접 확인한 근거로 제시하지 않는다.

## 검토했으나 반영하지 않은 자료

- [`j1nn0/skills@e762558662251e48b05de5c79f518e676ab97699`](https://github.com/j1nn0/skills/tree/e762558662251e48b05de5c79f518e676ab97699/skills/writing-ja)의 사실·추론·판단·어조 보존 기준을 검토했다. 당시 로컬 보존 지침이 이미 다루는 내용이므로 별도 실행 지침을 도입하지 않았다.
- [`devswha/patina@dd73aab0a1542db37b838cfe396b621e9ef1b928`](https://github.com/devswha/patina/tree/dd73aab0a1542db37b838cfe396b621e9ef1b928)는 패턴·평가 목록으로 검토했다. 점수 산정, 수치 기준, 재작성 절차와 초기 일본어 패턴은 반영하지 않았다.
- [`gonta223/humanizer-ja@a1e343696e43aa50e7218891f3319ab22cde3464`](https://github.com/gonta223/humanizer-ja/tree/a1e343696e43aa50e7218891f3319ab22cde3464)는 일반적인 일본어 표현 교정 패턴을 검토하는 데 참고했다. 사실·수치·경험·의견을 만들거나 불확실성을 바꾸고, 격식 변주나 형식 변경을 강제할 수 있는 규칙은 반영하지 않았다.
- [`blader/humanizer@e2e92e7b4b8229253ed5c8e81dc65463fdeddda5`](https://github.com/blader/humanizer/tree/e2e92e7b4b8229253ed5c8e81dc65463fdeddda5)는 영어 패턴 범위와 오탐 방지 기준을 검토하는 데 참고했다. 방대한 패턴 목록, 문장부호 규칙, 개성 추가, 편집 절차, 예시와 Wikipedia에서 유래한 문구는 반영하지 않았다.
- [`forjd/better-writing@dd9d0a50581a7652fb38f03b7b751741ed917993`](https://github.com/forjd/better-writing/tree/dd9d0a50581a7652fb38f03b7b751741ed917993)는 고정 입력, 결정적 검사와 블라인드 비교 설계를 검토하는 데 참고했다. 스킬 규칙, 테스트 코드, 고정 입력이나 결과는 반영하지 않았다.

위 검토 전용 저장소의 원문, 코드, 예시와 테스트 입력은 이 버전에 포함되지 않는다. 이후 도입한다면 정확한 원본 commit, 경로, 조정 범위와 라이선스 고지를 추가한다.

## 참고한 일본어 근거

- [일본 문화청, `公用文作成の考え方`](https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/93657201.html)
- [일본번역연맹, `JTF日本語標準スタイルガイド（翻訳用）第4.0版`](https://www.jtf.jp/pdf/jtf_style_guide.pdf)
- [Walker, Iida와 Cote의 일본어 담화·영형 대명사 연구](https://aclanthology.org/J94-2003/)
- [Mori, Nomura와 Nitta의 일본어 사용 설명서 영형 대명사 연구](https://aclanthology.org/W97-1302/)

이 자료들은 일본어 규칙의 적용 범위를 정하는 근거다. 이 스킬의 모델 출력이 원어민 검토를 통과했다는 근거는 아니다.

### 일본어 문어 표기와 한국어 번역 전이 (2026-09-06)

로컬의 문어 표기·번역 절은 여섯 가지 조건을 다룬다. 문서별 관례, 한자와 읽기의 범위, 보조·형식 용법과 실질 용법의 구분, 문맥에 따른 한자어·고유어 선택, 한국어를 일본어로 옮길 때의 뜻·품사·논항 구조, 한 번만 나타난 명확한 용법 오류의 교정이다. 금지어 목록, 한자 비율, 말뭉치 빈도 기준이나 구어 절차는 추가하지 않았다.

[조사 목록](../../docs/research/fluent-japanese-writing-catalog.md)은 문맥별 규칙·예시·반례 85개, 정확한 출처 위치, 원본·조정 예시 구분과 예외를 기록한다. JTF 가이드, 일본 문화청, Mochizuki (2010), Ishihara (2013), Ko (2017), Uematsu (2017), Liu (2017), Yoon (2012)와 당시 확인한 사전 항목을 참고했다. 문어 예시와 구어 자료, 범위가 정해진 편집 선호와 문법 오류, 실제 용례와 빈도 주장을 구분한다. 개별 BCCWJ 빈도 검색은 수행하지 않았다.

JTF에서 유래한 지침과 목록은 CC BY 4.0에 따라 출처를 표시한 로컬 재서술·조정본이며, 자세한 내용은 제삼자 고지를 참고한다. [평가 절차](../../evals/fluent-japanese/README.md)는 주입한 지침의 A/B 결과, 실제 플러그인 로딩과 일본어 원어민 검토를 구분한다. 모델 평가만으로 베타 상태를 해제하지 않는다.

## 참고한 영어 근거

- [WALS Online, 영어의 주어·목적어·동사 순서](https://wals.info/valuesets/81A-eng)
- [WALS Online, 영어의 대명사 주어 표현](https://wals.info/valuesets/101A-eng)
- [Google 개발자 문서 스타일 가이드, 능동태](https://developers.google.com/style/voice)
- [Google 개발자 문서 스타일 가이드, 대명사](https://developers.google.com/style/pronouns)
- [Google 개발자 문서 스타일 가이드, 국제 독자를 위한 작성](https://developers.google.com/style/translation)
- [Microsoft 작문 스타일 가이드, 동사](https://learn.microsoft.com/en-us/style-guide/grammar/verbs)
- [Microsoft 작문 스타일 가이드, 국제 독자를 위한 작성 요령](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips)
- [호주 정부 스타일 매뉴얼, 문장](https://www.stylemanual.gov.au/writing-and-designing-content/clear-language-and-writing-style/sentences)
- [Kobak 외, LLM을 활용한 생의학 글쓰기의 말뭉치 수준 초과 어휘 연구](https://doi.org/10.1126/sciadv.adt3813)
- [Liang 외, 영어 비원어민 글에 대한 GPT 탐지기의 편향 연구](https://doi.org/10.1016/j.patter.2023.100779)

기관의 스타일 가이드는 해당 기술 문서 관례에 관한 근거이며 보편적인 영어 문법을 정하지 않는다. 말뭉치·탐지기 연구는 문맥에 따른 최종 점검의 범위를 제한한다. 금지어 목록, 개별 작성 주체 판단이나 이 스킬의 출력이 자연스럽다는 주장을 뒷받침하지 않는다.

반영한 각 출처의 저작권·라이선스 원문은 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)에 보존한다.
