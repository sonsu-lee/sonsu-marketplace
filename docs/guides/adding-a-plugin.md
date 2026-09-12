# 플러그인 개발·수정·추가하기

플러그인을 로컬에서 수정하고 검증하거나 새 플러그인을 마켓플레이스에 추가하는 절차입니다.
구성 요소와 로딩 경계는 [아키텍처 개요](../architecture/overview.md), 외부 원본을 갱신하는
절차는 [업스트림 업데이트 런북](../runbooks/updating-upstream-plugin.md)을 참고하세요.

## 로컬 개발 환경

저장소를 clone하고 사용하는 에이전트에서 로컬 마켓플레이스로 등록합니다.

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
```

Codex에서는 `codex plugin` 명령을 지원하는 CLI를 사용합니다.

```sh
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace
```

Claude Code에서는 다음 명령을 사용합니다.

```sh
claude plugin marketplace add . --scope local
claude plugin list --available --json
```

GitHub 소스와 로컬 경로는 같은 `sonsu-marketplace` 식별자를 사용하므로 한 환경에서는 한 가지
방식으로 등록합니다. 실제 등록·설치 검증에는 기존 사용자 설정과 분리된 환경을 사용하세요.
플러그인 설치와 설치 후 스킬 목록을 다시 불러오는 방법은 [루트 README](../../README.md#설치)에 있습니다.

## 기존 플러그인 수정

1. 해당 플러그인의 README와 매니페스트에서 수정할 스킬·hook·script의 진입점을 확인합니다.
   외부 원본이 포함되어 있으면 `UPSTREAM.md`에서 원본과 로컬 변경의 경계를 확인합니다.
2. 수정 대상의 정본을 갱신합니다. Fluent Languages의 스킬 문구는 `plugins/fluent-languages/sources/`를 고친 뒤
   `python3 plugins/fluent-languages/scripts/render-skills.py`로 생성합니다.
3. Claude Code용 생성 결과에 영향을 주는 변경이면 `python3 scripts/render-claude-compat.py`를
   실행합니다. 생성된 catalog·manifest·호환 패키지는 직접 수정하지 않습니다.
4. 변경한 동작에 맞는 평가를 [evals/](../../evals/)에서 선택하고 아래 검증을 실행합니다.
   사용법·계약·개발 절차가 달라졌다면 [문서 배치 기준](../README.md)에 따라 담당 문서를 갱신합니다.

## 새 플러그인 추가

### 사전 조건

- 추가할 플러그인의 이름, 출처와 라이선스를 확인합니다.
- 외부 플러그인이면 가져올 정확한 tag 또는 commit을 선택합니다.
- 기존 `plugins/`와 `.agents/plugins/marketplace.json`에서 같은 이름이 없는지 확인합니다.

### 절차

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

저장소 루트에서 다음 정적 검사를 실행합니다.

```sh
find .agents .claude-plugin .claude-plugins plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 scripts/render-claude-compat.py --check
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
claude plugin validate . --strict
git diff --check
```

플러그인을 추가하거나 구조를 변경했다면 `<plugin-name>`을 해당 이름으로 바꿔 개별 패키지도 검사합니다.

```sh
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/<plugin-name>/.codex-plugin/plugin.json
claude plugin validate plugins/<plugin-name> --strict
# compat.json을 선언한 플러그인
claude plugin validate .claude-plugins/<plugin-name> --strict
```

이 명령은 JSON 구문, 생성 결과와 정본의 일치 여부, 평가 fixture·runner와 호환 패키지의 구조를
확인합니다. 실제 모델의 스킬 선택이나 출력 품질은 별도 검증이 필요합니다. 구조를 변경했다면
격리된 Codex와 Claude Code 환경에서 마켓플레이스 등록, 플러그인 설치와 스킬 노출을 확인하고,
플러그인의 이름·버전·구성 요소와 참조 경로를 대조합니다. 한 플랫폼의 정적 검증을 다른 플랫폼의
로딩 성공으로 간주하지 않습니다. API 키와 토큰은 저장하지 않으며 필요한 환경 변수 이름만
`.env.example`에 기록합니다.

플랫폼별 형식은 [OpenAI 공식 플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins)와
[Anthropic 공식 marketplace 문서](https://code.claude.com/docs/en/plugin-marketplaces)를 따릅니다.
