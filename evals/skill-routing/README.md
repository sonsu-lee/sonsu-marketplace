# Thin capability pack routing 평가

[`cases.json`](cases.json)은 31개 skill의 positive ownership, host baseline negative routing,
`review-pr` explicit-only, Code Intelligence semantic/no-prerequisite와 한 가지 runtime composition을
정의합니다. JSON parse나 description 문자열 비교는 native selection 결과가 아닙니다.

## Case 계약

- `mode: ownership`: 요청에 필요한 marketplace skill name만 반환하는 native selection smoke.
- `mode: behavior`: 실제 tool 사용과 결과 상태를 확인하는 대표 동작 smoke.
- `expected_skills`: 순서와 무관한 exact 선택 집합. 빈 배열은 host baseline입니다.
- `must_not_select`: 기대 집합 밖에서 특히 금지하는 오선택.
- `semantic`: trusted Rust fixture와 semantic tool prerequisite가 필요한 case.
- `disable_semantic_prerequisite`: prerequisite 부재를 만들고 text fallback 없이 `blocked`인지 확인.
- `must_contain`: representative behavior 결과에서 관찰할 consumer-visible 값.
- `expected_semantic_trace`: 성공 case에서 실제 definition/reference tool result에 반드시 포함될 fixture 위치.

평가 모델에는 `expected_*`, `must_*`, 정답을 암시하는 case ID를 주지 않습니다. fixture, 원래 사용자
요청, host의 native discovery 결과와 반환 schema만 줍니다. Codex catalog도 runner의 수기 목록이
아니라 같은 disposable config에서 실행한 app-server `skills/list` 응답으로 만듭니다.

## Native smoke

```sh
python3 evals/skill-routing/native_smoke.py --help
python3 evals/skill-routing/native_smoke.py \
  --host both --mode ownership --cases evals/skill-routing/cases.json \
  --output /absolute/evidence/ownership
python3 evals/skill-routing/native_smoke.py \
  --host both --mode behavior --cases evals/skill-routing/cases.json \
  --case semantic-missing-prerequisite --output /absolute/evidence/failure-mode
python3 evals/skill-routing/native_smoke.py \
  --host both --mode behavior --cases evals/skill-routing/cases.json \
  --case semantic-definition-references --output /absolute/evidence/semantic
```

CLI는 `--host codex|omp|both`, `--mode ownership|behavior`, `--cases`, 반복 가능한 `--case`, `--output`
만 평가 선택 인자로 받습니다. model, thinking, reviewer roster를 override하지 않고 trace에서 실제로
관찰된 model field를 기록합니다.

### Codex isolation

각 run은 새 HOME/CODEX_HOME을 만들고 기존 `auth.json`이 있으면 read-only copy만 사용합니다. local
marketplace의 exact 10개 pack을 설치하고 이 disposable `config.toml`만 읽도록 합니다. 먼저 같은
환경의 app-server `skills/list`가 exact 31개 namespaced skill을 반환하는지 확인하고, 그 native
catalog를 `codex exec --ephemeral --sandbox read-only --json` routing context로 전달합니다.
`--ignore-user-config`는 설치한 plugin enable 설정까지 버리므로 사용하지 않습니다. nonsemantic case는
plugin-owned mcpls를 disabled로 고정합니다. semantic case는 mcpls만 활성화하고 실제 mcpls 0.6.0
이름인 `lsp_get_definition`, `lsp_get_references`만 allowlist합니다. registry/install 결과가
marketplace 계약과 다르면 model을 호출하지 않고 case를 `fail`로 기록합니다.

### OMP isolation

OMP는 disposable HOME에서 repository의 10개 `--plugin-dir`를 직접 로드하고 exact 31개 bare skill
name을 `--skills`로 제한합니다. `--no-rules --no-session --approval-mode always-ask --mode json -p`와
case별 최소 tool allowlist를 사용합니다. provider credential 환경 변수는 제거합니다. model behavior를
실행할 때는 `PI_CODING_AGENT_DIR`이 명시적으로 지정한 disposable source profile의 `agent.db`와
선택적인 config/model/LSP 파일만 임시 경로로 복사합니다. 값이 없거나 profile이 불완전하면 case는
구조화된 `blocked`로 남습니다. semantic case는 OMP native `lsp`만 사용하고 plugin의 Codex MCP
metadata를 등록하지 않습니다.

## 판정

`pass`, `fail`, `blocked`, `not_run`, `inconclusive`를 구분합니다. native registry 발견, model selection,
tool behavior와 external mutation은 서로 다른 증거입니다. 응답 field type/enum을 host와 무관하게
검증하며 case 실행 뒤 CLI nonzero exit는 환경 blocker가 아닌 `fail`입니다. semantic success는
definition과 references tool result에 fixture의 기대 위치가 모두 있어야 통과합니다. auth, exact
`mcpls 0.6.0` 또는 `rust-analyzer`가 없으면 model 실행 전 blocker로 evidence에 기록합니다. 원격
ticket/PR, Figma canvas와 repository file은 이 smoke에서 수정하지 않습니다.
