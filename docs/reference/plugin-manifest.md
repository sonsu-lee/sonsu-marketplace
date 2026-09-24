# 플러그인 매니페스트 참조

이 문서는 Sonsu Marketplace의 세 호스트 매니페스트 관계를 설명합니다. 새 필드를 추가할 때에는
현재 공식 문서와 실제 로더 결과를 확인합니다.

## 파일 위치

```text
.agents/plugins/marketplace.json                 # 정본 marketplace catalog
plugins/<plugin-name>/.codex-plugin/plugin.json  # 정본 plugin manifest
.omp-plugin/marketplace.json                     # OMP catalog
.claude-plugin/marketplace.json                  # 생성된 Claude catalog
plugins/<plugin-name>/.claude-plugin/plugin.json # 생성된 Claude manifest
```

Codex 형식을 저장소의 정본으로 유지합니다. `interface`, `apps`, `hooks`는 각 필드를 지원하는
Codex 로더에서만 실제 소비 결과를 확인합니다.
`scripts/render-claude-compat.py`가 Codex 카탈로그·매니페스트를 읽고 OMP의 이름·버전·경로를
대조한 다음 Claude 파일을 만듭니다. `--check`는 생성 결과의 drift를 실패로 보고합니다.

## 현재 사용하는 필드

| 필드 | 용도 | 로컬 규칙 |
| --- | --- | --- |
| `name` | 플러그인 식별자 | 폴더명과 marketplace 항목 이름에 맞춤 |
| `version` | 플러그인 버전 | 단일 upstream fork는 `<upstream>-sonsu.<revision>`, 여러 source를 합성하거나 새로 설계한 plugin은 독립 semantic version 사용 |
| `description` | 기능 설명 | 실제 제공 범위만 기술 |
| `author` | 현재 배포·유지관리 주체 | 로컬 fork는 로컬 주체를 표시하고 원저작자와 저작권은 `LICENSE`와 `UPSTREAM.md`에 보존 |
| `homepage`, `repository` | 현재 배포본의 공개 위치 | 유지되는 로컬 공개 위치가 없으면 생략하고 원본 링크는 `UPSTREAM.md`에 기록 |
| `license` | 라이선스 식별자 | 포함한 라이선스 파일과 일치 |
| `skills` | 스킬 디렉터리 | 매니페스트 기준 상대 경로 사용 |
| `hooks` | hook 선언 | plugin-relative `./hooks/hooks.json`; 실제 로더 노출과 hook 실행·신뢰를 별도 검증 |
| `interface` | Codex UI 메타데이터 | 표시 이름, 설명, 아이콘과 기능 범위 정의 |
| `apps` | 등록된 Codex connector 선언 | plugin-relative `.app.json`만 가리키며, connector ID와 실제 노출은 Codex가 소유 |

Engineering은 독립 플러그인으로 관리하므로 `1.0.0`부터 독립 semantic version을 사용하고
upstream 기준선이나 이전 호환 경로를 매니페스트 계약으로 두지 않습니다. MIT 고지는
[`LICENSE`](../../plugins/engineering/LICENSE)에 보존합니다.

## 마켓플레이스 연결

`.agents/plugins/marketplace.json`의 `source.path`는 마켓플레이스 JSON이 있는 디렉터리가
아니라 저장소 루트를 기준으로 합니다.

```json
{
  "name": "engineering",
  "source": {
    "source": "local",
    "path": "./plugins/engineering"
  }
}
```

정적 validator와 Codex 실제 런타임이 지원하는 필드가 다를 수 있습니다. `profiles.json`에 등록된 플러그인은
`hooks: "./hooks/hooks.json"`으로 작업 연속성 hook을 포함합니다. `plugin/read`, `skills/list`와
`hooks/list`로 패키지·스킬·event·matcher를 확인하고, 실제 실행은 별도로 관찰합니다.
Codex에서는 설치만으로 hook이 신뢰되지는 않으며 현재 정의를 사용자가 검토해야 합니다. Claude는
활성 플러그인의 hook을 자동 병합하며 `/hooks`는 읽기 전용 확인 메뉴입니다. 정확한 동작과
수동 복구는 [작업 연속성 계약](task-continuity.md)을 따릅니다.

Catalog의 각 local `source.path`는 해당 `plugins/<plugin-name>` 디렉터리를 가리켜야 합니다.
Codex의 실제 `plugin/read`, `skills/list`, `hooks/list` 검증은 정적 JSON 검사와 별개의 관찰 결과로 기록합니다.

Claude 카탈로그의 각 항목은 `source: "./plugins/<name>"`을 사용합니다. Claude 매니페스트는
이름·버전·설명 등 호환 메타데이터만 담습니다. `skills/`와 `hooks/hooks.json`은 Claude의 표준
위치에서 발견되므로 명시 필드를 다시 넣지 않습니다. `claude plugin validate --strict .`와
각 플러그인 검증, 분리된 설정 디렉터리의 실제 설치·발견을 각각 확인합니다. Claude용 Figma
연결은 공식 Figma 플러그인을 사용하며 Codex `apps` 선언을 복사하지 않습니다.

## Figma Workflow connector와 companion 경계

`plugins/figma-workflow/.codex-plugin/plugin.json`은 `apps: "./.app.json"`으로 등록된 official
Figma connector를 참조합니다. `.app.json`의 실제 shape는 다음과 같습니다.

```json
{ "apps": { "figma": { "id": "connector_68df038e0ba48191908c8434991bbac2" } } }
```

이 선언은 Codex가 connector를 찾는 metadata이며 OAuth, seat, capability 또는 canvas mutation 권한을
부여하지 않습니다. 실제 `use_figma` 호출은 installed official contract의 `figma:figma-use`
prerequisite를 먼저 적용하고, capability가 없으면 `blocked`, `inconclusive` 또는 `not_run`으로
상태를 구분합니다.

`plugins/figma-workflow/figma-plugin/manifest.json`은 Figma Desktop에서 사용자가 직접 import하는
development companion manifest입니다. 이는 Codex plugin manifest나 agent-callable MCP bridge가 아니며,
manual companion은 registered connector와 별개의 두 번째 writer가 아닙니다. companion은 versioned
allowlist JSON만 받고 network access를 허용하지 않으며, mutation 전에 explicit target·preview receipt·
apply-time readback을 요구합니다.
