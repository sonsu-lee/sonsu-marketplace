# 브랜치 이름 짓기

> 영문 정본: [SKILL.md](SKILL.md) (`f1bd632` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

저장소의 브랜치 이름 규칙을 확인하고 따른다. 여기에는
[commit-check](https://github.com/commit-check/commit-check) 같은 브랜치 이름
검증기 설정도 포함한다. 저장소에 규칙이 없는 부분에는 아래 기본값을 사용한다.

## 이름 규칙

작업의 목적에 맞게 브랜치 이름을 짓는다.
[Conventional Branch 1.1.0](https://conventionalbranch.org/v1.1.0/spec.json)을
사용한다.

```text
<type>/<description>
```

| Type | 사용처 |
| --- | --- |
| `feat` | 새 기능 또는 개선 |
| `bugfix` | 버그 수정 |
| `hotfix` | 긴급 프로덕션 수정 |
| `release` | 릴리스 준비 |
| `chore` | 유지보수: 의존성, 문서, CI, 리팩터링 |

* **Type:** `feature`가 아니라 `feat`, `fix`가 아니라 `bugfix`를 쓴다. 개별
  커밋의 type이 아니라 브랜치 전체의 목적을 기준으로 고른다. 커밋 메시지는
  `fix`를 포함한 자체 규칙을 그대로 유지한다.
* **Description:** 간결하고 구체적으로 쓴다. 소문자 ASCII 문자, 숫자, 단어 사이의
  하이픈을 사용한다. 영숫자 구간 사이에는 점도 허용하며, 릴리스 버전이 아닌
  곳도 마찬가지다. 문자 또는 숫자로 시작하고 끝나며, 하이픈이나 점을 서로
  인접시키지 않는다. 공백, 밑줄, 추가 슬래시는 사용하지 않는다.
* **Issue ID:** 제공되었거나 확인된 경우 소문자로 맨 앞에 둔다. `ENG-123`은
  `eng-123`, GitHub 이슈 #45는 `issue-45`로 쓴다. 지어내지 않는다.
* **Trunk 브랜치:** `main`, `master`, `develop`은 접두사를 붙이지 않는다.
* **에이전트 접두사:** 사용자나 저장소가 명시적으로 요청한 경우에만 사용하며,
  에이전트가 작업한다는 이유만으로 붙이지 않는다.

## 필수 검증

브랜치를 만들거나 이름을 바꾸기 전, 또는 이름을 완성본으로 제시하기 전에 제안하는
이름을 검증한다. [검증 절차](references/validation.md)를 따른다.

1. Git ref 문법을 확인하고 저장소의 이름 규칙을 먼저 적용한다.
2. 저장소에 이미 있는 검증 명령, 도구, 버전을 사용한다. 의존성이 없으면
   문서화된 설치 방법을 따르며, 실패하거나 사용할 수 없는 설정된 검증기를
   우회하지 않는다.
3. 실행 환경이 정해져 있지 않은 경우에만 버전을 고정한 `commit-check`를
   `uvx`로 사용한다. 이것은 Conventional Branch가 링크하는 Python CLI이며
   npm 패키지가 아니다. 저장소 설정이 있으면 유지하고, 없으면
   [번들 기본값](assets/commit-check.toml)을 사용한다.

결과가 현재 브랜치나 건너뛴 규칙이 아니라 제안한 이름을 검사했는지 확인한다.
저장소의 통과 기준을 따른다. 이름을 검증하려고 브랜치를 만들거나 hook 또는 CI
job을 설치하지 않는다. 검사하지 않은 이름이 통과했다고 주장하지 말고 막힌 점을
보고한다.

목적, 티켓 ID, 접두사 선택은 별도로 검토한다. CLI는 특수한 CI ref 이름도
허용한다. 저장소가 명시적인 예외를 두지 않는 한, 접두사 없는 브랜치 이름은
`main`, `master`, `develop`뿐이다.

## 예시

```text
feat/eng-123-add-login-page
bugfix/issue-45-header-overflow
hotfix/payment-outage
release/v1.2.0
chore/upgrade-node-v20.11
```
