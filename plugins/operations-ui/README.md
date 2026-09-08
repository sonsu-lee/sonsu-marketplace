# Operations UI

`operations-ui`는 WMS, 배송, 고객지원, 금융 운영, 콘텐츠 검수처럼 **많은 상태와 데이터를 보고 다음 행동을 결정하는 B2B 화면**을 위한 Codex·Claude Code 플러그인입니다. 특정 산업의 용어가 아니라 작업 구조를 기준으로 라우팅합니다.

```sh
# Codex
codex plugin add operations-ui@sonsu-marketplace

# Claude Code
claude plugin install operations-ui@sonsu-marketplace
```

## 디자인 언어

기본 디자인 언어는 **Precision Operations Console**입니다.

- 밝은 작업 영역과 어두운 persistent navigation
- 정보 밀도가 높은 표와 분명한 계층
- blue primary/selection과 용도가 고정된 semantic colors
- 장식보다 상태, 위험, 다음 행동을 우선하는 화면 구성
- loading, empty, error, permission, long data와 overflow를 정상 상태로 취급

세부 규칙의 source of truth는 [design.md](references/design.md)이며 token 값은 [design-tokens.json](assets/design-tokens.json)에 있습니다.

## 스킬

- `design-operations-ui`: 신규 운영 화면을 Screen Contract부터 구현·검증합니다.
- `redesign-operations-ui`: 기존 화면의 기능, 상태와 권한을 추적 가능한 형태로 보존하며 재설계합니다.
- `audit-operations-ui`: 코드를 바꾸지 않고 화면과 증거를 품질 계약에 따라 감사합니다.
- `figma-operations-flow`: 사용자가 Figma를 명시했을 때만 Figma 화면·상태·동선을 Screen Contract에 연결합니다.

마케팅 사이트, 에디토리얼 페이지, 브랜드 캠페인, 일러스트레이션이 주목적인 요청은 이 플러그인의 기본 대상이 아닙니다.

## 실행 계약

1. [screen-contract.md](references/screen-contract.md)로 사용자, 작업, 엔터티, 상태, 권한, 위험과 검증 시나리오를 확정합니다.
2. [screen-patterns.md](references/screen-patterns.md)와 [ux-patterns.md](references/ux-patterns.md)에서 작업 구조에 맞는 패턴을 고릅니다.
3. 대상 저장소의 기존 stack, token, component와 test/browser harness를 우선 사용해 실제 코드를 구현합니다.
4. [quality-contract.md](references/quality-contract.md)의 G0–G7을 판정합니다.
5. 실제 앱 실행 정보와 브라우저 증거가 없으면 완료를 `passed`로 보고하지 않습니다.

Figma는 필수 선행 단계가 아닙니다. 명시적으로 요청된 경우에만 선택형 흐름으로 사용하며 Figma 증거는 실제 브라우저 게이트를 대체하지 않습니다.

## 계약 검증

```bash
python3 scripts/validate_contracts.py screen-contract assets/examples/outbound-management/screen-contract.json
python3 scripts/validate_contracts.py quality-report assets/examples/outbound-management/quality-report.json assets/examples/outbound-management/screen-contract.json
python3 scripts/validate_contracts.py evals ../../evals/operations-ui/cases.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

검증기는 구조적 모순과 허위 `overall=passed`를 막습니다. JSON parse나 fixture 검증은 실제 skill routing, 플랫폼별 plugin loader, target browser 실행을 증명하지 않습니다.
