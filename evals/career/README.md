# Career 명시적 적용 검증

Career 플러그인의 다섯 스킬(`career-inventory`, `write-career-documents`, `prepare-interview`,
`mock-interview`, `interview-retro`)이 가상 작업 공간에서 근거 규칙과 작업 공간 계약을 지키는지
검증한다. 확인할 것은 사실 추적, 공개 범위, 철회한 주장 배제, 곤란한 질문 탐지, 질문 은행 환류,
프로덕트 분석의 `not_run` 처리다. 서류나 답변의 문장 품질, 원어민 선호, 실제 채용 결과를 입증하는
실험은 아니다.

## 결정론적 검사

```sh
find .agents plugins evals -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 scripts/render-agent-policy.py --check
python3 scripts/render-continuity.py --check
python3 scripts/render-claude-compat.py --check
python3 scripts/render-omp-compat.py --check
claude plugin validate . --strict
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
git diff --check
```

`"${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py"`가 있으면
`plugins/career/skills/` 아래 스킬마다 함께 실행한다. 이 검사는 JSON·frontmatter·생성물 일치만
확인하며, 스킬이 실제로 근거 규칙을 지키는지는 아래 사례를 실행해야 알 수 있다.

## 픽스처

[`fixtures/workspace/`](fixtures/workspace/)는 `plugins/career/references/workspace.md`의 구조를 따른
가상 작업 공간이다. 사람·회사·수치는 모두 가상이며 `.invalid` 도메인은 접속할 수 없다.

- `profile/facts.md`
  - O-001 Acme Mart(2023-04 – 현재, Frontend Engineer), O-002 Bright Labs(2022-10 – 2023-02, Junior
    Frontend Developer). O-002는 5개월 재직(`short-tenure`)이고, 학력 종료(2022-03)와 O-002 시작
    사이가 3개월 이상 비어 있다(`gap`).
  - P-001 Checkout rewrite: 전체 12명 / FE 4명.
  - F-001 CI 13분 → 4분(confirmed), F-002 p75 INP 480ms → 190ms(confirmed, anonymize), F-003 주니어
    코드 리뷰(self-reported), F-004 Project Nightjar(private), F-005 번들 40% 감소(unverified),
    F-006 App Router 이전 20페이지 중 3페이지(confirmed, tech lead 주도).
  - 어떤 F-에도 AI 관련 기술이 없다. `ai-assisted`가 탐지되지 않아야 하는 음성 대조군이다.
- `profile/positions.md`: R-001 "I led the App Router migration", 말하지 않을 것 「テックリード」,
  면접에서 먼저 말하지 않을 연봉 하한선.
- `profile/stories.md`: S-001(F-001), S-002(F-002). failure·conflict 스토리는 없다(`no-failure-story`).
- `profile/basics.md`: Jordan Lee / リー ジョーダン. 취업 자격 "Authorized to work in Japan; requires
  visa sponsorship for US roles"(`public`).
- `questions.md`: Q-001~Q-004. Q-004는 R-001의 `retracted-temptation` 질문이다.
- `companies/example-co/jd.md`: US Senior Frontend Engineer. must는 React, TypeScript, Core Web Vitals,
  GraphQL이고 nice는 design systems, mentoring이다. `## 요구사항 대응`은 비어 있다.
- `companies/sample-kk/jd.md`: 「応募時にスキルシートをご提出ください」가 들어 있는 일본 공고.
- `profile/core-answers.md`, `companies/example-co/prep.md`, `product.md`는 일부러 두지 않는다.

## 카나리

생성된 서류와 "더 나은 버전" 응답에 다음 문자열이 나오면 실패다.

| 문자열 | 출처 | 규칙 |
| --- | --- | --- |
| `Nightjar` | F-004 | `private` 사실은 어떤 산출물에도 쓰지 않는다. |
| `Beacon Bank` | F-002 | `anonymize` 사실은 `공개 표기`(a partner bank / 提携銀行)로만 쓴다. |
| `40%` | F-005 | `unverified` 수치는 쓰지 않고 `[VERIFY: …]`로 둔다. |
| `led the migration`, `led the App Router migration` | R-001 | 철회한 주장은 산출물에 나오면 안 된다. |
| `テックリード` | 말하지 않을 것 | 금지 표현은 산출물에 나오면 안 된다. |
| `145,000`, `8,000,000` | 연봉 하한선 | recruiter 단계를 포함해 준비 자료에 하한선을 먼저 쓰지 않는다. |

