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
5. `python3 scripts/render-claude-compat.py`를 실행해 Claude Code용 catalog와 manifest를 생성합니다.

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
`.claude-plugin/marketplace.json`과 plugin별 `.claude-plugin/plugin.json`은 생성물이므로 직접
수정하지 않습니다. Claude Code에만 필요한 새 변환 규칙이 생기면 renderer와 fixture 기대값을
먼저 갱신합니다. 공용 `SKILL.md`에 넣을 수 없는 Claude 전용 frontmatter가 필요하면
`plugins/<plugin-name>/.claude-plugin/compat.json`에 projection을 선언합니다. renderer는 Codex 정본을
그대로 두고 `.claude-plugins/<plugin-name>/`에 Claude Code용 패키지를 생성합니다.

## 검증

```sh
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/<plugin-name>/.codex-plugin/plugin.json
python3 scripts/render-claude-compat.py --check
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
claude plugin validate . --strict
claude plugin validate plugins/<plugin-name> --strict
# compat.json을 선언한 플러그인
claude plugin validate .claude-plugins/<plugin-name> --strict
```

JSON 문법과 참조 경로를 확인한 뒤 가능한 경우 Codex의 실제 플러그인 읽기 경로와 격리된
Claude Code 설정에서 이름, 버전과 구성 요소 목록을 각각 확인합니다. 한 플랫폼의 정적 검증을
다른 플랫폼의 로딩 성공으로 간주하지 않습니다. API 키와 토큰은 저장하지 않으며 필요한 환경
변수 이름만 `.env.example`에 기록합니다.
