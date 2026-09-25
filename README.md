# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

개발, 리서치, 제품 기획과 글쓰기에 사용하는 Codex·Claude Code 플러그인 모음입니다.
필요한 플러그인만 골라 설치하고, 사용하는 코딩 에이전트에 평소처럼 작업을 요청하세요.

[설치](#설치) · [플러그인](#플러그인) · [사용 예시](#사용-예시) · [문서](docs/README.md)

## 설치

### Codex

`codex plugin` 명령을 지원하는 Codex CLI에서 마켓플레이스를 등록합니다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

필요한 플러그인을 설치합니다. 예를 들어 개발 작업에는 Engineering을 사용할 수 있습니다.

```sh
codex plugin add engineering@sonsu-marketplace
```

다른 플러그인은 아래 표의 설치 이름으로 바꿔 설치하세요. Workflow의 설치 예시는 다음과 같습니다.

```sh
codex plugin add workflow@sonsu-marketplace
```

설치 후에는 새 Codex 작업을 시작하세요. 등록된 플러그인 목록은 다음 명령으로 확인할 수 있습니다.

```sh
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

Claude Code CLI에서는 마켓플레이스를 등록한 다음 필요한 플러그인을 설치합니다.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
claude plugin list
```

현재 체크아웃을 시험할 때에는 첫 명령에 저장소의 **절대 경로**를 전달합니다.
스킬은 `/engineering:review`처럼 호출합니다. 설치·업데이트 후 새 세션에서 확인하세요.
Codex connector와 Claude Code MCP 연결은 별도로 설정하며, Figma 작업에는 현재 호스트의
공식 Figma 도구 연결이 필요합니다.

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
| [Figma Workflow](plugins/figma-workflow/README.md) | Figma 제품 화면, 클릭 가능한 프로토타입과 디자인 품질 검토 | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 명시적으로 호출하는 코딩 에이전트 메모리 점검과 정리 | `memory-manager` |
| [Interface Design](plugins/interface-design/README.md) | 일반 웹·앱 화면의 설계·재설계와 정보 자산 검증 | `interface-design` |
| [Operations UI](plugins/operations-ui/README.md) | 상태·데이터 중심 운영형 B2B 화면의 설계, 재설계와 품질 감사 | `operations-ui` |
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
| Figma Workflow | “이 Figma 화면의 Auto Layout과 프로토타입 연결을 검토해 줘.” |
| Memory Manager | “`$memory-manager` 현재 프로젝트의 Codex 메모리를 점검해 줘.” |
| Interface Design | “새 모바일 가입 흐름을 디자인해 줘. 이 차트의 정보 표현도 개선해 줘.” |
| Operations UI | “이 주문 운영 화면을 Design Decision Contract부터 구현하고 DQ 게이트와 브라우저 증거로 검증해 줘.” |
| Design Patterns | “이 구조에 패턴이 필요한지 판단하고 가장 작은 구현 형태를 골라 줘.” |

호스트는 요청 내용과 설치된 스킬의 설명을 바탕으로 필요한 스킬을 선택합니다.
Memory Manager는 Codex의 `$memory-manager`, Claude Code의 `/memory-manager:memory-manager`로
명시적으로 호출할 때만 작동합니다.

Research의 Exa·Perplexity 연동은 선택 사항이며, 사용 가능한 web·browser·connector와 로컬 자료로도 조사할 수 있습니다.
Figma Workflow의 캔버스 작업에는 공식 Figma MCP 연결과 해당 도구의 필수 스킬이 필요합니다.
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