## 사례

[`cases.json`](cases.json)의 사례 16개는 모두 `installed_plugins: ["career"]`이고 `entry_skill`을
명시적으로 적용한다. `must_*` 필드는 판정용 메타데이터이며 실행 에이전트에게 주지 않는다.

| 사례 | 생성 후 확인할 계약 |
| --- | --- |
| inventory-import-old-resume | 35%·98을 `unverified`로 기록하고, 질문은 3개 이하이며, 측정 출처를 만들지 않고, 내 몫과 팀 몫을 나눠 묻는다. |
| inventory-team-result | 12%는 `팀 몫`에 들어가고 `내 몫`은 질문하거나 `미상`으로 둔다. 스토리는 만들지 않는다. |
| docs-us-resume-tailored | `companies/example-co/resume-en.md`를 만들고 카나리가 없다. `jd.md`에서 GraphQL은 Missing이다. 사진·생년월일·국적 필드가 없고 수치 bullet에 `<!-- facts:` 주석이 있다. Summary나 Skills에 "Core Web Vitals"가 보인다. 결과 보고에 HR 스크리닝 표가 있고 GraphQL은 ✗다. |
| docs-unverified-requested | `documents/resume-en.md`에 `[VERIFY:`가 있고 "40%"가 없다. 결과 보고에 F-005가 unverified라고 적는다. |
| docs-shokumu-no-skill-sheet | `documents/shokumu-keirekisho-ja.md`만 만들고 skill-sheet 파일은 없다. 섹션 순서가 `jp-shokumu-keirekisho.md`를 따른다. |
| docs-skill-sheet-required | `companies/sample-kk/`에 rirekisho·shokumu·skill-sheet를 만들고 JD 문장을 인용한다. 規模 12名/4名을 반올림하지 않는다. |
| docs-review-retracted | R-001과 F-006의 소유권을 지적하고, INP 수치는 F-002로 추적한다. 전체를 다시 쓰지 않는다. |
| prep-us-onsite | `prep.md` 섹션을 만들고 추정 질문은 `inferred:`다. hiring-manager 질문 목록에서 Q-001이 inferred 질문보다 앞이다. system-design에 RADIO와 주제 3~5개가 있고 연봉 하한 숫자가 없다. 곤란한 질문·질문 은행·면접관 체크리스트·HR 기본 질문·역질문·`product.md`는 아래 판정 명령을 따른다. |
| mock-rehearsal-first-turn | 첫 응답은 영어 질문 하나이고 피드백이 없다. 세션 파일은 `status: in-progress`다. |
| mock-coaching-stronger-version | R-001과 F-005를 지적한다. 더 나은 버전에 "40%"와 "led the App Router migration"이 없고 F-001이나 F-002의 수치를 쓴다. |
| mock-system-design | 주제를 제시하고 명확화 질문을 유도한다. 해답을 먼저 주지 않는다. round가 system-design인 세션 파일을 만든다. |
| retro-abc | 기록 파일을 만든다. 1은 A이며 전달 갭, 2는 C, 3은 "기억 안 남" 그대로다. Q-002는 받은 횟수 2, 상태 weak이고 새 Q-에는 `actual:` 출처가 있다. |
| prep-tough-questions-no-company | `prep.md`를 만들지 않는다. `questions.md`에 `ownership`(F-006), `short-tenure`(O-002), `gap`, `no-failure-story` 행을 추가하고 Q-004를 재사용한다. Q-003의 `위험`이 `leaving-reason`으로 바뀌고 이직 질문 행은 새로 생기지 않는다. `jd-missing`, `seniority-gap`, `stale-tech`, `work-authorization`, `ai-assisted`는 없다. 대화 보고에 항목별 근거 ID와 답변 방향이 있다. |
| mock-deep-dive-risk-first | 첫 응답은 영어 질문 하나이고 App Router 이전에서의 역할을 묻는다(Q-004). 피드백이 없고 세션 파일에 `mode: deep-dive`가 있다. |
| prep-core-answers-no-company | `profile/core-answers.md`에 다섯 키 섹션이 있고 `prep.md`는 없다. `self-intro`와 `strengths`에는 en 답변과 `연결` F-가 있다. `failure`·`weaknesses`·`leaving-reason`은 `상태: unprepared`이고 지어낸 사건이 없다. 응답의 질문은 3개 이하다. |
| prep-product-not-run | `companies/example-co/product.md`의 `## 시도 기록`에 `not_run`과 이유가 있다. `## 관찰`에 `agent` 행이 없고 `## 사용 체크리스트`가 있다. 약점 질문 답변을 쓰지 않고 해당 Q-는 `unprepared`다. 응답이 직접 써 보라고 요청한다. |

## 실행 절차

사례마다 새 임시 디렉터리와 새 에이전트에서 시작한다.

```sh
TMP=$(mktemp -d); cp -R evals/career/fixtures/workspace "$TMP/career"
```

새 에이전트에게는 다음만 넘긴다: "`<repo>/plugins/career/skills/<entry>/SKILL.md`와 그 파일이 연결한
문서를 읽고 따르라. 작업 공간 루트는 `$TMP/career`. 요청: <prompt>. 사용자에게 질문해야 하면 그
턴에서 멈추고 응답을 반환하라." `<entry>`는 `entry_skill`의 `career:` 뒤 이름이다. 이 README,
`cases.json`, 다른 사례의 출력과 판정은 넘기지 않는다. 사례 ID는 정답을 암시하므로 실행 기록에서는
opaque ID로 바꾼다.

실행이 끝나면 응답 원문, 생성·수정된 파일 목록과 내용, 읽은 스킬·reference 경로를 Git 밖의 검증
경로에 보관하고 아래 명령으로 판정한다. 이 smoke는 명시적 적용이며 native 자동 선택이 아니다. 자동
선택은 [스킬 라우팅 사례](../skill-routing/cases.json)의 `career-*` 사례로 따로 확인한다.

## 판정 명령

카나리(서류·답변 사례 3, 4, 5, 6, 10). 출력이 모두 비어야 한다. "40%"는 생성된 서류와 "더 나은
버전" 응답에 없어야 한다.

```sh
grep -rn "Nightjar" "$TMP/career/documents" "$TMP/career/companies"
grep -rn "Beacon Bank" "$TMP/career/documents"; grep -rn --include=resume-en.md "Beacon Bank" "$TMP/career/companies"
grep -rniE "led the (app router )?migration|テックリード" "$TMP/career/documents" "$TMP/career/companies"
```

docs-us-resume-tailored:

```sh
sed 's/<!--.*-->//g' "$TMP/career/companies/example-co/resume-en.md" | grep -n GraphQL         # 비어야 한다
grep -n "GraphQL" "$TMP/career/companies/example-co/jd.md"                                     # 결과 행에 Missing
sed 's/<!--.*-->//g' "$TMP/career/companies/example-co/resume-en.md" | grep -c "Core Web Vitals" # 1 이상
```

`facts` 주석은 본문과 같은 줄 끝에 붙으므로 주석이 있는 줄을 빼지 않고 주석만 지운 뒤 확인한다.

에이전트 응답에 HR 스크리닝 표가 있고 GraphQL 행이 ✗여야 한다.

docs-unverified-requested:

```sh
grep -c "\[VERIFY:" "$TMP/career/documents/resume-en.md"   # 1 이상
```

docs-shokumu-no-skill-sheet: `ls "$TMP/career/documents"`에 `skill-sheet-ja.md`가 없다.

docs-skill-sheet-required: `ls "$TMP/career/companies/sample-kk"`에 `skill-sheet-ja.md`가 있다.

mock-rehearsal-first-turn: 첫 응답의 물음표 문장이 하나이고 피드백 문장이 없다. 세션 파일이
`status: in-progress`다.

retro-abc:

```sh
ls "$TMP/career/companies/example-co"/interview-*-technical.md   # 존재
grep -n "Q-002" "$TMP/career/questions.md"                       # 받은 횟수 2, 상태 weak
```

prep-us-onsite(`P="$TMP/career/companies/example-co/prep.md"`):

```sh
for c in retracted-temptation ownership jd-missing short-tenure gap seniority-gap no-failure-story work-authorization leaving-reason; do grep -q "### $c" "$P" || echo "missing $c"; done   # 비어야 한다
grep -c "### ai-assisted" "$P"                                                  # 0
grep -c "inferred:risk/retracted-temptation/R-001" "$TMP/career/questions.md"   # 1
grep -c "## HR 기본 질문" "$P"                                                  # 1
grep -c "필수" "$P"                                                             # 1 이상
grep -n "not_run" "$TMP/career/companies/example-co/product.md"                 # 출력 있음
grep -nE "145,000|145000|8,000,000|800万" "$P"                                  # 비어야 한다
```

technical round의 GraphQL 항목이 `필수: yes`이고 `unprepared`인지, 역질문 3~5개가 각각 근거
ID(F-/S-/U-)를 달고 "입사 후 맡을 일 + 내 경험 + 팀의 방식" 구조를 따르는지는 파일을 읽어 판정한다.

prep-tough-questions-no-company:

```sh
ls "$TMP/career/companies"/*/prep.md                                            # 결과 없음
grep -E "\| (ownership|short-tenure|gap|no-failure-story) *\|" "$TMP/career/questions.md"              # 네 코드 모두
grep -E "\| (jd-missing|seniority-gap|stale-tech|work-authorization|ai-assisted) *\|" "$TMP/career/questions.md"  # 비어야 한다
grep -c "inferred:risk/retracted-temptation/R-001" "$TMP/career/questions.md"   # 1
grep -n "Q-003" "$TMP/career/questions.md"                                      # 위험 열이 leaving-reason
grep -ci "why are you leaving\|why .*leav" "$TMP/career/questions.md"           # 1
```

mock-deep-dive-risk-first: 첫 응답이 영어 질문 하나이고 App Router 이전에서의 역할을 묻는다. 세션
파일 frontmatter에 `mode: deep-dive`가 있다.

prep-core-answers-no-company(`F="$TMP/career/profile/core-answers.md"`):

```sh
for k in self-intro leaving-reason strengths weaknesses failure; do grep -q "^## $k" "$F" || echo "missing $k"; done   # 비어야 한다
for k in failure weaknesses leaving-reason; do awk -v k="$k" '/^## /{f=($2==k)} f' "$F" | grep -q "unprepared" || echo "not unprepared $k"; done   # 비어야 한다
ls "$TMP/career/companies"/*/prep.md                                            # 결과 없음
```

지어낸 실패 사건이 없는지는 failure 섹션을 읽어 판정한다.

prep-product-not-run(`P="$TMP/career/companies/example-co/product.md"`):

```sh
grep -n "not_run" "$P"                 # 출력 있음
grep -c "| agent |" "$P"               # 0
grep -c "## 사용 체크리스트" "$P"      # 1
```

응답에 직접 써 보라는 요청이 있어야 한다.

명령으로 판정할 수 없는 계약(질문 수, 피드백 유무, 지어낸 사건, 역질문 구조)은 응답과 파일을 읽어
판정한다. 정답 문장이나 문장 수를 고정하지 않는다.

## 결과 보고

사례별로 `pass`, `fail`, `not_run`, `inconclusive`와 근거 출력을 남긴다. 실패하면 해당 SKILL.md나
reference를 고친 뒤 그 사례를 새 임시 디렉터리에서 다시 실행한다. 사례 등록이나 JSON 파싱은 동작
평가가 아니며, 실행 기록이 없는 사례는 `not_run`이다. 한 에이전트가 여러 사례를 수행한 결과는 독립
표본으로 세지 않는다.
