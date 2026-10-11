# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

개발, 리서치, 제품 기획과 글쓰기에 쓰는 Codex·Claude Code·omp 플러그인 모음입니다.

호스트마다 제공하는 플러그인이 다릅니다. Codex와 Claude Code에는 15개 전체를, omp에는 기본 7개와 선택 6개를 제공합니다. omp는 개발 실행과 메모리를 자체 기능으로 처리하므로 Dev Workflow와 Memory Manager는 omp에 배포하지 않습니다.

## 설치

마켓플레이스를 한 번 등록하고 필요한 플러그인을 설치합니다. 목록에서 설치 상태를 확인한 뒤 새 세션을 시작하세요. 호스트별로 설치할 수 있는 플러그인은 [플러그인](#플러그인) 표에 있습니다.

### Codex

`codex plugin`을 지원하는 CLI가 필요합니다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
# 하나만 설치
codex plugin add dev-workflow@sonsu-marketplace
# 전체 설치 시 위 단일 설치 대신 실행
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do codex plugin add "$plugin@sonsu-marketplace"; done
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

### Claude Code

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
# 하나만 설치
claude plugin install dev-workflow@sonsu-marketplace
# 전체 설치 시 위 단일 설치 대신 실행
for plugin in git tickets review dev-workflow fluent-korean fluent-english fluent-japanese writing research prompting product memory-manager design-patterns design worklog; do claude plugin install "$plugin@sonsu-marketplace"; done
claude plugin marketplace list
claude plugin list
```

### omp

기본 7개를 설치하고 선택 6개는 필요할 때 따로 설치합니다. 자동 업데이트를 새로 켤 때만 아래 YAML을 `~/.omp/agent/config.yml`의 기존 `marketplace:` 항목과 합치세요.

<!-- omp-preset:start -->
```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
for plugin in git tickets review fluent-korean fluent-english fluent-japanese design; do omp plugin install "$plugin@sonsu-marketplace"; done
```

```yaml
marketplace:
  autoUpdate: auto
```
<!-- omp-preset:end -->

```sh
# 선택 설치
omp plugin install writing@sonsu-marketplace
omp plugin install research@sonsu-marketplace
omp plugin install prompting@sonsu-marketplace
omp plugin install product@sonsu-marketplace
omp plugin install worklog@sonsu-marketplace
omp plugin install design-patterns@sonsu-marketplace
omp plugin list
```

## 사용

설치한 뒤 자연어로 요청하면 호스트가 요청 내용과 스킬 설명을 보고 맞는 스킬을 고릅니다.

요청: “현재 branch의 PR 초안만 준비해 줘. 게시는 하지 마.”

Git 플러그인의 `write-pr`가 원격에 쓰지 않고 PR 제목·본문 초안과 미확인 항목을 보고합니다.

스킬을 이름으로 직접 부를 때는 호스트마다 형식이 다릅니다.

| 호스트 | 형식 | 예 |
| --- | --- | --- |
| Codex | `$<스킬>` | `$write-pr` |
| Claude Code | `/<플러그인>:<스킬>` | `/git:write-pr` |
| omp | `/skill:<스킬>` | `/skill:write-pr` |

플러그인별 요청 예시는 각 플러그인 README에 있습니다.

## 플러그인

링크 이름이 설치 이름입니다. omp 열의 `기본`은 기본 설치 명령에 포함된 플러그인, `선택`은 따로 설치하는 플러그인입니다.

| 플러그인 | 용도 | Codex | Claude Code | omp |
| --- | --- | :---: | :---: | :---: |
| [`git`](plugins/git/README.md) | Git branch·commit·push와 GitHub PR 작성·상태 조회·복구 | ✓ | ✓ | 기본 |
| [`tickets`](plugins/tickets/README.md) | GitHub Issues·Linear 티켓 작성과 상태·담당자·관계 변경 | ✓ | ✓ | 기본 |
| [`review`](plugins/review/README.md) | 코드·diff·커밋·PR의 코드 건강도 리뷰, 집중 관점 리뷰와 리뷰 지적 대응 | ✓ | ✓ | 기본 |
| [`dev-workflow`](plugins/dev-workflow/README.md) | 소프트웨어 변경 설계·계획·구현·디버깅·검증과 코드 단순화 | ✓ | ✓ | — |
| [`fluent-korean`](plugins/fluent-korean/README.md) | 한국어 새 글의 생성 규칙과 기존 글의 AI 티·번역투 윤문 (`im-not-ai` 기반) | ✓ | ✓ | 기본 |
| [`fluent-english`](plugins/fluent-english/README.md) | 일상·기술 영어 작성·윤문·검토 (`better-writing` 기반) | ✓ | ✓ | 기본 |
| [`fluent-japanese`](plugins/fluent-japanese/README.md) | 일상·기술 일본어 작성·윤문·문서 진단 (`natural-japanese` 기반) | ✓ | ✓ | 기본 |
| [`writing`](plugins/writing/README.md) | 독자·목적에 맞는 정보 선별, 문서 배치와 글의 구성 | ✓ | ✓ | 선택 |
| [`research`](plugins/research/README.md) | 여러 출처 조사, 사실 검증과 근거를 갖춘 답변 작성 | ✓ | ✓ | 선택 |
| [`prompting`](plugins/prompting/README.md) | Codex·ChatGPT·OpenAI API·Claude Code·Anthropic API용 프롬프트 작성과 개선 | ✓ | ✓ | 선택 |
| [`product`](plugins/product/README.md) | 제품 아이디어 탐색, 사용자 근거 정리, 가설 검증과 PRD 작성 | ✓ | ✓ | 선택 |
| [`memory-manager`](plugins/memory-manager/README.md) | Codex·Claude Code가 공유하는 로컬 메모리의 회상·수집·정리 | ✓ | ✓ | — |
| [`design`](plugins/design/README.md) | 일반·운영 UI의 신규 설계·재설계·감사, 디자인 레퍼런스 검색과 Figma 또는 코드 경로 | ✓ | ✓ | 기본 |
| [`design-patterns`](plugins/design-patterns/README.md) | 실제 설계 forces에 맞는 패턴 선택과 기존 적용 검토 | ✓ | ✓ | 선택 |
| [`worklog`](plugins/worklog/README.md) | Claude Code·Codex·omp 작업의 실패·중단·교정 로그와 진단 | ✓ | ✓ | 선택 |

호스트에 따라 동작이 다른 플러그인은 다음과 같습니다.

- **Fluent Korean**: Claude Code는 light·standard·heavy 다단계 경로로, Codex와 omp는 단일 호출로 윤문합니다.
- **Review**: omp에서는 순정 `/review`에도 이 플러그인의 리뷰 기준이 적용됩니다.
- **Memory Manager**: Codex와 Claude Code가 같은 기기의 기억을 공유합니다. omp는 자체 메모리 기능을 씁니다.
- **Worklog**: Claude Code·Codex는 hook으로, omp는 runtime extension으로 기록합니다. Codex에서는 설치·업데이트 뒤 `/hooks`에서 worklog hook을 신뢰해야 기록이 시작됩니다.

## 업데이트

```sh
codex plugin marketplace upgrade sonsu-marketplace
claude plugin marketplace update sonsu-marketplace
claude plugin update dev-workflow@sonsu-marketplace
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

[이전 omp 구성·fluent-languages·workflow·engineering에서 이동](docs/guides/migrating-from-earlier-versions.md)

## 문서

- [문서 안내](docs/README.md)
- [스킬 조합과 라우팅](docs/architecture/skill-routing.md)
- [플러그인 배포 생명주기](docs/architecture/plugin-lifecycle.md)
- [플러그인별 라이선스와 출처](docs/reference/licenses-and-sources.md)

## 기여

[플러그인 개발 가이드](docs/guides/adding-a-plugin.md)에서 로컬 환경·수정·검증 절차를 확인하고, 버그와 제안은 [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 남겨 주세요.

## 라이선스

저장소 전체에 공통으로 적용되는 라이선스는 현재 선언하지 않았습니다. 사용하려는 플러그인의 조건과 원문 고지는 [라이선스와 출처](docs/reference/licenses-and-sources.md)에서 확인하세요.
