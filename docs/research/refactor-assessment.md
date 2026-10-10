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
| fluent-korean | keep |  | default | default | 2 | 14 | Codex 단일 호출과 Claude 다단계 스킬을 유지하고 공통 규칙을 정리하는 방향이 맞습니다. 기계 단계는 기존 스크립트를 재사용하며 미포함 commit-ko·평가 의존성 및 상위 프로젝트 홍보 도구를 번들에서 줄일 수 있습니다. |
| fluent-english | new-tool |  | default | default | 1 | 5 | 독립적인 영어 작성·윤문 지침을 유지하면서 수치 기반 voice calibration과 보호 문자열 대조를 코드에 맡깁니다. |
| fluent-japanese | new-tool |  | default | default | 1 | 6 | 독립 도메인과 기존 검사 도구를 유지하고 점수 산식 계산을 도구화하며, 배포에 없는 코퍼스 전용 연구 도구는 정리합니다. |
| writing | keep |  | opt-in | opt-in | 2 | 7 | 두 스킬은 업무 문서 편집과 기술 아티클 작성이라는 독립 과업을 갖습니다. Fluent와 경계가 명시되어 있어 플러그인 전체를 통합할 이유는 부족합니다. |
| research | new-tool |  | opt-in | opt-in | 1 | 8 | 원문이 주장을 지지하는지와 상충 자료의 의미를 판단하는 독립 과업은 유지합니다. 증거 원장의 필드·식별자·상태 누락은 검사기로 분리하고, 이미 구현된 코드 검색 cache를 중복 구현하지 않습니다. |
| prompting | keep |  | opt-in | opt-in | 1 | 10 | 프롬프트 자체를 요청한 사용자에게 복사 가능한 결과를 제공하는 독립 과업입니다. 실행 에이전트 정책과 일반 문체 규칙의 중복은 줄이되, 제품별 입력·API 설정 구분과 의미 보존 계약은 유지합니다. |
| product | new-tool |  | opt-in | opt-in | 7 | 22 | 일곱 과업은 탐색·발산·근거 종합·도메인·실험·문서 작성이라는 별도 결과를 냅니다. PRD의 ID·링크·metadata 검사는 판단 절차에서 분리할 수 있습니다. |
| memory-manager | keep |  | not-distributed | not-distributed | 4 | 10 | omp 기본 기억과 겹친다는 이유로 다른 호스트가 공유하는 로컬 저장소까지 제거할 수는 없다. Markdown 정본·출처·범위·SHA 기반 변경 계약은 기존 도구와 함께 유지하고 omp에서는 미배포한다. |
| design-patterns | keep |  | opt-in | opt-in | 2 | 1 | 독립적인 선택·검토 과업과 카탈로그 기반 판단 계약이 있다. 기계적 스키마·snapshot·관계 검사는 이미 validate_catalog.py가 맡으므로 새 조정 계층을 만들 필요가 없다. |
| design | keep |  | default | default | 4 | 15 | 네 진입점의 쓰기 권한과 결과가 다르고 공통 계약·검증기는 이미 reference와 shared 원본으로 분리되어 있습니다. 문서 구성과 반복 규칙을 줄이는 정리가 우선입니다. |
| worklog | new-tool |  | opt-in | opt-in | 2 | 7 | 로그 수집·집계는 기존 도구를 유지하고, worklog-improve의 평가 입력 고정·횟수·회귀·통과 조건을 검사하는 도구를 추가해 문서에 남은 결정론적 부담을 줄인다. |

### 유지 외 판정

