# Career

개발자 이직을 위해 확인 상태와 출처가 있는 경력 원본을 정리하고, 그 원본의 사실만으로 미국식
영문 resume, 履歴書, 職務経歴書를 작성하며, 회사·라운드별 면접 준비, 모의면접과 실제 면접 회고를
질문 은행으로 이어 주는 개인용 Codex·Claude Code·omp 플러그인입니다.

## 포함된 스킬

- `career-inventory`: 경력 사실, 성과 수치, STAR+R 스토리와 조건 답변을 확인 상태·출처와 함께
  원본으로 정리하고 정정·철회합니다.
- `write-career-documents`: 확인된 사실만으로 미국식 resume, 履歴書, 職務経歴書를 작성·JD
  맞춤·검토하고, 지원처가 요구할 때만 スキルシート를 만듭니다.
- `prepare-interview`: 공고 요구사항 대응, 면접관 체크리스트, HR 기본 질문 답변, 제출 서류
  심층 질문, 자료에서 찾은 곤란한 질문, 프로덕트 분석, 역질문과 직전 요약을 준비합니다.
- `mock-interview`: 한 번에 한 질문씩 묻고 꼬리질문을 이어 가며 coaching, rehearsal,
  deep-dive, 프론트엔드 system-design 모의면접을 진행하고 기록합니다.
- `interview-retro`: 실제 면접의 질문과 답변을 기록하고 A/B/C로 분류해 질문 은행, 스토리와
  경력 원본에 반영할 조치를 정리합니다.

## 작업 공간

다섯 스킬은 사용자 작업 공간 하나를 함께 씁니다. 기본 경로는 `./career`이며 저장소에는 개인
데이터를 두지 않습니다. 필드, ID, 어휘와 쓰기 규칙은 [작업 공간 계약](references/workspace.md)과
[근거 규칙](references/evidence-rules.md)을 따릅니다.

```text
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

## 조합과 경계

이 스킬들은 고정된 pipeline이 아닙니다. 요청의 직접 목적에 따라 어느 스킬에서든 시작하며, 다른
플러그인의 설치나 선행 실행을 전제로 하지 않습니다.

- 다른 플러그인에 의존하지 않습니다. manifest에 plugin dependency를 선언하지 않습니다.
- 완성된 문장의 윤문은 Fluent English·Japanese, 여러 출처를 교차 확인하는 회사 조사는 Research와
  runtime에서 조합합니다.
- スキルシート는 사용자가 요청했거나, 응모 안내가 요구하거나, SES·フリーランス 案件일 때만
  만듭니다.
- 알고리즘 문제 풀이·채점, 지원서 제출·메일 발송·외부 양식 입력은 하지 않습니다.
- 개인 데이터는 사용자 작업 공간에만 둡니다.

## 설치

마켓플레이스를 등록한 뒤 사용하는 호스트에서 다음 명령으로 설치합니다.

```sh
codex plugin add career@sonsu-marketplace
claude plugin install career@sonsu-marketplace
omp plugin install career@sonsu-marketplace
```

설계 참고 출처는 [UPSTREAM.md](UPSTREAM.md)에 기록합니다.
