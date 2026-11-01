# GitHub Issues

> 영문 정본: [github-issue.md](github-issue.md) (`092f9e2` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

## 해당 템플릿 선택하기

대상 저장소의 기여 지침과 이슈 템플릿을 기본 브랜치에서 읽는다.
`.github/ISSUE_TEMPLATE/`을 확인하되 이슈 폼, `config.yml`, 지원되는 위치의
레거시 이슈 템플릿도 포함한다. 로컬 이슈 템플릿이나 선택기 설정이 있으면
상속받는 `.github/ISSUE_TEMPLATE` 디렉터리는 적용되지 않는다. 요청과 맞는
로컬 템플릿이 없다는 이유만으로 소유자의 기본값을 끌어와 합치지 않는다.
저장소에 템플릿과 설정이 없을 때는 소유자의 공개 `.github` 저장소에서
상속되는 기본값이 있는지 확인한다. 작업 브랜치에 GitHub가 현재 제공하는
템플릿이 있다고 가정하지 않는다.

첫 번째 파일이 아니라 요청에 맞는 템플릿을 고른다. 필수 폼 필드, 레이블,
그 밖에 의무인 메타데이터는 보존한다. 폼의 YAML은 생성 스키마이지 이슈
설명이 아니다. API나 CLI를 쓸 때는 답변을 읽기 좋은 섹션으로 구성하고
관련 속성은 따로 적용한다. 필수 체크박스는 알려진 사실을 반영해야 한다.
템플릿이 요구한다는 이유만으로 재현, 검색, 합의를 했다고 주장하지 않는다.

목적을 읽어 봐도 여러 템플릿이 여전히 실질적으로 다르다면 의도한 이슈
유형을 확인한다. 번들된 대체 템플릿은 맞는 것이 하나도 없을 때만 쓴다.

`config.yml`의 연락처 링크는 질문, 지원, 아이디어, 보안 제보를 이슈가 아닌
곳, 예를 들어 Discussions나 비공개 취약점 제보로 보낼 수 있다. 요청이 그런
경로에 속하면 이슈를 만들지 말고 안내 대상을 알린다. 요청받지 않았다면
토론을 만들지 않는다.

## 이슈와 프로젝트 메타데이터 검토하기

기존 저장소 레이블, 지정 가능한 담당자, 마일스톤, 사용 가능한 이슈 유형을
확인한다. [공통 기준](metadata.md)을 써서 관련 값을 추천한다.
GitHub 마일스톤은 저장소에 속하며, Linear 프로젝트 마일스톤이나 GitHub
Projects 이터레이션이 아니다.

우선순위와 추정치는 조직 이슈 필드, Projects 사용자 정의 필드, 확립된 레이블
관례로 표현될 수 있다. 보편적인 필드가 있다고 가정하거나 Linear식 매핑을
지어내지 말고 실제 구성을 확인한다. 프로젝트 필드라면 대상 프로젝트, 필드
정의와 옵션, 이슈의 프로젝트 항목을 파악한다. 프로젝트에 표시되는 조직
이슈 필드와 이름이 같은 프로젝트 로컬 필드를 구분한다.

기존의 척도와 분류 관례를 쓴다. 우선순위나 추정치를 채우려고 필드를 만들거나
이슈를 무관한 프로젝트에 추가하지 않는다. 그런 관례가 없다면 임의의 값을
본문에 넣거나 우선순위 레이블을 만들지 말고 해당 필드가 구성되지 않았다고
보고한다.

조직 이슈 필드는 현재 이슈 템플릿으로 채울 수 없다. 허가를 받았다면
지원되는 필드 작업으로 적용한다. 프로젝트 소속과 프로젝트 로컬 필드 값도
이슈 생성과는 별도 작업이 필요할 수 있다. 의도한 결과를 각각 확인한다. 이슈
생성에 성공했다고 해서 프로젝트 필드가 설정되었다는 증거는 아니다. 접근이나
도구를 쓸 수 없었던 경우와 적용하지 못한 추천은 따로 보고한다.

## 게시하고 작업 연결하기

이슈를 만들거나 수정하기 전에 소유자와 저장소를 확인한다. 그 범위에서 기존
이슈를 검색하고 중복 가능성이 있는 것을 살펴본다. 기존 Linear 동기화를
존중하며, Linear에 두 번째 티켓을 독자적으로 만들지 않는다.

쪼갤 때는 지원되는 트래커 작업으로 상위/하위 관계나 의존 관계를 기록하며,
상위와 하위에는 하위 이슈(sub-issue)를 쓴다. 본문에서 이슈를 언급했다고
구조화된 관계가 만들어졌다는 증거는 아니다. 이슈 유형은 이슈를 분류할
뿐 계층을 만들지 않는다.

공개 저장소의 이슈는 누구나 볼 수 있다. 취약점이 의심되면 저장소의 보안
정책을 따른다. 정책이 채널을 명시하지 않으면 이슈가 아니라, 활성화되어
있는 경우 비공개 취약점 제보를 쓴다.

공개 저장소의 이슈에 첨부한 파일은 인증 없이 접근할 수 있다. 사용자에게
푸시 권한이 있으면 GitHub CLI로 로컬 이미지와 동영상을 첨부할 수 있고,
그렇지 않으면 증거를 링크하거나 업로드를 사용자에게 맡긴다. 일부만 업로드되어도
이슈는 만들어지므로, 첨부를 보고하기 전에 어떤 것이 렌더링되었는지 확인한다.

`#123` 참조는 해당 저장소 안에서만 유효하다. 저장소를 넘나들 때는
`owner/repository#123`이나 전체 URL을 쓴다. 부분 PR은 완료 키워드 없이
이슈를 참조해야 한다. PR 설명의 GitHub 닫기 키워드는 PR이 기본 브랜치를
대상으로 할 때 적용되며, 그런 PR을 머지하면 참조한 이슈가 닫힌다. 중간 단계
PR에 완료 링크를 쓰지 않고, 기본 브랜치가 아닌 곳으로 머지해도 이슈가 닫힌다고
가정하지 않는다. 실제 PR 작업에는 PR 스킬을 재사용한다.

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