| 경로 | 판정 | 대상 | 근거 |
|---|---|---|---|
| plugins/engineering/skills/debug/condition-based-waiting-example.ts | to-reference | plugins/engineering/skills/debug/condition-based-waiting.md | `~/threads` 경로의 Lace 타입을 import하므로 이 패키지에서 실행하거나 타입 검사할 수 없다. 실행 도구가 아니라 조건 기반 대기의 구현 형태를 보여 주는 자료이므로 필요한 부분만 reference 예시로 옮긴다. |
| plugins/fluent-korean/scripts/build_social_preview_v2.py | delete |  | v2.3 생성기와 동일한 출력 파일을 쓰는 이전 홍보 자산 도구이며 이 패키지에는 assets나 홍보 이미지 생성 과업이 없습니다. |
| plugins/fluent-korean/scripts/build_social_preview_v2_3.py | delete |  | 상위 프로젝트 imnotai.kr 홍보물 제작 도구로 한국어 생성·윤문 실행에 쓰이지 않습니다. 현재 패키지의 산출물 계약과 무관합니다. |
| plugins/fluent-korean/scripts/check_commit_lexicon_ids.py | delete |  | 고정 입력 extras/skills/commit-ko/references/commit-lexicon.md가 현재 플러그인에 포함되지 않습니다. 함께 배포되지 않는 opt-in 스킬의 검사기를 런타임 번들에 유지할 이유가 없습니다. |
| plugins/fluent-korean/scripts/commit_msg_lint.py | delete |  | 현재 배포하지 않는 commit-ko와 Git hook용 진입점이며 일반 한국어 윤문 스킬이 호출하지 않습니다. 커밋 작업은 Workflow의 명시적 계약에 남기는 편이 맞습니다. |
| plugins/fluent-korean/scripts/eval_baseline.py | delete |  | 현재 패키지에 없는 tests/humanize_asserts·humanize_runner 및 fixtures.json에 의존하는 상위 프로젝트 실험입니다. 배포 스킬 평가와 분리된 과거 워터마크 실험 진입점을 제거할 수 있습니다. |
| plugins/fluent-korean/scripts/make_thumbnail.py | delete |  | 동일 출력의 후속 이미지 생성기들과 중복되는 상위 프로젝트 홍보용 코드입니다. 현재 플러그인에는 해당 자산 제작 과업이 없습니다. |
| plugins/fluent-english/skills/fluent-english/SKILL.md | new-tool |  | 영어 작성·교정은 유지하고 수작업으로 지시한 빈도·전후 수치 비교와 보호 문자열 대조만 결정론적 도구로 분리할 가치가 있습니다. 도구 출력은 수정 명령이 아니라 문맥 판단의 입력으로 사용합니다. |
| plugins/fluent-japanese/skills/fluent-japanese/SKILL.md | new-tool |  | 기존 lint·outline·terms의 기계/판단 분리는 적절합니다. diagnose.md의 명시적인 점수 산식은 lint JSON을 입력으로 계산하는 도구로 옮기고 구조·가독성 평가는 모델 판단으로 남길 수 있습니다. |
| plugins/fluent-japanese/skills/fluent-japanese/scripts/calibrate.py | delete |  | 고정된 plugins/fluent-japanese/corpus를 전제로 하지만 현재 패키지에는 corpus가 없고 문서 작성 경로에서도 호출하지 않습니다. [추론] 상위 프로젝트 연구 도구로 남기고 배포 패키지에서는 제외할 수 있습니다. |
| plugins/research/skills/research/SKILL.md | new-tool |  | 조사와 보고서 감사는 직접 요청되는 독립 과업이며 일반 검색·위임과 다른 증거 계약이 있습니다. 기계적으로 확인 가능한 원장 형식과 누락을 validator로 분리하되, 조사 품질과 원문의 진위는 모델 판단으로 남깁니다. |
| plugins/product/skills/to-prd/SKILL.md | new-tool |  | 형식·ID·링크 검사는 명시된 결정론적 완료 조건인데 별도 스크립트가 없습니다. 의미와 승인 진위는 모델이 판단하고 문서 구조 검사만 도구로 분리할 수 있습니다. |
| plugins/worklog/skills/worklog-improve/SKILL.md | new-tool |  | 스킬 개선은 로그 진단과 구별되는 사용자 과업이다. 현재 worklog.py는 clusters까지만 제공하므로 평가 횟수·고정 입력·숫자 통과 조건은 별도 검사기로 분리할 가치가 있다. |

### 도구 후보

| 스킬 | 위치 | 단계 | 제안 | 기존 도구 |
|---|---|---|---|---|
| plugins/fluent-english/skills/fluent-english/SKILL.md | plugins/fluent-english/skills/fluent-english/references/voice-and-context.md:100-120 | 원문·샘플·윤문본의 문장 길이, 축약형·인칭·유보 표현과 문장부호 빈도를 같은 규칙으로 집계하고 전후 차이를 반환합니다. | script | - |
| plugins/fluent-english/skills/fluent-english/SKILL.md | plugins/fluent-english/skills/fluent-english/SKILL.md:57 | 코드·인용·링크 대상·frontmatter의 전후 문자열 차이를 찾아 사람이 판단할 위치를 반환합니다. | validator | - |
| plugins/fluent-japanese/skills/fluent-japanese/SKILL.md | plugins/fluent-japanese/skills/fluent-japanese/references/diagnose.md:13-37 | lint severity별 건수와 문서 길이로 기계 기본 점수·구간·100자 미만 판정 및 조정 후 범위 제한을 계산합니다. | script | plugins/fluent-japanese/skills/fluent-japanese/scripts/lint.py |
| plugins/research/skills/research/SKILL.md | plugins/research/skills/research/references/evidence-policy.md:18-39 | 증거 원장의 필수 필드, enum, claim_id별 연결과 locator 누락을 검사합니다. 원문이 주장을 실제로 지지하는지와 출처의 권위는 검사 통과와 별도로 판단합니다. | validator | - |
| plugins/product/skills/to-prd/SKILL.md | plugins/product/skills/to-prd/SKILL.md:116-117 | PRD metadata·ID 중복·내부 참조·상대 링크·자리표시자·허용 경로를 읽기 전용으로 검사합니다. | validator | - |
| plugins/worklog/skills/worklog-improve/SKILL.md | plugins/worklog/skills/worklog-improve/SKILL.md:67-90 | 평가 입력·기준선 리비전·모델 설정의 고정값과 실행 횟수, 후보 독립성·순증가 줄 수, 회귀 case ID를 기록한 결과를 검사한다. | validator | - |
| plugins/worklog/skills/worklog-improve/SKILL.md | plugins/worklog/skills/worklog-improve/SKILL.md:98-118 | 기준선·후보별 n/3과 고정 회귀 결과에서 후보가 2/3 이상이고 기준선보다 높으며 기존 pass가 보존됐는지 계산한다. not_run·inconclusive와 회귀 대상 0개를 통과 근거와 분리한다. | validator | - |

