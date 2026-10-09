# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

개발, 리서치, 제품 기획과 글쓰기에 사용하는 Codex·Claude Code·omp 플러그인 모음입니다.

## 설치

### Codex

`codex plugin`을 지원하는 CLI에서 한 번 등록하고 필요한 플러그인 하나 또는 전체를 설치합니다. 목록에 설치 상태가 표시되면 새 Codex 작업을 시작하세요.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# 하나만 설치
codex plugin add engineering@sonsu-marketplace
# 전체 설치 시 위 단일 설치 대신 실행
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design career worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

마켓플레이스는 한 번만 등록하고 필요한 플러그인 하나 또는 전체를 설치합니다. 목록에서 설치 상태를 확인한 뒤 새 세션을 시작하세요.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# 하나만 설치
claude plugin install engineering@sonsu-marketplace
# 전체 설치 시 위 단일 설치 대신 실행
for plugin in engineering workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design career worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

기본 6개를 설치하며 Worklog는 선택 사항입니다. 자동 업데이트를 새로 선택할 때만 아래 YAML을 `~/.omp/agent/config.yml`의 기존 `marketplace:` 항목과 합치세요.

<!-- omp-preset:start -->
```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in workflow fluent-korean fluent-english fluent-japanese design career; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
marketplace:
  autoUpdate: auto
```
<!-- omp-preset:end -->

```sh
# 선택 설치
omp plugin install worklog@sonsu-marketplace
omp plugin list
```

## 플러그인

각 플러그인은 독립적으로 사용하며 링크에서 상세 사용법을 확인할 수 있습니다(Codex·Claude Code: 전체 14개, omp: 기본 6개와 opt-in Worklog).

| 플러그인 | 용도 | 설치 이름 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | 소프트웨어 변경 설계·구현·검증과 코드 단순화·품질 리뷰 | `engineering` |
| [Workflow](plugins/workflow) | Git branch·commit·push, 티켓 작성·수정·상태 관리와 GitHub PR 작업 | `workflow` |
| [Fluent Korean](plugins/fluent-korean) | 한국어 새 글의 생성 규칙과 기존 글의 AI 티·번역투 윤문 (`im-not-ai` 기반) | `fluent-korean` |
| [Fluent English](plugins/fluent-english) | 일상·기술 영어 작성·윤문·검토 (`better-writing` 기반) | `fluent-english` |
| [Fluent Japanese](plugins/fluent-japanese) | 일상·기술 일본어 작성·윤문·문서 진단 (`natural-japanese` 기반) | `fluent-japanese` |
| [Writing](plugins/writing) | 독자·목적에 맞는 정보 선별, 문서 배치와 글의 구성 | `writing` |
| [Research](plugins/research/README.md) | 여러 출처 조사, 사실 검증과 근거를 갖춘 답변 작성 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex·ChatGPT·OpenAI API·Claude Code·Anthropic API용 프롬프트 작성과 개선 | `prompting` |
| [Product](plugins/product/README.md) | 제품 아이디어 탐색, 사용자 근거 정리, 가설 검증과 PRD 작성 | `product` |
| [Memory Manager](plugins/memory-manager/README.md) | Codex·Claude Code가 공유하는 로컬 메모리의 회상·수집·정리 | `memory-manager` |
| [Design](plugins/design/README.md) | 일반·운영 UI의 신규 설계·재설계·감사, 디자인 레퍼런스 검색과 Figma 또는 코드 경로 | `design` |
| [Design Patterns](plugins/design-patterns/README.md) | 실제 설계 forces에 맞는 패턴 선택과 기존 적용 검토 | `design-patterns` |
| [Career](plugins/career/README.md) | 개발자 경력 원본 정리, 미국식 resume·履歴書·職務経歴書 작성, 면접 준비·모의면접·회고 | `career` |
| [Worklog](plugins/worklog/README.md) | Claude Code·Codex·omp 작업의 실패·중단·교정 로그와 진단 | `worklog` |

## 사용 예시

관련 플러그인을 설치한 뒤 Codex 또는 Claude Code에 요청하세요(직접 호출 예: Claude Code `/engineering:review`, omp `/skill:commit`).

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
| Career | “이 JD에 맞춰 1페이지 영문 resume를 만들고, 다음 주 1차 면접 기준으로 모의면접을 해 줘.” |

호스트는 요청 내용과 설치된 스킬의 설명을 바탕으로 필요한 스킬을 선택합니다.

## 업데이트

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update engineering@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[이전 omp 구성·fluent-languages에서 이동](docs/guides/migrating-from-earlier-versions.md)

## 문서

- [문서 안내](docs/README.md)
- [스킬 조합과 라우팅](docs/architecture/skill-routing.md)
- [플러그인 배포 생명주기](docs/architecture/plugin-lifecycle.md)
- [플러그인별 라이선스와 출처](docs/reference/licenses-and-sources.md)

## 기여

[플러그인 개발 가이드](docs/guides/adding-a-plugin.md)에서 로컬 환경·수정·검증 절차를 확인하고, 버그와 제안은 [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 남겨 주세요.

## 라이선스

저장소 전체에 공통으로 적용되는 라이선스는 현재 선언하지 않았습니다. 사용하려는 플러그인의 조건과 원문 고지는 [라이선스와 출처](docs/reference/licenses-and-sources.md)에서 확인하세요.
