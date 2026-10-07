# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-10-07

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
같은 패키지 파일을 사용합니다. `memory-manager`는 네 스킬과 저장 스크립트·훅을 별도 Claude
패키지에 생성합니다. 정리·승격 스킬만 Claude의 수동 호출 제한을 적용합니다. 모델 프로필은 호스트별로 분리하며, Codex connector와
Claude Code MCP 구성은 별도의 실행 환경 상태입니다.

## omp에는 6개만 배포한다

`python3 scripts/render-omp-compat.py`는 Codex catalog의 순서를 유지하며 `workflow`,
`fluent-korean`, `fluent-english`, `fluent-japanese`, `design`, `career` 6개만
`.omp-plugin/marketplace.json`에 생성합니다. Codex·Claude Code 배포 대상과 원본 패키지는 바꾸지 않습니다.

| 플러그인 | omp catalog의 source |
| --- | --- |
| Workflow | `./plugins/workflow/omp` |
| Fluent Korean | `./plugins/fluent-korean/omp` |
| Fluent English | `./plugins/fluent-english` |
| Fluent Japanese | `./plugins/fluent-japanese` |
| Design | `./plugins/design/omp` |
| Career | `./plugins/career` |

Design·Workflow의 omp 전용 패키지는 필요한 skills·references·assets·scripts·figma-plugin·라이선스를
원본 패키지에서 생성해 다른 플러그인 없이 쓸 수 있게 합니다. 스크립트의 실행 권한은 복사할 때 유지합니다.
독자 hook, evidence gate, `task-continuity.py`, omp runtime extension은 포함하지 않습니다. 원본 패키지의
hook·연속성 스크립트는 Codex·Claude Code용으로 남깁니다. Fluent Korean은 Codex 단일 호출 경로의
스킬·참고 자료·라이선스를 전용 패키지로 생성합니다. 품질 불변식을 유지하고 현재 호스트 모델을 사용하며,
Claude Code의 다중 호출·strict 모드와 고정 Opus 에이전트를 요구하지 않습니다. English·Japanese 스킬,
Design의 품질 계약·프로필, Workflow의 작업 권한 경계는 유지합니다.

생성된 `references/continuity.md`는 omp 순정 todo·session으로 작업을 이어 가도록 안내합니다.
`.sonsu`에 연속성 기록을 남기거나 복원 hook·세션 ID 전달을 따로 추가하지 않습니다.
개발 실행·task·todo·session·review는 omp 순정 기능이, Workflow·언어 3개·Design·Career는 도메인 계약을
담당합니다. Research·Product·Writing은 필요할 때 고르는 후보로 두고 기본 catalog에는 추가하지 않습니다.
커스텀 역할용 `task.agentModelOverrides`도 요구하지 않습니다. Engineering의 omp 모델 프로필은 직접
설치해 선택한 legacy 사용자의 기존 consumer를 위해 보존하고 기본 구성과 분리합니다.

생성물은 직접 편집하지 않습니다. 생성기는 `--check`로 내용·실행 권한의 최신 여부와 불필요한 이전 생성물을
확인하고, 일반 실행에서는 자신이 생성했다고 확인할 수 있는 이전 extension의 `package.json`·`extension.ts`만
정리합니다. 사용자의 파일, 기존 `.sonsu`·`.engineering` 기록과 설치 캐시는 삭제하거나 편집하지 않습니다.

### 공개와 사용자 업데이트를 구분한다

생성·검증·커밋, GitHub 공개, 사용 환경 반영은 서로 다른 작업입니다. 로컬 변경만으로 기존 GitHub 등록이나
설치된 패키지가 갱신됐다고 보지 않습니다.

사용자는 `~/.omp/agent/config.yml`의 `marketplace.autoUpdate`를 `auto`로 설정할 수 있습니다.
omp는 시작할 때 24시간보다 오래된 카탈로그의 갱신을 가능한 범위에서 시도합니다. 설치한 플러그인을
자동 업데이트하려면 배포 카탈로그에서 해당 플러그인의 버전을 올려야 합니다. 같은 버전으로 `main`만
바꾸면 자동 업데이트 조건이 되지 않습니다. 상시 감시나 hot reload도 아닙니다.

이전 구성의 제거와 불필요한 설정 정리는 [README의 이동 절차](../../README.md#omp)를 따릅니다.
정리한 뒤에는 세션을 끝내고 omp를 다시 시작해 이미 읽힌 이전 hook·agent를 내립니다.

## 검증

생성기의 `--check`, 호스트별 catalog·스킬 경로·frontmatter 검사, 실제 loader·행동 평가는 따로 확인합니다.
정적 JSON 검사를 통과했다는 사실만으로 실제 스킬 선택이나 호스트별 hook 동작을 확인했다고 보지 않습니다.
미실행은 `not_run`, 원인 불명은 `inconclusive`로 기록합니다.
[업데이트 런북](../runbooks/updating-upstream-plugin.md)과
[ADR 0015](../decisions/0015-independent-skills.md)를 따릅니다. 이전 Engineering 게이트 결정은
[ADR 0014](../decisions/0014-use-codex-managed-engineering.md)에 역사적 근거로 보존합니다.
