# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-10-09

## 흐름

```text
후보 선정
  → 업스트림과 라이선스 확인
  → 원본 기준 commit 가져오기
  → 원본 동일성 검증
  → 별도 기준 commit
  → Codex 정본 manifest와 marketplace 등록
  → package 검증과 실제 로딩 검증
  → 로컬 정책 변경
  → 로컬 변경 commit
  → 이후 업스트림 업데이트
```

## 업스트림 기준선

외부 플러그인은 원본 파일과 실행 권한을 먼저 보존하고, 업스트림 출처와 기준 commit을
`UPSTREAM.md`에 기록합니다. 여러 upstream의 일부 파일을 합성할 때는 source path, 임시 baseline
path, 최종 path와 hash를 함께 기록합니다. 원본 가져오기와 로컬 커스텀을 서로 다른 commit으로
남겨 이후 업데이트에서 두 변경의 출처를 구분할 수 있게 합니다.

## 로컬 커스텀

로컬 정책은 원본 기준선 이후에 적용합니다. 하나의 upstream plugin을 fork한 매니페스트 버전은
업스트림 버전 뒤에 `-sonsu.<revision>`을 붙여 원본 릴리스와 구분합니다. 여러 source를 합성하거나
로컬에서 새로 설계한 plugin은 독립 semantic version을 사용합니다. 여러 source를 합성했다면
`UPSTREAM.md`에서 각 source와 변환을 추적하고, 가져온 source가 없는 독립 plugin은 upstream
기준선을 만들지 않습니다. 정책 변경은 관련 결정 기록과 현재 아키텍처 문서를 함께 갱신합니다.

Engineering은 [독립 플러그인 결정](../decisions/0009-maintain-engineering-as-an-independent-plugin.md)에
따라 독립 semantic version을 사용하며 upstream 동기화나 이전 호환 경로를 배포 계약으로 두지
않습니다.

## Codex 배포

`.agents/plugins/marketplace.json`과 각 `.codex-plugin/plugin.json`이 Codex 패키지의 정본입니다.
기존 연구·라이선스·upstream 기록은 유지합니다. `shared/agent-policy`와 `shared/task-continuity`에서
각 플러그인에 필요한 자료를 생성해 다른 패키지 설치 없이 실행되게 합니다.

## Claude Code 배포

Codex catalog와 manifest를 정본으로 두고 `python3 scripts/render-claude-compat.py`로
`.claude-plugin/marketplace.json` 및 각 패키지 manifest를 생성합니다. 대부분의 스킬·hook·script는
같은 패키지 파일을 사용합니다. `memory-manager`는 네 스킬과 저장 스크립트·훅을, `worklog`는 진단
스킬과 기록 스크립트, Claude 전용 hook 정의(`hooks/claude-hooks.json`)를 별도 Claude 패키지에
생성합니다. memory-manager의 정리·승격 스킬만 Claude의 수동 호출 제한을 적용합니다. 모델 프로필은 호스트별로 분리하며, Codex connector와
Claude Code MCP 구성은 별도의 실행 환경 상태입니다.

## omp는 기본 6개와 opt-in Worklog를 배포한다

`python3 scripts/render-omp-compat.py`는 Codex catalog의 순서를 유지하며 기본 6개인 `workflow`,
`fluent-korean`, `fluent-english`, `fluent-japanese`, `design`, `career`와 opt-in `worklog`를
`.omp-plugin/marketplace.json`에 생성합니다. Codex·Claude Code 배포 대상과 원본 패키지는 바꾸지 않습니다.
Worklog는 기본 구성에 포함하지 않고 필요한 사용자만 별도로 설치합니다.

| 플러그인 | omp catalog의 source |
| --- | --- |
| Workflow | `./plugins/workflow/omp` |
| Fluent Korean | `./plugins/fluent-korean/omp` |
| Fluent English | `./plugins/fluent-english` |
| Fluent Japanese | `./plugins/fluent-japanese` |
| Design | `./plugins/design/omp` |
| Career | `./plugins/career` |
| Worklog(opt-in) | `./plugins/worklog/omp` |

Design·Workflow의 omp 전용 패키지는 필요한 skills·references·assets·scripts·figma-plugin·라이선스를
원본 패키지에서 생성해 다른 플러그인 없이 쓸 수 있게 합니다. 스크립트의 실행 권한은 복사할 때 유지합니다.
독자 hook, evidence gate, `task-continuity.py`, omp runtime extension은 포함하지 않습니다. 원본 패키지의
hook·연속성 스크립트는 Codex·Claude Code용으로 남깁니다. Fluent Korean은 Codex 단일 호출 경로의
스킬·참고 자료·라이선스를 전용 패키지로 생성합니다. 품질 불변식을 유지하고 현재 호스트 모델을 사용하며,
Claude Code의 다중 호출·strict 모드와 고정 Opus 에이전트를 요구하지 않습니다. English·Japanese 스킬,
Design의 품질 계약·프로필, Workflow의 작업 권한 경계는 유지합니다.
Design의 native tool 전제도 유지합니다. Japanese는 omp의 기존 model·effort·병렬 실행 정책을 쓰며
full 모드의 세 검토 관점도 같은 호출 안에서 확인합니다.

