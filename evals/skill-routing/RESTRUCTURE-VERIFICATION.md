# 독립 스킬 재구성 검증 기록

- 날짜: 2026-09-25
- 대상: 이 저장소의 12개 로컬 플러그인, 변경 중인 작업 트리
- 기준 HEAD: `0e2c940`

## 형식과 소비 검사

| 검사 | 관찰 |
| --- | --- |
| 공개 `SKILL.md`의 frontmatter `name`과 디렉터리 이름 | 53개 모두 일치 |
| 활성 Markdown 상대 문서 링크 | 깨진 링크 0개 |
| `render-agent-policy.py --check`, `render-continuity.py --check`, `render-design-quality.py --check` | 모두 통과 |
| `evals/plugin-compat` | 6개 통과 |
| `plugins/engineering/tests` | 89개 통과, 2개 skip |
| `evals/task-continuity` | 21개 통과. 이전 공개 디렉터리 이름으로 저장된 활성 기록도 읽고 현재 이름으로 갱신 가능. native probe는 설치 사본의 reference를 확인 |
| Engineering 패키징·identity shell 검사 | 5개 스크립트 통과 |
| `evals/design-quality`, `plugins/operations-ui/tests`, `plugins/design-patterns/tests` | 각각 160개 통과(30개 skip), 11개 통과, 38개 통과 |
| `evals/marketplace-v2` | 43개 통과. 앱 번들에는 `cua_node/bin/npm`이 없어 기본 실행은 실패했고, 동일 Codex 바이너리와 로컬 Node/npm을 격리된 임시 경로에 배치해 실행 |

## Native 발견과 선택

Codex CLI `0.155.1`의 격리된 `CODEX_HOME`에서 9개 연속성 플러그인을 각각 설치하고 함께
설치한 `plugin/read`, `skills/list`, `hooks/list`가 모두 오류 없이 완료됐다. 설치된 캐시의
`references/continuity.md` 존재도 hook의 `sourcePath`를 통해 확인했다. 나머지 3개도 각각
설치해 확인했다. 마지막으로 12개를 함께 설치했을 때 **플러그인 공개 스킬 53개**가 발견됐다.
호스트가 추가한 ambient 스킬 11개는 이 수에 포함하지 않았다. 옛 공개 호출명과 공개
`task-continuity`는 발견 목록에 없었다. 이 검사는 hook 실행이나 모델의 스킬 사용을 증명하지 않는다.

격리된 읽기 전용 Codex 모델 실행에서는 다음을 관찰했다.

| 요청 | 실제 관찰 |
| --- | --- |
| Git commit 후보의 범위·원자성·메시지 검토 | `workflow:review-commit` 자동 선택, 해당 `SKILL.md` 읽기, Git 상태와 diff 조회 후 읽기 전용 결과 작성 |
| 작은 API 구현 계획 | 첫 실행에서 `engineering:plan` 자동 선택·읽기 후 계획 작성. 새 설치에서 같은 요청을 다시 실행했을 때는 스킬 파일을 읽지 않고 계획 작성 |

따라서 설치·발견은 관찰됐고 자동 선택은 대표 요청에서 **부분적으로 관찰**됐다. 스킬 선택의
일관성이나 결과 품질 개선은 이 소수 실행으로 입증되지 않는다.

## 발동 조건과 미실행 범위

`engineering:review`, 집중 관점 리뷰, 품질 게이트 문구와 `evals/engineering-quality-gates/cases.json`,
`evals/skill-routing/cases.json`에서 일반 전체 5명, 집중·국소 재검토 1명, 기계적 변경 0명의
조건을 확인했다. `shared/design-quality/design-quality.md`와 디자인 스킬에서는 평가 가능한
신규·재설계 산출물에만 2인 DQ 평가를 요구하고 탐색·문구·디자인 없는 코드 작업을 제외한다.

평가 fixture를 대상으로 한 5인/1인 리뷰 발동 실험, 2인 디자인 평가 실행, 고위험 red team과
리뷰 발견력 비교는 실행하지 않았다. 위의 형식 검사와 loader 관찰을 해당 결과 품질의 증거로
사용하지 않는다.

이 재구성 구현 자체에는 같은 frozen working-tree 패키지(SHA-256
`be9835ab6fc415eb7289d60530547442f595245784c83046e5f12971959adbbe`)를 받은 Luna xhigh
독립 검토자 5명이 완료한 전체 변경 리뷰를 적용했다. ADR 0014의 현재 링크, Figma Workflow
출처 문서의 버전, native probe의 설치 사본 검사 누락을 유효한 지적으로 판정해 수정했다.
`*-task-continuity` frontmatter 이름이 옛 checkpoint에 저장된다는 지적은 기존 helper가
`skills/<디렉터리명>/SKILL.md`를 검증하고 `active_skill`을 기록하므로 도달할 수 없는 입력으로
판정했다.
세 지적의 수정 패키지(SHA-256
`48e5aae3ffafbc6cfdedbdf55e0c659aca141b6fa9e3a567395b45df67190056`)는 별도 새 문맥
Luna xhigh 1명이 집중 재검토했고 추가로 도달 가능한 결함을 보고하지 않았다. 이후 역사 문서
세 곳의 현재 ADR 링크만 기계적으로 갱신해 상대 링크 검사로 확인했다.
