# 플러그인 매니페스트 참조

이 문서는 Sonsu Marketplace에서 사용하는 로컬 규칙을 설명합니다. 전체 Codex 형식의
대체 문서가 아니며, 새 필드를 추가할 때에는 현재 공식 문서와 실제 Codex 읽기 결과를
확인합니다.

## 파일 위치

```text
plugins/<plugin-name>/.codex-plugin/plugin.json
```

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
| `hooks` | hook 선언 | 업스트림 값과 현재 Codex 호환성을 별도 검증 |
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

정적 validator와 Codex 실제 런타임이 지원하는 필드가 다를 수 있습니다. 이 저장소의
Engineering 매니페스트는 `hooks: {}`를 사용하므로 실제 `plugin/read` 결과를 최종 호환성
근거로 사용합니다.

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
