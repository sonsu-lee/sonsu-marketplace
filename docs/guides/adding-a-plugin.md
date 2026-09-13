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

GitHub 소스와 로컬 경로는 같은 `sonsu-marketplace` 식별자를 사용하므로 한 환경에서는 한 가지
방식으로 등록합니다. 실제 등록·설치 검증에는 기존 사용자 설정과 분리된 환경을 사용하세요.
플러그인 설치와 설치 후 스킬 목록을 다시 불러오는 방법은 [루트 README](../../README.md#설치)에 있습니다.

## 기존 플러그인 수정

1. 해당 플러그인의 README와 매니페스트에서 수정할 스킬·hook·script의 진입점을 확인합니다.
   외부 원본이 포함되어 있으면 `UPSTREAM.md`에서 원본과 로컬 변경의 경계를 확인합니다.
2. 수정 대상의 정본을 갱신합니다. Fluent Languages의 스킬 문구는 `plugins/fluent-languages/sources/`를 고친 뒤
   `python3 plugins/fluent-languages/scripts/render-skills.py`로 생성합니다.
3. 변경한 동작에 맞는 평가를 [evals/](../../evals/)에서 선택하고 아래 검증을 실행합니다.
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
`.agents/plugins/marketplace.json`과 plugin별 `.codex-plugin/plugin.json`이 Codex 패키지의 정본입니다.

## 검증

저장소 루트에서 다음 정적 검사를 실행합니다.

```sh
find .agents plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 scripts/render-agent-policy.py --check
python3 scripts/render-continuity.py --check
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
git diff --check
```

플러그인을 추가하거나 구조를 변경했다면 `<plugin-name>`을 해당 이름으로 바꿔 개별 패키지도 검사합니다.

```sh
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/<plugin-name>/.codex-plugin/plugin.json
```

JSON 문법과 참조 경로를 확인한 뒤 가능한 경우 Codex의 실제 플러그인 읽기 경로에서 이름, 버전과
구성 요소 목록을 확인합니다. 정적 검증을 실제 로딩 성공으로 간주하지 않습니다. API 키와 토큰은 저장하지 않으며 필요한 환경
변수 이름만 `.env.example`에 기록합니다.
