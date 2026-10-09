# 이전 버전에서 이동하기

이전 omp 구성이나 `fluent-languages`를 설치한 사용자를 위한 절차입니다. 처음 설치한다면 [설치 안내](../../README.md#설치)를 따르세요.

## 이전 omp 구성에서 이동

이전 11개 구성이나 8개 preset을 사용했다면 다음 중 설치한 이전 플러그인을 omp에서 제거합니다.
설치하지 않은 항목의 `not installed` 오류는 무시합니다. Codex·Claude Code 설치는 유지합니다.
`design-patterns`는 opt-in 패키지로 계속 제공하므로 제거 목록에 없습니다.

```sh
for plugin in engineering writing research prompting product memory-manager operations-ui interface-design figma-workflow; do omp plugin uninstall "$plugin@sonsu-marketplace"; done
```

이전에 등록한 `sonsu-marketplace`가 로컬 체크아웃 경로이거나 오래된 카탈로그일 수 있으므로 GitHub 소스로
다시 등록합니다. 마켓플레이스 등록을 제거해도 설치된 플러그인은 제거되지 않습니다. 이미 설치한
`workflow`·`fluent-korean`·`design`은 일반 `install`로 갱신되지 않으므로 `--force`로 다시 설치합니다.

```sh
omp plugin marketplace remove sonsu-marketplace
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in workflow fluent-korean fluent-english fluent-japanese design; do omp plugin install --force "$plugin@sonsu-marketplace"; done
```

`design-patterns`를 계속 쓰려면 다시 등록한 뒤 `omp plugin install --force design-patterns@sonsu-marketplace`로 갱신합니다.

이전 preset 때문에 추가한 `skills.ignoredSkills`, `task.disabledAgents`, `task.agentModelOverrides`
항목만 설정에서 제거하고 사용자가 별도로 설정한 항목은 유지합니다. 세션을 종료하고 omp를 다시
시작합니다. 실행 중 세션에는 이전 hook·agent가 남아 있을 수 있습니다.
캐시 파일을 직접 편집하거나 기존 `.sonsu`·`.engineering` 기록을 삭제하지 않습니다.

## fluent-languages에서 언어별 플러그인으로 이동

이전 `fluent-languages` 설치본이 있으면 언어 스킬의 적용 범위가 겹치므로 먼저 제거하고 필요한
언어 플러그인을 설치하세요. 새 스킬 ID는 `fluent-korean:fluent-korean`,
`fluent-english:fluent-english`, `fluent-japanese:fluent-japanese`입니다. 영어는 일상·기술 문장의 작성·윤문·검토에,
일본어는 작성·윤문과 문서 진단에 사용할 수 있습니다. 한국어는 새 글의 생성 규칙과 기존 글의 AI 티·번역투 윤문에 적용합니다.
기존 작업 연속성 기록은 보존되지만 자동 이전되지 않으며 [수동 복구 절차](../reference/task-continuity.md)에 따라 확인합니다.

```sh
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin add fluent-korean@sonsu-marketplace
codex plugin add fluent-english@sonsu-marketplace
codex plugin add fluent-japanese@sonsu-marketplace
```

Claude Code에서는 `claude plugin uninstall fluent-languages@sonsu-marketplace` 후 필요한 언어
플러그인을 `claude plugin install <name>@sonsu-marketplace`로 설치합니다. 다른 마켓플레이스의
동명 스킬이나 standalone `prompt-builder`, `product-discovery`, `to-prd`도 중복되지 않도록 확인하세요.
설치·업데이트 후에는 새 Codex 작업 또는 Claude Code 세션에서 확인합니다.
