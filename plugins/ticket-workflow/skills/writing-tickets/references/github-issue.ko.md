# GitHub Issues

> 영문 정본: [github-issue.md](github-issue.md) (`4f07d42` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

[티켓 작성](../SKILL.md)의 절차와 함께 아래 GitHub 차이를 적용한다.

## 템플릿과 안내 경로

- 대상 저장소의 기본 브랜치에서 기여 지침과 이슈 템플릿을 읽는다. 이슈 폼,
  `config.yml`, 지원되는 위치의 레거시 템플릿도 확인한다. 저장소에 템플릿과
  설정이 없으면 소유자의 공개 `.github` 저장소에서 상속되는 기본값을 확인한다.
- API나 CLI로 만들 때는 폼 답변을 읽기 좋은 섹션으로 구성하고 속성을 따로
  적용한다. 필수 체크박스는 알려진 사실을 반영해야 하며 재현, 검색, 합의를
  추측해서 표시하지 않는다.
- `config.yml`의 연락처 링크가 요청을 Discussions나 비공개 취약점 제보 등
  다른 곳으로 안내하면 이슈를 만들지 말고 목적지를 알린다. 토론은 요청받았을
  때만 만든다. 보안 정책에 취약점 의심 제보 채널이 없으면 이슈 대신 활성화된
  비공개 취약점 제보를 이용한다.

## 필드와 관계

- GitHub에는 저장소 레이블, 지정 가능한 담당자, 마일스톤, 이슈 유형이 있다.
  우선순위와 추정치는 조직 이슈 필드, Projects 사용자 정의 필드 또는 확립된
  레이블로 표현될 수 있으므로 실제 구성을 확인한다. 관례가 없으면 임의의 본문
  값이나 우선순위 레이블을 만들지 말고 필드가 구성되지 않았다고 보고한다.
- 프로젝트 필드는 대상 프로젝트, 필드 정의·옵션, 이슈의 프로젝트 항목을
  파악한다. 프로젝트에 표시되는 조직 필드와 이름이 같은 프로젝트 로컬 필드를
  구분한다. 조직 필드, 프로젝트 소속, 프로젝트 로컬 필드에는 별도로 지원되는
  작업이 필요할 수 있다.
- 상위·하위 관계에는 하위 이슈를 쓴다. 이슈 유형은 작업을 분류할 뿐 계층을
  만들지 않는다. GitHub 마일스톤은 저장소에 속하며 Linear 프로젝트 마일스톤이나
  GitHub Projects 이터레이션이 아니다.

## 증거와 PR 참조

- 공개 저장소에서 사용자가 푸시 권한을 가진 경우에만 GitHub CLI로 로컬 이미지와
  동영상을 첨부한다. 그렇지 않으면 증거를 링크하거나 업로드를 사용자에게 맡긴다.
  보고하기 전에 어떤 첨부가 렌더링되었는지 확인한다.
- 다른 저장소를 참조할 때는 `owner/repository#123`이나 전체 URL을 쓴다.

## 주의사항

- 로컬 이슈 템플릿이나 선택기 설정이 있으면 맞는 로컬 템플릿이 없어도 상속된
  `.github/ISSUE_TEMPLATE` 디렉터리는 적용되지 않는다. 작업 브랜치에 GitHub가
  현재 제공하는 템플릿이 없을 수 있다.
- 폼 YAML은 생성 스키마이지 이슈 설명이 아니다. 조직 이슈 필드는 현재 이슈
  템플릿으로 채울 수 없다.
- 보편적인 우선순위·추정치 필드나 Linear식 매핑을 가정하지 않는다. 이슈를
  만들었다고 Projects 필드도 설정되는 것은 아니다.
- 공개 저장소의 이슈는 누구나 볼 수 있고 첨부 파일도 인증 없이 접근할 수
  있다. 일부 첨부만 업로드되어도 이슈는 생성된다.
- `#123`은 해당 저장소 안에서만 유효하다. PR 설명의 GitHub 닫기 키워드는
  PR이 기본 브랜치를 대상으로 할 때 적용되며 머지하면 참조 이슈가 닫힌다.
  기본 브랜치가 아닌 곳으로 머지해도 닫힌다고 가정하지 않는다.

## 출처

- [Configuring issue templates][templates]
- [Default community health files][defaults]
- [Linking pull requests to issues][linking]
- [Setting organization issue field values][issue-fields]
- [Projects priority and estimate fields][project-fields]
- [Adding sub-issues][sub-issues]
- [Privately reporting a security vulnerability][private-reporting]
- [Attaching files][attaching]
- [Attaching files with GitHub CLI][attaching-cli]

[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[linking]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
[issue-fields]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-and-managing-issue-fields
[project-fields]: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects
[sub-issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
[private-reporting]: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
[attaching]: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files
[attaching-cli]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
