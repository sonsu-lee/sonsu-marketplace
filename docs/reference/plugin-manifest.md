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
