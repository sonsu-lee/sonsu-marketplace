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
| `version` | 플러그인 버전 | 로컬 커스텀은 `<upstream>-sonsu.<revision>` 사용 |
| `description` | 기능 설명 | 실제 제공 범위만 기술 |
| `author` | 저작자 정보 | 업스트림 저작권과 출처를 보존 |
| `homepage`, `repository` | 원본 링크 | 업스트림의 공식 위치 사용 |
| `license` | 라이선스 식별자 | 포함한 라이선스 파일과 일치 |
| `skills` | 스킬 디렉터리 | 매니페스트 기준 상대 경로 사용 |
| `hooks` | hook 선언 | 업스트림 값과 현재 Codex 호환성을 별도 검증 |
| `interface` | Codex UI 메타데이터 | 표시 이름, 설명, 아이콘과 기능 범위 정의 |

## 마켓플레이스 연결

`.agents/plugins/marketplace.json`의 `source.path`는 마켓플레이스 JSON이 있는 디렉터리가
아니라 저장소 루트를 기준으로 합니다.

```json
{
  "name": "superpowers",
  "source": {
    "source": "local",
    "path": "./plugins/superpowers"
  }
}
```

정적 validator와 Codex 실제 런타임이 지원하는 필드가 다를 수 있습니다. 이 저장소의
Superpowers 매니페스트는 업스트림의 `hooks: {}`를 유지하므로 실제 `plugin/read` 결과를
최종 호환성 근거로 사용합니다.
