# Sonsu Marketplace

개인적으로 사용하는 Codex 플러그인을 관리하는 마켓플레이스입니다.
현재는 기본 구조만 준비되어 있으며, 등록된 플러그인은 없습니다.

## 저장소 구조

```text
sonsu-marketplace/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   └── .gitkeep
├── .gitignore
└── README.md
```

- `.agents/plugins/marketplace.json`에는 마켓플레이스 정보와 플러그인 목록을 정의합니다.
- `plugins/`에는 각 플러그인을 별도 폴더로 보관합니다.
- 마켓플레이스 식별자는 `sonsu-marketplace`, 표시 이름은 `Sonsu Marketplace`입니다.

## Codex에 등록하기

`codex plugin` 명령을 지원하는 Codex CLI에서 저장소 루트를 기준으로 실행합니다.

```sh
codex plugin marketplace add .
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

등록 명령에는 `marketplace.json` 파일 경로가 아닌 저장소 루트 경로를 전달합니다.
플러그인을 추가하기 전에는 목록이 비어 있습니다. 저장소를 만드는 것만으로
사용자의 Codex 설정에 마켓플레이스가 자동 등록되지는 않습니다.

## 플러그인 추가하기

1. `plugins/<plugin-name>/` 폴더를 만들고 `.codex-plugin/plugin.json`에 플러그인 정보를 작성합니다.
2. 필요한 구성 요소만 추가합니다. 스킬은 `skills/<skill-name>/SKILL.md`에,
   MCP 서버 설정은 `.mcp.json`에 작성하고 플러그인 매니페스트에 연결합니다.
3. `.agents/plugins/marketplace.json`의 `plugins` 배열에 다음 형식으로 항목을 추가합니다.

```json
{
  "name": "my-plugin",
  "source": {
    "source": "local",
    "path": "./plugins/my-plugin"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

`my-plugin`은 예시 이름입니다. 폴더명, 플러그인 매니페스트의 `name`,
마켓플레이스 항목의 `name`을 같은 값으로 지정합니다.
`source.path`는 `.agents/plugins/`가 아닌 **저장소 루트 기준 상대 경로**입니다.
`plugins` 배열의 순서는 Codex에 표시되는 순서이므로 새 항목은 끝에 추가합니다.

API 키와 토큰은 플러그인 파일에 직접 저장하지 않습니다.
로컬 `.env` 파일은 Git에서 제외하고, 필요한 환경 변수 이름만 `.env.example`에 기록합니다.

## 형식 확인

저장소 루트에서 JSON 문법을 확인할 수 있습니다.

```sh
python3 -m json.tool .agents/plugins/marketplace.json
```

이 명령은 JSON 문법만 확인합니다. 플러그인을 추가한 뒤에는 매니페스트와
참조 경로를 검토하고 Codex에서 설치 및 실행까지 확인합니다.

마켓플레이스 경로와 소스 형식은 [OpenAI 공식 문서](https://learn.chatgpt.com/docs/enterprise/plugin-management#supported-formats)를 따릅니다.