Worklog는 [ADR 0022](../decisions/0022-add-worklog-plugin.md)에 따른 opt-in 예외입니다. 전용 패키지에는
진단·개선 스킬과 기록 스크립트, runtime extension `extension/worklog.ts`와 이를 선언하는 `package.json`을
생성합니다. runtime extension은 opt-in 패키지에만 배포하며 hook은 포함하지 않습니다.
기본 6개 패키지에는 hook·runtime extension을 포함하지 않는 정책을 유지합니다.
Worklog extension은 도구 결과와 세션 이벤트를 로컬 JSONL로 기록하며 진단 스킬은 읽기 전용입니다.

생성된 `references/continuity.md`는 omp 순정 todo·session으로 작업을 이어 가도록 안내합니다.
`.sonsu`에 연속성 기록을 남기거나 복원 hook·세션 ID 전달을 따로 추가하지 않습니다.
스킬은 `/skill:commit`처럼 플러그인 접두어 없이 호출합니다. model·effort·memory·isolation·동시성은
기존 omp 설정을 쓰며 커스텀 역할용 `task.agentModelOverrides`를 추가하지 않습니다.

| 책임 | 담당 | 배포 |
| --- | --- | --- |
| 개발 실행·task·todo·session·review·메모리 | omp 순정 기능 | 호스트 기능 |
| Git·티켓·PR 작업 권한과 산출물 | Workflow | 기본 6개 |
| 언어별 문장 품질·보호 규칙 | Fluent Korean·English·Japanese | 기본 6개 |
| UI·prototype·handoff 품질과 native tool 전제 | Design | 기본 6개 |
| 경력 원본·지원 서류·면접 준비 | Career | 기본 6개 |
| 원시 작업 이벤트 기록과 진단 | Worklog | opt-in |
| 외부 조사·제품 탐색·글 구성 | Research·Product·Writing | 기본 catalog에 추가하지 않는 선택 후보 |

Research·Product·Writing을 추가하려면 필요한 도메인과 현재 native tool 계약을 별도로 확인합니다.
Engineering의 omp 모델 프로필은 직접 설치한 기존 사용자를 위해 보존하며 기본 구성에는 적용하지 않습니다.

생성물은 직접 편집하지 않습니다. 생성기는 `--check`로 내용·실행 권한의 최신 여부와 불필요한 이전 생성물을
확인하고, 일반 실행에서는 자신이 생성했다고 확인할 수 있는 이전 extension의 `package.json`·`extension.ts`만
정리합니다. 사용자의 파일, 기존 `.sonsu`·`.engineering` 기록과 설치 캐시는 삭제하거나 편집하지 않습니다.

### 공개와 사용자 업데이트를 구분한다

생성·검증·커밋, GitHub 공개, 사용 환경 반영은 서로 다른 작업입니다. 로컬 변경만으로 기존 GitHub 등록이나
설치된 패키지가 갱신됐다고 보지 않습니다.

기존 자동 업데이트 설정은 유지합니다. 자동 업데이트를 새로 선택할 때만 README의 YAML을
`~/.omp/agent/config.yml`의 기존 `marketplace:` 항목에 합치고 `marketplace.autoUpdate`를 `auto`로 설정합니다.
omp는 시작할 때 24시간보다 오래된 카탈로그의 갱신을 가능한 범위에서 시도합니다. 설치한 플러그인을
자동 업데이트하려면 배포 카탈로그에서 해당 플러그인의 버전을 올려야 합니다. 같은 버전으로 `main`만
바꾸면 자동 업데이트 조건이 되지 않습니다. 상시 감시나 hot reload도 아닙니다.
새 버전을 바로 반영하려면 `omp plugin marketplace update sonsu-marketplace` 다음에
`omp plugin upgrade`를 실행합니다.

이전 구성의 제거와 불필요한 설정 정리는 [이동 가이드](../guides/migrating-from-earlier-versions.md#이전-omp-구성에서-이동)를 따릅니다.
정리한 뒤에는 세션을 끝내고 omp를 다시 시작해 이미 읽힌 이전 hook·agent를 내립니다.

## 검증

생성기의 `--check`, 호스트별 catalog·스킬 경로·frontmatter 검사, 실제 loader·행동 평가는 따로 확인합니다.
정적 JSON 검사를 통과했다는 사실만으로 실제 스킬 선택이나 호스트별 hook 동작을 확인했다고 보지 않습니다.
미실행은 `not_run`, 원인 불명은 `inconclusive`로 기록합니다.
[업데이트 런북](../runbooks/updating-upstream-plugin.md)과
[ADR 0015](../decisions/0015-independent-skills.md)를 따릅니다. 이전 Engineering 게이트 결정은
[ADR 0014](../decisions/0014-use-codex-managed-engineering.md)에 역사적 근거로 보존합니다.
