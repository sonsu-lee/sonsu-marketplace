# 플러그인 추가하기

## 사전 조건

- 추가할 플러그인의 이름, 출처와 라이선스를 확인합니다.
- 외부 플러그인이면 가져올 정확한 tag 또는 commit을 선택합니다.
- 기존 `plugins/`와 `.agents/plugins/marketplace.json`에서 같은 이름이 없는지 확인합니다.

## 절차

1. `plugins/<plugin-name>/`을 만들고 `.codex-plugin/plugin.json`을 작성합니다.
2. 필요한 구성 요소만 추가합니다. 스킬은 `skills/<skill-name>/SKILL.md`에 두고 매니페스트가
   해당 경로를 가리키게 합니다.
3. 외부 플러그인은 원본 파일과 실행 권한을 검증하고 `UPSTREAM.md`에 출처, 기준 commit,
   버전, 라이선스와 포함 범위를 기록합니다.
4. `.agents/plugins/marketplace.json`의 `plugins` 배열 끝에 등록합니다.

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

폴더명, 플러그인 매니페스트의 `name`과 마켓플레이스 항목의 `name`은 같아야 합니다.
`source.path`는 저장소 루트 기준 상대 경로입니다.

## 검증

```sh
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/<plugin-name>/.codex-plugin/plugin.json
```

JSON 문법과 참조 경로를 확인한 뒤 가능한 경우 Codex의 실제 플러그인 읽기 경로로 이름,
버전과 구성 요소 목록을 확인합니다. API 키와 토큰은 저장하지 않으며 필요한 환경 변수
이름만 `.env.example`에 기록합니다.
