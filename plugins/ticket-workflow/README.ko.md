# ticket-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

작고 결과 중심적인 GitHub 및 Linear 티켓을 작성하고 구현은 담당자에게 맡긴다.

## 설치

[루트 설치 가이드](../../README.md#install)에 따라 마켓플레이스를 등록한 뒤
사용하는 클라이언트의 명령을 실행한다.

```sh
omp plugin install ticket-workflow@sonsu-marketplace
codex plugin add ticket-workflow@sonsu-marketplace
claude plugin install ticket-workflow@sonsu-marketplace
```

### 의존성

티켓을 게시하려면 선택한 GitHub 저장소 또는 Linear 워크스페이스에 인증된 도구가
필요하다. `ticket-workflow`는 인증 정보를 포함하거나 트래커 연동을 설정하지 않는다.

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details ticket-workflow
```

지원되는 클라이언트에서 작업을 자연어로 요청한다.

```text
Draft a GitHub issue from these bug notes without publishing it.

Split this oversized Linear ticket into smaller drafts without publishing them.
```

자연어 요청은 대개 일치하는 스킬을 선택하지만, 선택은 모델의 판단이며 보장된
훅이 아니다. 스킬을 명시적으로 선택하려면 Codex에서는
`$ticket-workflow:writing-tickets`, Claude Code에서는
`/ticket-workflow:writing-tickets`를 사용한다. 플러그인이 목록에 표시된다고 해서
그 스킬이 실행된다는 뜻은 아니다.

### 스킬

- **`writing-tickets`**는 간결하고 결과 중심적인 GitHub 및 Linear 티켓을 작성한다.
  프로젝트 템플릿을 우선 따르며, 템플릿이 없으면 명확한 제목이나 한두 문장만으로
  티켓을 작성할 수 있다. 본문에는 필수 제약 조건을 유지하면서 누적된 조사 내용이나
  진행 로그가 아닌 현재 합의 내용을 담는다. 또한 레이블, 담당자, 우선순위, 추정치,
  마일스톤을 검토하고 트래커의 실제 필드와 관례에 따라 근거 있는 메타데이터를
  본문과 별도로 제안한다. 알 수 없는 선택 항목은 추측하지 않고 비워 둔다. 버그
  보고서와 상위 티켓에는 종류별 지침을 추가하며, 취약점이 의심되면 공개 티켓 대신
  프로젝트의 비공개 보고 경로를 따른다.
  [티켓 작성 절차](skills/writing-tickets/SKILL.md)와
  [대체 템플릿](skills/writing-tickets/assets/ticket-body.md)을 참고한다.

`writing-tickets`를 사용하려면 GitHub Issues 또는 Linear 티켓의 초안 작성, 생성,
수정 또는 분할을 요청한다. 초안 작성 요청은 이슈를 게시하지 않는다.

일반적인 개발 흐름은 티켓, 작업, PR 순서로 진행한다. 티켓과 PR이 반드시 일대일로
대응할 필요는 없으며, 일부 작업만으로 전체 티켓을 닫아서는 안 된다. 이후 브랜치
이름 지정과 PR 준비를 위해 `git-workflow`를 설치한다. 티켓 초안을 작성하는 데는
필요하지 않다. 티켓 플러그인은 기존 트래커 동기화와 템플릿을 따르지만 이를
설정하거나 양쪽 트래커에 중복 이슈를 게시하거나 훅으로 티켓 우선 작업을 강제하지
않는다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 올린다.
[플러그인](../../CONTRIBUTING.md#adding-a-plugin)과
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차를 포함한 저장소의
[기여자 가이드](../../CONTRIBUTING.md)를 따른다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee
