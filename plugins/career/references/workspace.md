# 작업 공간 계약

Career 플러그인의 다섯 스킬은 이 파일 하나를 함께 따른다. 작업 공간은 사용자 데이터이며 이
저장소에는 없다. 산출물에 쓸 수 있는 사실의 범위는 [근거 규칙](evidence-rules.md)이 정한다.

## 레이아웃

```
<root>/                       기본값 ./career
├── profile/
│   ├── facts.md              경력 원본: O-/P-/F- 항목
│   ├── stories.md            STAR+R 스토리: S- 항목
│   ├── basics.md             연락처·학력·자격·언어·취업 자격
│   ├── positions.md          조건 답변·말하지 않을 것·철회한 주장(R- 항목)
│   └── core-answers.md       HR 기본 질문 답변(자기소개·이직 사유·강점·약점·실패 경험)
├── questions.md              질문 은행: Q- 항목 표
├── documents/                맞춤 전 기본 서류
├── practice/                 회사 없이 진행한 모의면접
└── companies/<slug>/
    ├── jd.md                 공고 원문 + `## 요구사항 대응`
    ├── product.md            프로덕트 분석: 관찰(U- 항목)·개선 제안·약점 질문 답변
    ├── prep.md               면접 준비
    ├── <document>.md         맞춤 서류(resume-en.md 등)
    ├── mock-YYYY-MM-DD-<round>.md
    └── interview-YYYY-MM-DD-<round>.md
```

## 루트 탐색

다음 순서로 작업 공간 루트를 찾는다.

1. 사용자가 지정한 경로
2. `./career/profile/facts.md`가 있으면 `./career`
3. `./profile/facts.md`가 있으면 `.`

셋 다 없으면 각 스킬에 정한 처리를 따른다. 루트를 만드는 일은 `career-inventory`가 맡고,
`interview-retro`는 사용자가 동의할 때 같은 구조를 만든다. 나머지 스킬은 멈추거나 파일 없이
진행한다.

## ID 규칙

| 접두어 | 대상 | 유일 범위 |
|---|---|---|
| `O-001` | 조직 | 작업 공간 |
| `P-001` | 프로젝트 | 작업 공간 |
| `F-001` | 사실 | 작업 공간 |
| `S-001` | 스토리 | 작업 공간 |
| `Q-001` | 질문 | 작업 공간 |
| `R-001` | 철회한 주장 | 작업 공간 |
| `U-001` | 프로덕트 관찰 | 회사 폴더 |

- 새 ID는 같은 접두어의 최댓값에 1을 더하고 세 자리로 맞춘다.
- ID는 재사용하지 않는다. 항목을 지우거나 철회해도 그 번호는 다시 쓰지 않는다.

## 날짜와 회사 slug

- 기간은 `YYYY-MM`, 사건은 `YYYY-MM-DD`로 쓴다.
- 회사 slug는 소문자 ASCII와 하이픈만 쓴다.
  - 일본어 이름은 헵번식으로 로마자화하고 법인 표기(株式会社, Inc. 등)는 뺀다. 예:
    `pksha-technology`.
  - 애매하거나 기존 slug와 겹치면 사용자에게 한 번 묻는다.

## 고정 어휘

모든 템플릿과 스킬은 아래 값을 그대로 쓴다. 다른 값을 만들지 않는다.

| 필드 | 값 |
|---|---|
| 사실 `상태` | `confirmed`(확인 자료를 `출처`에 기록) · `self-reported`(사용자가 구체적으로 말했지만 자료 없음) · `unverified`(문서에서 옮겼거나 모호함) |
| 사실 `공개` | `public` · `anonymize`(`공개 표기`만 사용) · `private`(어떤 산출물에도 쓰지 않음) |
| 스토리 `역량` | ownership, impact, technical-depth, performance, collaboration, conflict, leadership, mentoring, failure, ambiguity, learning, customer-focus |
| 질문 `분류` | recruiter, motivation, behavioral, resume-deep-dive, tech-experience, tech-fundamentals, system-design, company, conditions |
| 질문 `상태` | `unprepared` · `weak` · `ready` |
| 질문 `출처` | `actual:<slug>/<YYYY-MM-DD>/<round>` · `sourced:<URL>` · `inferred:<근거 한 줄>`. 곤란한 질문 스캔으로 만든 질문은 `inferred:risk/<위험 코드>/<근거 ID들>`(예: `inferred:risk/ownership/F-006`) |
| 질문 `위험` | `-` 또는 [곤란한 질문 신호](risk-probes.md)의 위험 코드 하나 |
| round | recruiter, hiring-manager, technical, system-design, behavioral, onsite, casual, first, second, final |
| market / 면접 언어 | `us` / `jp`, `en` / `ja` |
| 회사 `status` | researching, applied, interviewing, offer, closed |
| 프로덕트 관찰 `관찰자` | `본인`(사용자가 직접 사용) · `agent`(에이전트가 브라우저로 사용) · `공개 자료`(리뷰·릴리스 노트·문서, URL 필수) |
| `core-answers.md` 키 | `self-intro`, `leaving-reason`, `strengths`, `weaknesses`, `failure` |

질문 `출처`가 여러 개면 `; `로 잇는다.

## 쓰기 규칙

- 작업 공간 루트 안에만 쓴다. 사용자가 다른 경로를 지정한 경우는 예외다.
- 사용자가 파일 쓰기를 금지하면 결과를 대화로만 낸다.
- `documents/`와 `companies/<slug>/`의 서류, `mock-*`, `interview-*` 파일은 덮어쓰지 않는다.
  - 같은 이름이 있으면 `-YYYYMMDD`를 붙인 새 파일을 만들고, 같은 날 또 겹치면 `-YYYYMMDD-2`로
    만든다.
  - 사용자가 특정 파일을 고치라고 명시하면 그 파일만 고친다.
- `facts.md`, `stories.md`, `positions.md`, `core-answers.md`, `questions.md`, `product.md`는
  계속 갱신하는 파일이므로 제자리에서 고친다.
  - 사실 값을 바꿀 때는 지우지 않고 그 항목 아래에
    `- 변경: YYYY-MM-DD <이전> → <새 값> (<이유>)`를 추가한다.
- 지원서 제출, 메일 발송, 외부 양식 입력은 하지 않는다.

## 템플릿

새 파일은 아래 템플릿을 복사해 만든다. 템플릿에는 frontmatter, 제목, 필드 이름과 빈 예시 행
하나만 있다. 제목·필드 이름은 한국어로, 파일 이름·frontmatter 키·어휘 값은 ASCII로 쓴다.

- [facts.md](../assets/workspace/facts.md) → `profile/facts.md`
  - frontmatter `type: career-facts`, `updated`.
  - `## 조직` 표: `ID | 조직 | 기간 | 고용 형태 | 직함 | 공개 | 공개 표기`.
  - `## 프로젝트`: `### P-001 <이름>` 아래에 `조직`, `기간`, `개요`, `규모`, `역할`, `담당 공정`,
    `기술 환경`, `공개`, `공개 표기`.
    - `규모`는 `전체 N명 / 팀 N명`으로 쓰고 반올림하지 않는다.
    - `담당 공정`은 要件定義/基本設計/詳細設計/実装/テスト/運用保守마다 `●`(주담당), `○`(일부),
      `–`(없음)을 쓴다.
    - `기술 환경`은 언어/FW·라이브러리/DB/인프라·클라우드/도구로 나누고 버전을 포함한다.
  - `## 사실`: `### F-001 <한 줄 요약>` 아래에 `프로젝트`, `기간`, `내 몫`, `팀 몫`, `수치`,
    `출처`, `기술`, `상태`, `공개`, `공개 표기`, `메모`. `수치`는 이전 → 이후와 측정 방법·시점을
    쓰고, 없으면 `없음`이라고 쓴다.
- [stories.md](../assets/workspace/stories.md) → `profile/stories.md`
  - `### S-001 <제목>` 아래에 `역량`, `사실`(F- 목록), `Situation`, `Task`, `Action`,
    `해결·대응`, `Result`, `Reflection`, `15초`, `60초`, `2분`, `#### 답변`, `예상 꼬리 질문`,
    `약점`, `사용 기록`.
  - `해결·대응`은 문제가 생겼을 때 내가 한 행동이다. 없으면 `-`로 둔다. 역량에 failure나
    conflict가 있는 스토리는 비울 수 없다.
  - `#### 답변`에는 `en-60s`, `ja-60s` 같은 언어별 답변을 필요할 때 추가한다.
  - `약점`에는 PSR(Problem·Solution·Result) 가운데 빈칸을 적는다.
- [basics.md](../assets/workspace/basics.md) → `profile/basics.md`
  - 이름(언어별 표기), email, 전화, 링크(GitHub/LinkedIn/포트폴리오), 거주 도시·국가, 학력,
    자격(정식 명칭·취득 연월), 언어 능력(시험·레벨).
  - `취업 자격`은 문장으로 쓰고 `공개`를 `public`, `ask`, `private` 중 하나로 둔다.
  - 履歴書 전용 필드(ふりがな, 생년월일, 주소, 사진 유무)는 `## 履歴書 전용`에 따로 둔다.
- [positions.md](../assets/workspace/positions.md) → `profile/positions.md`
  - `## 조건 답변`: 희망 연봉 범위와 근거, 현재 연봉 공개 여부, 입사 가능 시기, 근무 형태·원격,
    근무지, 비자 지원 필요 여부마다 `en`/`ja` 문장.
  - `## 말하지 않을 것`: 표 `표현 | 이유 | 대신 쓸 표현`.
  - `## 철회한 주장`: `- R-001 "<주장>" (<맥락>). 관련: F-…. 이유: … 올바른 표현: …`.
- [core-answers.md](../assets/workspace/core-answers.md) → `profile/core-answers.md`
  - frontmatter `type: career-core-answers`, `updated`.
  - 키마다 `## <키>` 섹션(5개 고정) 아래에 `연결`(F-/S-), `이유`, `해결·대응`, `상태`,
    `### en`(15s, 60s), `### ja`(15秒, 60秒).
  - `이유`는 strengths에서 그 강점이라고 판단한 근거다. `해결·대응`은 weaknesses·failure·
    leaving-reason에서 내가 한 행동과 결과다. `상태`는 `unprepared`, `weak`, `ready` 중 하나다.
  - 지원 동기는 회사마다 다르므로 여기에 두지 않고 `prep.md`에 둔다.
- [questions.md](../assets/workspace/questions.md) → `questions.md`
  - 표 `ID | 질문(원문) | 언어 | 분류 | 출처 | 상태 | 받은 횟수 | 연결(S-/F-) | 위험`.
- [jd.md](../assets/workspace/jd.md) → `companies/<slug>/jd.md`
  - frontmatter `company`, `role`, `market`, `source_url`, `product_url`, `captured`.
  - `## 원문`에는 공고를 붙여넣은 그대로 둔다.
  - `## 요구사항 대응` 표: `요구사항 | JD 표기(공고 문구 그대로) | 구분(must/nice) | 연수 요구(없으면 -) | 판정(Matched/Missing/Unknown) | 근거(F-/S-)`.
- [product.md](../assets/workspace/product.md) → `companies/<slug>/product.md`
  - frontmatter `company`, `product`, `url`, `checked`.
  - `## 개요`: 무엇을, 누구에게, 핵심 사용자 흐름 3개와 출처 URL.
  - `## 시도 기록`: 에이전트 브라우저 사용 결과. `done` 또는 `not_run: <이유>`와 날짜.
  - `## 관찰`: 표 `ID | 관찰 | 관찰자 | 근거(화면·URL·날짜) | 본인 확인(yes/no)`.
    `관찰자: 본인`이면 `본인 확인`은 항상 yes다.
  - `## 사용 체크리스트`: 사용자가 직접 해 볼 흐름과 기록할 점.
  - `## 개선 제안`: `### U-001 <제목>`마다 `사용자 영향`, `원인 가설`(추정으로 표시), `해결안`,
    `구현 방식`, `트레이드오프`, `효과 측정`, `내 근거`(F-/S-).
  - `## 약점 질문 답변`: 면접 언어 답변과 사용한 U- ID.
- [prep.md](../assets/workspace/prep.md) → `companies/<slug>/prep.md`
  - frontmatter `company`, `role`, `market`, `interview_language`, `status`, `next_round`,
    `next_date`.
  - 섹션: `## 전할 메시지`, `## 면접관 체크리스트`, `## 라운드별 준비`(round마다 `###`),
    `## HR 기본 질문`, `## 제출 서류 심층 질문`, `## 곤란한 질문`, `## 약점과 대응`, `## 역질문`,
    `## 조건 답변`, `## 준비 계획`, `## 직전 15분 요약`, `## 다음 라운드 예상`.
  - 프로덕트 분석은 `product.md`에 두고 `prep.md`에서는 링크만 건다.
- [mock.md](../assets/workspace/mock.md) → `companies/<slug>/mock-YYYY-MM-DD-<round>.md` 또는
  `practice/mock-YYYY-MM-DD-<round>.md`
  - frontmatter `company`, `round`, `mode`, `language`, `date`, `status`
    (`in-progress`, `done`, `stopped`).
  - 섹션: `## 진행`(`### Q1`, `### Q1-1 [꼬리: <유형>]` 형식, 답변은 원문 그대로), `## 평가`,
    `## 다음 행동`.
- [interview.md](../assets/workspace/interview.md) →
  `companies/<slug>/interview-YYYY-MM-DD-<round>.md`
  - frontmatter `company`, `round`, `date`, `format`, `interviewers`(역할만), `result`
    (`pending`, `passed`, `rejected`, `unknown`), `input_source`(`recall`, `transcript`).
  - 섹션:
    - `## 받은 질문`: 표 `# | 질문 | 내 답 요지 | 자기 판정 | 분류 | 위험 | 연결`
    - `## 내가 한 역질문`: 표 `역질문 | 기준 충족(yes/no) | 면접관 반응`
    - `## 들은 정보`
    - `## 소감`
    - `## 갭과 조치`
    - `## 반복 취약 영역`
