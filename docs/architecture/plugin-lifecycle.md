# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-09-23

## 흐름

```text
후보 capability와 host baseline 비교
  → 실제로 필요한 얇은 boundary만 선택
  → 포함/consulted-only upstream과 license 기록
  → package manifest + shared skills
  → Codex catalog + OMP projection
  → 정적 계약 검사
  → model-free native loader probe
  → explicit behavior smoke
  → release 또는 근거 있는 blocked/not_run
```

Host가 이미 제공하는 general coding/research/writing/continuity 동작은 plugin으로 복제하지 않습니다.
새 capability는 다른 package 설치, 공통 router, setup skill, fixed model roster 또는 hook 없이 독립
실행되어야 합니다.

## 출처와 버전

복사한 외부 파일은 exact source path, 기준 commit, 최종 path와 license를 `UPSTREAM.md`와 notice에
기록합니다. 아이디어만 검토하고 파일을 포함하지 않은 자료는 `consulted-only`로 표시하며 재배포
license를 package에 주장하지 않습니다. runtime dependency는 다운로드하지 않고 정확한 version,
upstream commit, license와 실행 전제만 기록합니다.

현재 10개 package는 깨끗한 major cutover로 모두 `1.0.0`입니다. 삭제한 package 이름에는 alias,
wrapper 또는 deprecated path를 두지 않습니다.

## Codex 정본과 OMP projection

`.agents/plugins/marketplace.json`과 package별 `.codex-plugin/plugin.json`이 Codex 정본입니다.
`.omp-plugin/marketplace.json`은 같은 10개 이름·version·path를 투영합니다. 두 host는 같은 31개
`skills/`를 로드합니다. Figma `apps`와 Code Intelligence `codex-mcp.json`은 Codex-only metadata이고
OMP catalog에는 `mcp`/`lsp` 설정으로 복사하지 않습니다.

## 검증 층

1. JSON/frontmatter, exact inventory, 상대 경로, version과 unsafe config를 정적으로 검사합니다.
2. Codex app-server stdio와 OMP disposable marketplace로 실제 loader registry를 model 없이 검사합니다.
3. ownership case와 대표 behavior를 native CLI로 실행합니다.
4. semantic case는 exact mcpls/language-server prerequisite가 있을 때만 실행합니다.

정적 통과는 loader 성공이 아니고, registry 발견은 model behavior 성공이 아닙니다. 실행하지 못한
항목은 성공으로 바꾸지 않고 exact blocker와 함께 `blocked`/`not_run`/`inconclusive`로 남깁니다.

## Observability와 privacy

Code Intelligence는 자체 telemetry나 별도 log store를 만들지 않습니다. mcpls의 JSON stderr는 host가
수집할 수 있으며 skill은 사용자가 명시적으로 진단을 요청했을 때만 warning과 함께 필요한 최소
log를 보여 줍니다. Codex의 analytics, `log_dir`, OpenTelemetry 설정과 OMP의 session JSONL, stats,
OTLP, `pi.logger`는 각 host의 기존 설정 그대로입니다.

운영자는 host log와 외부 collector의 retention, export, deletion을 각각 관리합니다. marketplace의
기본 설정은 raw prompt export를 켜지 않고 collector endpoint도 제공하지 않습니다. 삭제가 필요하면
host local log와 collector 보관본을 별도로 삭제해야 합니다.

## 업데이트와 migration

업스트림 반영은 [업데이트 런북](../runbooks/updating-upstream-plugin.md)을 따릅니다. 제거한
`engineering`, `research`, `fluent-languages`, `memory-manager`, `writing` 설치는 README의 host별 명령으로
사용자가 명시적으로 제거합니다. 기존 cache, `.sonsu/continuity`, `.engineering` artifact는 자동으로
읽거나 이동하거나 삭제하지 않습니다.
