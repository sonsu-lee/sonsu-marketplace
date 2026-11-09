# sonsu-marketplace

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

omp, Codex, Claude Code용 개인 플러그인 마켓플레이스.

[omp](https://github.com/can1357/oh-my-pi)는 `.omp-plugin/marketplace.json`을,
[Codex](https://developers.openai.com/codex/cli)는
`.agents/plugins/marketplace.json`을,
[Claude Code](https://code.claude.com/docs/en/overview)는
`.claude-plugin/marketplace.json`을 읽는다. 세 클라이언트 모두 같은 `plugins/`
패키지를 설치한다.

## 목차

- [설치](#설치)
  - [의존성](#의존성)
  - [마켓플레이스](#마켓플레이스)
- [사용법](#사용법)
  - [CLI](#cli)
- [사용 가능한 플러그인](#사용-가능한-플러그인)
- [기여](#기여)
- [라이선스](#라이선스)

## 설치

### 의존성

이 마켓플레이스를 쓰기 전에 [omp](https://github.com/can1357/oh-my-pi#install),
[Codex CLI](https://developers.openai.com/codex/cli),
[Claude Code](https://code.claude.com/docs/en/overview) 중 하나를 설치한다.
Codex와 Claude Code는 플러그인 마켓플레이스와 일부 플러그인이 쓰는 서브에이전트
인터페이스를 제공해야 하며, 이를 지원하지 않는 이전 클라이언트는 전제 조건을
충족하지 않는다. 로컬 카탈로그 설치와 설치된 skill 탐색은 `checks` 워크플로가
설치하는 버전인 Codex CLI `0.163.0`, omp `18.12.6`, Claude Code `2.1.304`에서
확인했다. 이 버전은 확인한 기준선일 뿐, 모든 이전 릴리스를 보장하거나 인증된
모델 실행을 입증하지 않는다.

일부 플러그인은 추가 도구나 인증된 서비스가 필요하다.
[사용 가능한 플러그인](#사용-가능한-플러그인)에서 각 플러그인 안내서의
`Dependencies` 절을 참고한다.

### 마켓플레이스

omp에서는 마켓플레이스를 추가한다:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

플러그인 목록을 보고 하나를 설치한다:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

현재 프로젝트에만 설치하려면 `--scope project`를 붙인다.

Codex에서는 다음과 같다:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace --available --json
codex plugin add git-workflow@sonsu-marketplace
```

Claude Code에서는 다음과 같다:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install git-workflow@sonsu-marketplace
```

다른 패키지는 `codex plugin add <name>@sonsu-marketplace` 또는
`claude plugin install <name>@sonsu-marketplace`로 설치한다. Claude Code도
`--scope project`를 지원한다. 이 저장소는 저장소 기반 마켓플레이스이며 공개
플러그인 디렉터리에 제출한 것이 아니다. 공통 로컬 마켓플레이스 형식은 이를
지원하는 앱과 IDE 화면에도 적용되지만, 지원 여부는 화면마다 다르며 CLI 검사는
그 UI를 검증하지 않는다.

## 사용법

### CLI

omp에서는 설치 후 사용 가능한 skill을 확인한다:

```sh
omp skill list
```

Codex에서는 카탈로그와 설치 상태를 확인한다:

```sh
codex plugin list --marketplace sonsu-marketplace --json
```

Claude Code에서는 설치 상태와 패키지 구성 요소를 확인한다:

```sh
claude plugin list
claude plugin details git-workflow
```

목록에 나타난다는 것은 카탈로그나 설치 상태를 보여 줄 뿐, skill 실행을
입증하지 않는다. Codex 세션에서는 설치된 플러그인 skill을
`$<plugin>:<skill>` 형식으로 명시해 선택한다. 예를 들면
`$git-workflow:writing-commits`이다. 확인한 CLI 기준선에서 `$writing-commits`만
쓰면 해당 플러그인 skill이 선택되지 않는다. Claude Code에서는
`/<plugin>:<skill>` 형식, 예를 들어 `/git-workflow:writing-commits`로 호출한다.
skill을 호출하거나 결과를 대조할 때는 탐색 결과가 돌려준 정규화된 이름을 그대로
쓴다. 자연어로 선택되는지는 모델의 동작이며, 설치 훅이나 보장된 트리거가 아니다.

omp 세션에서 `/marketplace`를 입력하면 플러그인 브라우저에서 카탈로그가 열린다.
설치된 skill은 관련 요청에 대한 지침을 제공한다. 예를 들어 `git-workflow`를 쓸
때 omp에 branch 이름을 정하거나 commit 메시지를 써 달라고 요청한다.
[사용 가능한 플러그인](#사용-가능한-플러그인)의 각 플러그인 안내서에 skill별
요청 예시가 있다.

omp에서는 카탈로그 변경을 가져온 뒤 설치된 플러그인을 업그레이드한다:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

Codex에서는 Git 기반 마켓플레이스를 갱신한다:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

절대 경로로 등록한 로컬 마켓플레이스는 그 경로를 직접 사용하므로
`marketplace upgrade`로 갱신할 수 없다. 이 명령은 Git 소스가 설정되어 있어야
한다.

Claude Code에서는 카탈로그를 갱신한 뒤 설치된 플러그인을 업데이트한다:

```sh
claude plugin marketplace update sonsu-marketplace
claude plugin update git-workflow@sonsu-marketplace
```

Claude Code는 로컬 경로 마켓플레이스의 플러그인을 그 자리에서 불러오므로, 소스
수정은 버전을 바꾸지 않아도 다음 세션부터 적용된다.

## 사용 가능한 플러그인

- [git-workflow][git-workflow]: 저장소 규칙에 따라 branch 이름을 정하고 commit을
  쓰고 draft pull request를 준비한다.
- [skill-workflow][skill-workflow]: 초점이 분명한 에이전트 skill을 만들고 다듬고
  평가하고 독립적으로 리뷰하며, 기계적인 작업은 기존 도구에 맡긴다.
- [ticket-workflow][ticket-workflow]: 작고 결과 중심적인 GitHub·Linear 티켓을
  쓰고, 구현 방법은 담당자에게 맡긴다.
- [decision-workflow][decision-workflow]: 중요한 설계 결정을 골라 저장소 규칙을
  우선하는 가벼운 ADR을 쓴다.
- [writing-workflow][writing-workflow]: 의미와 글쓴이의 목소리를 지키면서 자연스러운
  한국어·영어·일본어 글을 쓰고 다듬는다.
- [review-workflow][review-workflow]: 근거 중심의 코드 리뷰를 독립적인 일반·집중
  리뷰어와 함께 수행하고 결과는 로컬에 먼저 보고한다.
- [planning-workflow][planning-workflow]: 단순하지 않은 작업을 계획하고, 승인된
  실행을 독립 리뷰와 최종 검증까지 조율한다.
- [design-workflow][design-workflow]: 범위가 정해진 근거와 선택적인 omp 검증
  하네스로 인터페이스와 그래픽을 설계하고 리뷰한다.

## 기여

Pull request를 환영한다. 질문이나 문제 보고는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 남긴다.
플러그인, skill, 문서, 워크플로를 바꾸기 전에
[기여 안내서](CONTRIBUTING.md)를 읽는다.

## 라이선스

[MIT](LICENSE) © sonsu-lee. 단,
`plugins/skill-workflow/skills/evaluating-skills/`는
[Apache License 2.0](plugins/skill-workflow/skills/evaluating-skills/LICENSE.txt)을
따르며 Anthropic의
[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
자료를 포함한다.

[git-workflow]: plugins/git-workflow/README.md
[skill-workflow]: plugins/skill-workflow/README.md
[ticket-workflow]: plugins/ticket-workflow/README.md
[decision-workflow]: plugins/decision-workflow/README.md
[writing-workflow]: plugins/writing-workflow/README.md
[review-workflow]: plugins/review-workflow/README.md
[planning-workflow]: plugins/planning-workflow/README.md
[design-workflow]: plugins/design-workflow/README.md