### 문서 지적 집계

| 플러그인 | negative-definition | history | duplicate-rule | missing-example | structure | internal-detail |
|---|---|---|---|---|---|---|
| engineering | 0 | 0 | 1 | 0 | 0 | 0 |
| workflow | 0 | 0 | 0 | 0 | 0 | 0 |
| fluent-korean | 3 | 2 | 3 | 2 | 2 | 2 |
| fluent-english | 1 | 1 | 1 | 1 | 1 | 0 |
| fluent-japanese | 0 | 1 | 1 | 1 | 2 | 1 |
| writing | 0 | 1 | 1 | 2 | 2 | 1 |
| research | 1 | 2 | 1 | 1 | 3 | 0 |
| prompting | 1 | 4 | 1 | 1 | 3 | 0 |
| product | 6 | 1 | 2 | 7 | 6 | 0 |
| memory-manager | 1 | 1 | 0 | 4 | 4 | 0 |
| design-patterns | 1 | 0 | 0 | 0 | 0 | 0 |
| design | 1 | 1 | 4 | 4 | 4 | 1 |
| worklog | 1 | 0 | 1 | 2 | 2 | 1 |
<!-- inventory-report:end -->

## 다음 단계

1. Writing·Research·Prompting·Product: omp `not-distributed` → `opt-in` 배포
2. `plugins/engineering/skills/review-pr`: `merge` → `engineering:review`의 심층·다중 옵션
3. `plugins/engineering/scripts/sdd-review-package`: `merge` → `review-package`
4. Fluent Korean 스크립트 6개(`build_social_preview_v2*.py`, `check_commit_lexicon_ids.py`, `commit_msg_lint.py`, `eval_baseline.py`, `make_thumbnail.py`): `delete`
5. `plugins/fluent-japanese/skills/fluent-japanese/scripts/calibrate.py`: `delete`
6. `plugins/engineering/skills/debug/condition-based-waiting-example.ts`: `to-reference` → `condition-based-waiting.md`의 예시
7. Engineering 도구 후보 2건: `plan` 참조 validator, `review` PR snapshot script
8. Workflow 도구 후보 2건: `to-pr` 첨부 manifest validator, `inspect-prs` 수집 script
9. Fluent English 도구 후보 2건, Worklog `worklog-improve` validator 2건
10. Fluent Japanese 점수 산식 script, Research 증거 원장 validator, Product PRD validator: 각 1건
11. Engineering 문서 재작성: `doc_findings` 41건
12. Workflow 문서 재작성: `doc_findings` 24건
13. Product 22건, Design 15건, Fluent Korean 14건 문서 재작성
14. Prompting·Memory Manager 각 10건, Research 8건, Writing·Worklog 각 7건, Fluent Japanese 6건, Fluent English 5건 문서 재작성
15. Design Patterns 문서 재작성: `doc_findings` 1건(`language-realization.md`)

## 참고 구현

- [sonsu-lee/oxc-config](https://github.com/sonsu-lee/oxc-config): 규칙을 설정과 계약 테스트로 고정하고 결정 근거는 [`docs/rule-ledger.md`](https://github.com/sonsu-lee/oxc-config/blob/main/docs/rule-ledger.md)에 둔다.
- [antfu/skills](https://github.com/antfu/skills): 짧은 SKILL.md와 references로 구성하고 `GENERATION.md`에 원본 SHA를 둔다.
- [wrtnlabs/evidence](https://github.com/wrtnlabs/evidence): 요구사항 연결의 누락은 검사하고 근거의 진위는 리뷰한다.
