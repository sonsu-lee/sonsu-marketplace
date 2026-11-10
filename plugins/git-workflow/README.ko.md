# git-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

저장소 관례에 따라 브랜치 이름을 짓고, 커밋을 작성하고, 초안 풀 리퀘스트를
준비한다.

## 설치

[루트 설치 안내](../../README.md#install)에 따라 마켓플레이스를 등록한 다음,
사용하는 클라이언트의 명령을 실행한다.

```sh
omp plugin install git-workflow@sonsu-marketplace
codex plugin add git-workflow@sonsu-marketplace
claude plugin install git-workflow@sonsu-marketplace
```

### 의존성

`git-workflow` 스킬은 대상 저장소의 검증 설정을 우선 재사용한다. 설정이 없으면
커밋 대체 실행에는 Node.js 22.12.0 이상과 npm(`npx`)이 필요하고, 브랜치 대체
실행에는 uv(`uvx`)와 Python 3.10 이상이 필요하다. 캐시되지 않은 대체 실행을
처음 수행할 때는 해당 패키지 레지스트리에 접근할 수 있어야 한다.

풀 리퀘스트를 게시하려면 인증된 GitHub 도구가 필요하다. 네이티브 미디어 업로드는
GitHub CLI의 `--attach` 지원을 사용하며 대상 저장소에 대한 푸시 권한이 필요하다.
UI 증거를 캡처하려면 적절한 캡처 및 주석 도구가 필요하다.

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details git-workflow
```

지원되는 클라이언트에서 작업을 자연스럽게 요청한다.

```text
Suggest a branch name for GitHub issue #45, which fixes a header overflow.

Write a commit message for the staged changes.

Draft a pull request title and body for this branch without publishing it.
```

자연어 요청은 대개 일치하는 스킬을 선택하지만, 선택은 모델의 판단이며 보장된
훅이 아니다. 스킬을 명시적으로 선택하려면 Codex에서는
`$git-workflow:writing-commits`를, Claude Code에서는
`/git-workflow:writing-commits`를 사용한다. 플러그인이 목록에 표시된다고 해서
해당 스킬이 실행된다는 뜻은 아니다.

### 스킬

- **`writing-commits`**는 Conventional Commit 메시지를 작성하고 사용 전에
  검증한다. 저장소의 명령, 도구, 버전, 설정을 재사용한다. 기존 실행 설정이
  없을 때만 `npx`로 버전이 고정된 commitlint를 실행하고, 설정이 없을 때만
  번들 ESM 기본값을 사용한다.
  [스킬의 검증 절차](skills/writing-commits/SKILL.md#required-validation)를
  참고한다.
- **`naming-branches`**는 Conventional Branch 1.1.0에 따라 브랜치 이름을 짓고
  검증하며, 저장소의 검증을 우선 재사용한다. 실행 설정이 없으면 `uvx`로 버전이
  고정된 `commit-check`를 실행하며, 저장소 설정은 여전히 번들 기본값보다
  우선한다. 이는 npm 패키지가 아닌 Python CLI다. 스킬의 기본 접두사는
  `feat/`(`feature/`가 아님), `bugfix/`(`fix/`가 아님), `hotfix/`, `release/`,
  `chore/`다.
  [스킬의 검증 절차](skills/naming-branches/SKILL.md#required-validation)를
  참고한다.
- **`writing-pull-requests`**는 변경 사항을 간결하게 요약하는 Summary로 PR
  설명을 시작하고, 필요에 따라 내용에 맞는 섹션, 핵심 코드 설명, 다이어그램,
  UI 증거를 추가한다. 티켓 내용을 반복하는 대신 링크한다. 의존 관계가 있는 PR은
  가능한 경우 GitHub 스택을 사용하며, 새 PR은 기본적으로 Draft다.
  [PR 작성 절차](skills/writing-pull-requests/SKILL.md)를 참고한다.

`writing-pull-requests`를 사용하려면 풀 리퀘스트의 초안 작성, 생성 또는 수정을
요청한다. 새 PR은 기본적으로 Draft다.

브랜치 접두사는 커밋 유형을 바꾸지 않는다. `bugfix/` 브랜치에도 `fix`, `test`
등의 커밋을 포함할 수 있다. 의존성이 없거나 설정된 검증기가 실패하는 것은 설정
자체가 없는 경우가 아니므로 대체 실행을 시작해서는 안 된다. 이 스킬은 Git 훅이나
CI 강제가 아니라 에이전트 워크플로 지침을 제공한다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 남긴다.
[플러그인](../../CONTRIBUTING.md#adding-a-plugin) 및
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차를 포함한 저장소의
[기여자 안내](../../CONTRIBUTING.md)를 따른다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee
