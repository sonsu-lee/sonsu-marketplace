# 마켓플레이스 리팩터링 판정

## 기준

각 플러그인·스킬·스크립트·평가 단위를 [스킬과 플러그인 문서 작성 기준](../guides/writing-skills.md)에 비추어 판정하고, 근거는 [`refactor-inventory/`](refactor-inventory)의 인벤토리 JSON에 둡니다. 아래 표는 `python3 scripts/validate_refactor_inventory.py report`로 다시 만들고 `check`가 인벤토리와의 일치를 검사합니다.

## 판정 결과

<!-- inventory-report:start -->
### 플러그인 판정

| 플러그인 | 판정 | 대상 | omp 현재 | omp 제안 | 스킬 수 | 문서 지적 수 | 근거 |
|---|---|---|---|---|---|---|---|
| engineering | keep |  | not-distributed | not-distributed | 17 | 1 | 호스트별 실행 계약과 내용 주소 기반 품질 근거는 고유하다. PR 리뷰 진입점은 review 하나로 합쳤고 계획 구조 검사와 PR snapshot 수집은 validate_plan.py·pr_review_snapshot.py로 도구화해 판단과 수집을 분리했다. |
| workflow | keep |  | default | default | 9 | 0 | 독립적인 전달 업무와 안전 계약은 유지한다. to-pr의 Git·GitHub 상태 수집은 pr_context.py, 첨부 manifest 검사는 validate_attachment_manifest.py, inspect-prs의 페이지 수집·상태 정규화는 inspect_prs.py로 분리해 모든 도구 제안을 처리했다. |
| fluent-korean | keep |  | default | default | 2 | 2 | Codex 단일 호출과 Claude 다단계 스킬을 유지합니다. 공통 보존 규칙은 quick-rules.header.md 하나로 모으고 Claude 실행 절차는 file-workflow.md로 옮겼으며, 런타임과 무관한 홍보·commit-ko·과거 평가 스크립트는 번들에서 제거했습니다. |
| fluent-english | keep |  | default | default | 1 | 0 | 독립적인 영어 작성·윤문 지침을 유지하고, 수치 기반 voice calibration과 보호 문자열 대조는 읽기 전용 도구로 분리했습니다. 도구 출력은 문맥 판단의 입력으로만 사용합니다. |
| fluent-japanese | keep |  | default | default | 1 | 0 | 독립 도메인과 기존 검사 도구를 유지합니다. 진단 점수 산식은 score.py로 계산하고, 코퍼스가 없는 연구 도구 calibrate.py는 패키지에서 제거했습니다. |
| writing | keep |  | opt-in | opt-in | 2 | 1 | 두 스킬은 업무 문서 편집과 기술 아티클 작성이라는 독립 과업을 갖습니다. Fluent와 경계가 명시되어 있어 플러그인 전체를 통합할 이유는 부족합니다. |
| research | keep |  | opt-in | opt-in | 1 | 0 | 원문이 주장을 지지하는지와 상충 자료의 의미를 판단하는 독립 과업은 유지합니다. 증거 원장의 필드·식별자·연결·locator 누락은 validate_evidence_ledger.py로 분리했고, 이미 구현된 코드 검색 cache는 그대로 재사용합니다. |
| prompting | keep |  | opt-in | opt-in | 1 | 0 | 프롬프트 자체를 요청한 사용자에게 복사 가능한 결과를 제공하는 독립 과업입니다. 실행 에이전트 정책과 일반 문체 규칙의 중복은 줄이되, 제품별 입력·API 설정 구분과 의미 보존 계약은 유지합니다. |
| product | keep |  | opt-in | opt-in | 7 | 0 | 일곱 과업은 탐색·발산·근거 종합·도메인·실험 설계·판정·문서 작성이라는 별도 결과를 냅니다. PRD 구조 검사는 validate_prd.py로 분리했습니다. |
| memory-manager | keep |  | not-distributed | not-distributed | 4 | 0 | omp 기본 기억과 겹친다는 이유로 다른 호스트가 공유하는 로컬 저장소까지 제거할 수는 없다. Markdown 정본·출처·범위·SHA 기반 변경 계약은 기존 도구와 함께 유지하고 omp에서는 미배포한다. 공통 명령·결과·복구·경계는 references/store-contract.md 하나에 두고 네 스킬이 링크한다. |
| design-patterns | keep |  | opt-in | opt-in | 2 | 0 | 독립적인 선택·검토 과업과 카탈로그 기반 판단 계약이 있다. 기계적 스키마·snapshot·관계 검사는 이미 validate_catalog.py가 맡으므로 새 조정 계층을 만들 필요가 없다. |
| design | keep |  | default | default | 4 | 0 | 네 진입점의 쓰기 권한과 결과가 다르고 공통 계약·검증기는 이미 reference와 shared 원본으로 분리되어 있습니다. 스킬·README는 작성 기준 구조로 정리했고 생성물에 있던 지적은 shared 정본에서 처리했습니다. |
| worklog | keep |  | opt-in | opt-in | 2 | 0 | 로그 수집·집계는 worklog.py가, worklog-improve의 기록 고정·횟수·회귀·채택 조건 계산은 validate_improvement.py가 맡는다. 스킬에는 원인 판단·사례 작성·블라인드 비교 같은 판단 절차만 남았다. |

### 유지 외 판정

| 경로 | 판정 | 대상 | 근거 |
|---|---|---|---|
| plugins/engineering/skills/debug/condition-based-waiting-example.ts | to-reference | plugins/engineering/skills/debug/condition-based-waiting.md | `~/threads` 경로의 Lace 타입을 import하므로 이 패키지에서 실행하거나 타입 검사할 수 없다. 실행 도구가 아니라 조건 기반 대기의 구현 형태를 보여 주는 자료이므로 필요한 부분만 reference 예시로 옮긴다. |

### 도구 후보

| 스킬 | 위치 | 단계 | 제안 | 기존 도구 |
|---|---|---|---|---|

### 문서 지적 집계

| 플러그인 | negative-definition | history | duplicate-rule | missing-example | structure | internal-detail |
|---|---|---|---|---|---|---|
| engineering | 0 | 0 | 1 | 0 | 0 | 0 |
| workflow | 0 | 0 | 0 | 0 | 0 | 0 |
| fluent-korean | 0 | 2 | 0 | 0 | 0 | 0 |
| fluent-english | 0 | 0 | 0 | 0 | 0 | 0 |
| fluent-japanese | 0 | 0 | 0 | 0 | 0 | 0 |
| writing | 0 | 0 | 1 | 0 | 0 | 0 |
| research | 0 | 0 | 0 | 0 | 0 | 0 |
| prompting | 0 | 0 | 0 | 0 | 0 | 0 |
| product | 0 | 0 | 0 | 0 | 0 | 0 |
| memory-manager | 0 | 0 | 0 | 0 | 0 | 0 |
| design-patterns | 0 | 0 | 0 | 0 | 0 | 0 |
| design | 0 | 0 | 0 | 0 | 0 | 0 |
| worklog | 0 | 0 | 0 | 0 | 0 | 0 |
<!-- inventory-report:end -->

## 다음 단계

1. `plugins/engineering/skills/finish-branch`: `duplicate-rule` 1건. 티켓 연결·자동 종료 규칙을 `shared/agent-policy` 정본으로 옮겨 Workflow와 공유한다.
2. Fluent Korean `ai-tell-taxonomy.md`·`quick-rules.footer.md`: `history` 2건. 판정 근거와 얽힌 버전 경위를 정리하고 omp 투영 테스트가 고정한 행을 함께 조정한다.
3. Writing `references/continuity.md`: `duplicate-rule` 1건. 생성물이므로 `shared/task-continuity/continuity.md.tmpl`에서 호스트 세션 규칙의 배치를 정한다.
4. `plugins/engineering/skills/debug/condition-based-waiting-example.ts`: `to-reference`. 이 패키지에서 실행·타입 검사할 수 없는 예시 코드이므로 필요한 부분만 `condition-based-waiting.md`의 예시로 옮긴다.

## 참고 구현

- [sonsu-lee/oxc-config](https://github.com/sonsu-lee/oxc-config): 규칙을 설정과 계약 테스트로 고정하고 결정 근거는 [`docs/rule-ledger.md`](https://github.com/sonsu-lee/oxc-config/blob/main/docs/rule-ledger.md)에 둔다.
- [antfu/skills](https://github.com/antfu/skills): 짧은 SKILL.md와 references로 구성하고 `GENERATION.md`에 원본 SHA를 둔다.
- [wrtnlabs/evidence](https://github.com/wrtnlabs/evidence): 요구사항 연결의 누락은 검사하고 근거의 진위는 리뷰한다.
