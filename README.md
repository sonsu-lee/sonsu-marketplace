# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

개발, 리서치, 제품 기획과 글쓰기에 사용하는 Codex·Claude Code·omp 플러그인 모음입니다.
필요한 플러그인만 골라 설치하고, 사용하는 코딩 에이전트에 평소처럼 작업을 요청하세요.

[설치](#설치) · [플러그인](#플러그인) · [사용 예시](#사용-예시) · [문서](docs/README.md)

## 설치

### Codex

`codex plugin` 명령을 지원하는 Codex CLI에서 GitHub 마켓플레이스를 한 번 등록합니다.
이미 등록했다면 이 단계는 생략하세요.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

필요한 플러그인만 설치합니다. 예를 들어 개발 작업에는 Engineering을 사용할 수 있습니다.

```sh
codex plugin add engineering@sonsu-marketplace
```

다른 플러그인은 [아래 표](#플러그인)의 설치 이름으로 바꿔 설치하세요.
12개를 모두 설치하려면 다음 명령을 실행합니다.

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  codex plugin add "$plugin@sonsu-marketplace"
done
```

등록된 소스와 각 플러그인의 설치 상태를 확인한 뒤 새 Codex 작업을 시작하세요.

```sh
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

Codex 데스크톱 앱에서 이 저장소를 열면 `.agents/plugins/marketplace.json`의 로컬 카탈로그도
표시될 수 있습니다. 같은 이름의 Git 등록본이 있으면 로컬 플러그인 변경이 가려질 수 있으므로,
두 항목이 보인다는 사실만으로 로컬 변경이 적용됐다고 판단하지 마세요. 현재 체크아웃은
Git 등록본이 없는 환경에서 [로컬 등록 절차](docs/guides/adding-a-plugin.md#로컬-개발-환경)로 시험하세요.

### Claude Code

Claude Code CLI에서는 GitHub 마켓플레이스를 한 번 등록합니다. 이미 등록했다면 생략하세요.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
```

필요한 플러그인만 설치합니다. 예를 들어 Engineering을 설치하려면 다음과 같이 실행합니다.

```sh
claude plugin install engineering@sonsu-marketplace
```

[아래 표](#플러그인)의 12개를 모두 설치하려면 다음 명령을 실행합니다.

```sh
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product memory-manager design-patterns design
do
  claude plugin install "$plugin@sonsu-marketplace"
done
```

등록된 마켓플레이스와 설치 상태를 확인하세요.

```sh
claude plugin marketplace list
claude plugin list
```

현재 체크아웃을 시험할 때에는 저장소 루트에서 `claude plugin marketplace add "$(pwd -P)"`로
로컬 경로를 등록합니다. GitHub 소스와 이름이 `sonsu-marketplace`로 같으므로 사용할 소스
하나를 선택하세요.
스킬은 `/engineering:review`처럼 호출합니다. 설치·업데이트 후 새 세션에서 확인하세요.
Codex connector와 Claude Code MCP 연결은 별도로 설정하며, Figma 작업에는 현재 호스트의
공식 Figma 도구 연결이 필요합니다.

### omp

omp에서는 GitHub 마켓플레이스를 한 번 등록합니다. omp는 `.omp-plugin/marketplace.json`의
11개 플러그인을 읽으며, `memory-manager`는 omp 자체 메모리를 사용하므로 제외합니다.

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in \
  engineering workflow fluent-korean fluent-english fluent-japanese \
  writing research prompting product design-patterns design
do
  omp plugin install "$plugin@sonsu-marketplace"
done
```

스킬은 `/skill:commit`처럼 플러그인 접두어 없이 호출합니다. Claude Code 명령 훅 대신 각 플러그인의
omp extension이 작업 연속성 복구, evidence gate 종료 알림과 세션 ID 전달을 맡습니다. 역할 agent
전체의 모델은 [omp 모델 프로필](plugins/engineering/references/omp-model-profiles.md)의
`task.agentModelOverrides` 블록을 `~/.omp/agent/config.yml`에 추가해 지정합니다.

omp의 계획·위임·검증 흐름을 그대로 쓰고 겹치지 않는 기능만 더하려면 전체 설치 대신 아래 구성을
사용합니다. 계획·실행·TDD·디버깅·일반 리뷰 스킬과 쓰지 않는 역할 agent는 설정으로 거르고,
명시적으로 요청하는 리뷰 관점, PR 심층 리뷰와 Git·문체·디자인 스킬을 남깁니다. 설정은
`~/.omp/agent/config.yml`의 기존 `skills:`·`task:` 항목에 합칩니다.

<!-- omp-preset:start -->
```sh
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese prompting design-patterns design; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
skills:
  ignoredSkills: [execute-plan, plan, brainstorming, worktree, finish-branch, test-driven-development, debug, write-skill, review]
task:
  disabledAgents: [extraction, exploration, localized_implementation, implementation, complex_design, adjudication, complex_adjudication, red_team]
  agentModelOverrides:
    general_review: "@smol"
    focused_review: "@smol"
    senior_review: "@default"
```
<!-- omp-preset:end -->

## 플러그인

| 플러그인 | 용도 | 설치 이름 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | 소프트웨어 변경 설계·구현·검증과 코드 단순화·품질 리뷰 | `engineering` |
| [Workflow](plugins/workflow) | Git branch·commit·push, 티켓 작성·수정·상태 관리와 GitHub PR 작업 | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | 기존 일상·기술 한국어의 AI 티·번역투 윤문 (`im-not-ai` 기반) | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | 일상·기술 영어 작성·윤문·검토 (`better-writing` 기반) | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | 일상·기술 일본어 작성·윤문·문서 진단 (`natural-japanese` 기반) | `fluent-japanese` |
| [Writing](plugins/writing) | 독자·목적에 맞는 정보 선별, 문서 배치와 글의 구성 | `writing` |
| [Research](plugins/research/README.md) | 여러 출처 조사, 사실 검증과 근거를 갖춘 답변 작성 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex·ChatGPT·OpenAI API·Claude Code·Anthropic API용 프롬프트 작성과 개선 | `prompting` |
| [Product](plugins/product/README.md) | 제품 아이디어 탐색, 사용자 근거 정리, 가설 검증과 PRD 작성 | `product` |
| [Memory Manager](plugins/memory-manager/README.md) | Codex·Claude Code가 공유하는 로컬 메모리의 회상·수집·정리 | `memory-manager` |
| [Design](plugins/design/README.md) | 일반·운영 UI의 신규 설계·재설계·감사, 디자인 레퍼런스 검색과 Figma 또는 코드 경로 | `design` |
| [Design Patterns](plugins/design-patterns/README.md) | 실제 설계 forces에 맞는 패턴 선택과 기존 적용 검토 | `design-patterns` |

각 플러그인은 독립적으로 사용할 수 있습니다. 포함된 스킬과 상세 사용법은 위 링크에서 확인하세요.

글을 작성할 때 Writing은 정보 선별·배치와 구성을, 언어별 Fluent는 요청한 출력 언어의 표현을,
Workflow는 티켓·PR 생성의 양식과 게시를, Engineering은 기존 PR의 리뷰 결과 게시를 담당합니다. 함께 쓰는 방법은
[스킬 라우팅 문서](docs/architecture/skill-routing.md)를 참고하세요.

## 사용 예시

관련 플러그인을 설치한 뒤 Codex 또는 Claude Code에 다음과 같이 요청할 수 있습니다.

| 플러그인 | 요청 예시 |
| --- | --- |
| Engineering | “이 버그를 수정해 검증하거나, 현재 diff의 불필요한 추상화와 도달 가능한 실패 경로를 리뷰해 줘.” |
| Workflow | “현재 변경을 커밋하고 Draft PR을 만들어 줘.” |
| Fluent Japanese | “이 일본어 기술 설명을 의미와 코드 식별자를 유지하면서 자연스럽게 다듬어 줘.” |
| Writing | “이 자료에서 README에 필요한 내용을 골라 요약하고, 상세 내용은 기존 문서에 반영해 줘.” |
| Research | “이 두 서비스의 요금과 제한 사항을 공식 자료로 비교해 줘.” |
| Prompting | “이 프롬프트를 Codex에서 바로 쓸 수 있게 개선해 줘.” |
| Product | “이 인터뷰 메모에서 사용자 문제와 근거를 정리해 줘.” |
| Memory Manager | “`$memory-capture` 이 결정을 현재 프로젝트 기억으로 저장해 줘.” |
| Design | “새 모바일 가입 흐름을 Figma에서 만들고, 이 운영 화면을 코드에서 재설계해 줘.” 또는 “로그인 화면 레퍼런스를 출처와 함께 찾아 줘.” |
| Design Patterns | “이 구조에 패턴이 필요한지 판단하고 가장 작은 구현 형태를 골라 줘.” |

호스트는 요청 내용과 설치된 스킬의 설명을 바탕으로 필요한 스킬을 선택합니다.
Memory Manager는 관련 작업에서 `$memory-recall`이 선택될 수 있고, 명시적 저장 요청에는
`$memory-capture`를 사용합니다. 정리와 스킬 초안은 `$memory-maintain`, `$memory-promote`로
명시적으로 요청합니다. Claude Code 호출은 `/memory-manager:memory-capture`처럼 씁니다.

Research의 Exa·Perplexity 연동은 선택 사항이며, 사용 가능한 web·browser·connector와 로컬 자료로도 조사할 수 있습니다.
Design의 Figma 캔버스 작업에는 공식 Figma MCP 연결과 해당 도구의 필수 스킬이 필요합니다.
Design의 레퍼런스 검색은 Mobbin·Refero 같은 MCP가 연결되어 있으면 사용하고, 없으면 호스트 웹 검색을 사용합니다.
설정과 도구 요구사항은 각 플러그인의 문서를 참고하세요.

## 업데이트

Codex에서는 등록된 Git 마켓플레이스의 최신 snapshot을 가져옵니다.

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

업데이트 후 새 Codex 작업을 시작해 최신 스킬 목록을 불러오세요.

Claude Code에서는 다음 명령으로 catalog와 설치한 플러그인을 갱신하고 새 세션을 시작합니다.

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
```

이전 `fluent-languages` 설치본이 있으면 언어 스킬의 적용 범위가 겹치므로 먼저 제거하고 필요한
언어 플러그인을 설치하세요. 새 스킬 ID는 `fluent-korean:fluent-korean`,
`fluent-english:fluent-english`, `fluent-japanese:fluent-japanese`입니다. 영어는 일상·기술 문장의 작성·윤문·검토에, 일본어는 작성·윤문과 문서 진단에 사용할 수 있습니다. 한국어는 기존 글의 AI 티·번역투 윤문에 적용합니다. 기존 작업 연속성 기록은 자동 이전되지 않으며
[수동 복구 절차](docs/reference/task-continuity.md)에 따라 확인합니다.

```sh
codex plugin remove fluent-languages@sonsu-marketplace
codex plugin add fluent-korean@sonsu-marketplace
codex plugin add fluent-english@sonsu-marketplace
codex plugin add fluent-japanese@sonsu-marketplace
```

Claude Code에서는 `claude plugin uninstall fluent-languages@sonsu-marketplace` 후 필요한 언어
플러그인을 `claude plugin install <name>@sonsu-marketplace`로 설치합니다. 다른 마켓플레이스의
동명 스킬이나 standalone `prompt-builder`, `product-discovery`, `to-prd`도 중복되지 않도록 확인하세요.

## 개발 및 기여

로컬 개발 환경, 플러그인 수정·추가와 검증 절차는
[플러그인 개발 가이드](docs/guides/adding-a-plugin.md)에 있습니다.

- [아키텍처 개요](docs/architecture/overview.md) — 저장소 구성과 로딩 경계
- [업스트림 업데이트 런북](docs/runbooks/updating-upstream-plugin.md) — 원본과 로컬 변경을 구분해 갱신하는 절차
- [평가 도구](evals) — 언어 출력, 스킬 라우팅과 플러그인 품질 검증
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — 버그 보고와 개선 제안

## 라이선스와 출처

저장소 전체에 공통으로 적용되는 라이선스는 현재 선언하지 않았습니다. 사용하려는 플러그인의
조건과 원문 고지는 [플러그인별 라이선스와 출처](docs/reference/licenses-and-sources.md)에서 확인하세요.
