# 플러그인 매니페스트 참조

이 문서는 Sonsu Marketplace의 로컬 계약입니다. 공식 Codex/OMP 형식을 대체하지 않으며 새 field는
현재 host 문서와 model-free loader 결과를 함께 확인합니다.

## 파일 위치와 정본

```text
.agents/plugins/marketplace.json                 # Codex catalog
.omp-plugin/marketplace.json                     # OMP name/version/path projection
plugins/<name>/.codex-plugin/plugin.json         # package manifest
plugins/<name>/skills/<skill>/SKILL.md            # 두 host 공통 skill
```

Folder, manifest, 두 catalog의 `name`은 같고 현재 10개 manifest version은 모두 `1.0.0`입니다. Codex
`source.path`는 repository root 기준 `./plugins/<name>`, OMP `source`는 `metadata.pluginRoot` 기준
`./<name>`입니다.

## 현재 사용하는 manifest field

| Field | 계약 |
| --- | --- |
| `name` | folder와 catalog entry에 일치 |
| `version` | 현재 major cutover의 exact `1.0.0` |
| `description` | 실제 package 책임과 negative boundary |
| `author` | 현재 배포·유지관리 주체; 원저작권은 license/UPSTREAM에 보존 |
| `license` | 실제 포함한 license file과 일치할 때만 사용 |
| `skills` | package-relative skill directory array |
| `apps` | Codex-only connector metadata; 현재 Figma Workflow만 사용 |
| `mcpServers` | Codex-only MCP declaration; 현재 Code Intelligence만 사용 |
| `interface` | 지원 host의 표시 metadata |

Marketplace-owned `hooks`는 없습니다. 공통 router, setup, continuity, evidence gate 또는 model policy를
manifest에 선언하지 않습니다.

## Marketplace entry

```json
{
  "name": "code-review",
  "source": {
    "source": "local",
    "path": "./plugins/code-review"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Developer Tools"
}
```

Code Intelligence도 `installation: AVAILABLE`이며 catalog 등록이 설치·실행·workspace trust를 자동
승인하지 않습니다.

## Codex-only metadata

### Figma apps

`plugins/figma-workflow/.codex-plugin/plugin.json`의 `apps: "./.app.json"`은 registered connector를
찾는 metadata입니다. OAuth, seat, capability 또는 canvas mutation 권한을 부여하지 않습니다.
OMP catalog에는 이를 복사하지 않습니다.

### Code Intelligence MCP

`plugins/code-intelligence/.codex-plugin/plugin.json`의 `mcpServers: "./codex-mcp.json"`은 Codex에서
native LSP가 없을 때 가능한 fallback entrypoint입니다. `codex-mcp.json`은 installed plugin의
relative cwd에서 `scripts/launch-mcpls.py`를 실행합니다.

Launcher는 PATH의 exact `mcpls 0.6.0`, canonical current directory와 별도 language server를 요구하며
network install이나 version fallback을 수행하지 않습니다. `MCPLS_CONFIG`는 package의 absolute config,
`MCPLS_TRUST_PROJECT_CONFIG=false`, JSON warning log로 고정됩니다. secret 값을 manifest/env에 넣지
않습니다. Codex는 plugin load 때 MCP를 초기화할 수 있으므로 trust 확인 전 semantic tool 호출을
금지합니다.

OMP는 이 MCP metadata를 사용하지 않고 host-native `lsp`를 사용합니다. prerequisite가 없으면 semantic
operation은 `blocked`이며 text search로 definition/reference 결과를 모사하지 않습니다.

## 검증

정적 검사로 catalog parity, path, version, skill inventory, unsafe config와 host-specific metadata를
확인합니다. Codex `plugin/read`, `skills/list`, `hooks/list`와 OMP disposable marketplace discovery를
별도 model-free probe로 관찰합니다. JSON parse 성공을 native load 성공으로 보고하지 않습니다.
