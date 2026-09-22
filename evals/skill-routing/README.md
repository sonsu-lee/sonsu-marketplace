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

평가 모델에는 `expected_*`, `must_*`와 정답을 암시하는 case ID를 주지 않습니다. fixture, 사용자 요청,
현재 native skill registry와 반환 schema만 줍니다.

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
marketplace의 exact 10개 pack을 설치한 뒤 `codex exec --ephemeral --ignore-user-config --sandbox read-only
--json`으로 실행합니다. nonsemantic case는 mcpls를 disabled로 고정합니다. semantic case는 mcpls만
활성화하고 `lsp_definition`, `lsp_references`만 allowlist합니다. registry prerequisite가 맞지 않으면
model을 호출하지 않고 case를 `blocked`로 기록합니다.

### OMP isolation

OMP는 disposable HOME에서 repository의 10개 `--plugin-dir`를 직접 로드하고 exact 31개 bare skill
name을 `--skills`로 제한합니다. `--no-rules --no-session --approval-mode always-ask --mode json -p`와
case별 최소 tool allowlist를 사용합니다. provider credential 환경 변수는 제거합니다. semantic case는
OMP native `lsp`만 사용하고 plugin의 Codex MCP metadata를 등록하지 않습니다.

## 판정

`pass`, `fail`, `blocked`, `not_run`, `inconclusive`를 구분합니다. native registry 발견, model selection,
tool behavior와 external mutation은 서로 다른 증거입니다. auth, exact `mcpls 0.6.0` 또는
`rust-analyzer`가 없으면 성공으로 표시하지 않고 blocker를 evidence에 기록합니다. 원격 ticket/PR,
Figma canvas와 repository file은 이 smoke에서 수정하지 않습니다.
