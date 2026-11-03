# GitHub Issues

> 영문 정본: [github-issue.md](github-issue.md) (`5cdc0e5` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

GitHub 이슈를 작성하거나 게시할 때 이 절차를 따른다.

## 절차

1. **템플릿을 선택한다.** 대상 저장소의 기본 브랜치에서 기여 지침과 이슈
   템플릿을 읽는다. 이슈 폼, `config.yml`, 지원되는 위치의 레거시 템플릿도
   확인한다. 저장소에 템플릿과 설정이 없으면 소유자의 공개 `.github`
   저장소에서 상속되는 기본값을 확인한다. 요청에 맞는 템플릿을 고르고,
   실질적으로 다른 템플릿이 여러 개 남으면 의도한 이슈 유형을 확인한다.
   맞는 템플릿이 없을 때만 번들된 대체 템플릿을 쓴다. 필수 필드, 레이블과
   그 밖의 의무 메타데이터를 보존한다. API나 CLI로 만들 때는 폼 답변을 읽기
   좋은 섹션으로 구성하고 속성을 따로 적용한다. 필수 체크박스는 알려진
   사실을 반영해야 하며 재현, 검색, 합의를 추측해서 표시하지 않는다.
2. **안내 경로와 공개 범위를 확인한다.** `config.yml`의 연락처 링크가
   요청을 Discussions나 비공개 취약점 제보 등 다른 곳으로 안내하면 이슈를
   만들지 말고 목적지를 알린다. 토론은 요청받았을 때만 만든다. 취약점이
   의심되면 보안 정책을 따르고, 정책에 채널이 없으면 이슈 대신 활성화된
   비공개 취약점 제보를 이용한다.
3. **메타데이터를 검토한다.** 저장소 레이블, 지정 가능한 담당자, 마일스톤과
   이슈 유형을 확인하고 [공통 기준](metadata.md)으로 값을 추천한다.
   우선순위와 추정치의 실제 구성을 확인하고 기존 척도와 분류 관례를 쓴다.
   프로젝트 필드는 대상 프로젝트, 필드 정의와 옵션, 이슈의 프로젝트 항목을
   파악하고, 프로젝트에 표시되는 조직 필드와 이름이 같은 프로젝트 로컬 필드를
   구분한다. 관례가 없으면 임의의 본문 값이나 우선순위 레이블을 만들지 말고
   필드가 구성되지 않았다고 보고한다. 우선순위나 추정치를 채우려고 필드를
   만들거나 이슈를 무관한 프로젝트에 추가하지 않는다.
4. **게시하고 연결한다.** 생성이나 수정 전에 소유자와 저장소를 확인하고 그
   범위의 기존 이슈와 중복 가능성을 살펴본다. 기존 Linear 동기화를 존중하며
   독립적인 두 번째 티켓을 만들지 않는다. 작업을 쪼갤 때는 지원되는 작업으로
   상위/하위 관계나 의존 관계를 기록하고, 상위와 하위에는 하위 이슈를 쓴다.
   허가받은 조직 필드는 지원되는 작업으로 적용한다. 프로젝트 소속과 로컬
   필드도 별도 작업이 필요할 수 있다. 의도한 결과를 각각 확인하고 접근이나
   도구를 쓸 수 없는 경우와 적용하지 못한 추천을 따로 보고한다.
5. **증거와 PR을 연결한다.** 공개 저장소에서 사용자가 푸시 권한을 가진
   경우에만 GitHub CLI로 로컬 이미지와 동영상을 첨부한다. 그렇지 않으면
   증거를 링크하거나 업로드를 사용자에게 맡긴다. 보고하기 전에 어떤 첨부가
   렌더링되었는지 확인한다. 다른 저장소를 참조할 때는
   `owner/repository#123`이나 전체 URL을 쓴다. 중간 단계 PR은 완료 키워드
   없이 연결하고 실제 PR 작업에는 PR 스킬을 재사용한다.

## 주의사항

- 로컬 이슈 템플릿이나 선택기 설정이 있으면 맞는 로컬 템플릿이 없어도 상속된
  `.github/ISSUE_TEMPLATE` 디렉터리는 적용되지 않는다. 작업 브랜치에 GitHub가
  현재 제공하는 템플릿이 없을 수 있다.
- 폼 YAML은 생성 스키마이지 이슈 설명이 아니다. 조직 이슈 필드는 현재 이슈
  템플릿으로 채울 수 없다.
- GitHub 마일스톤은 저장소에 속하며 Linear 프로젝트 마일스톤이나 GitHub
  Projects 이터레이션이 아니다. 우선순위와 추정치는 조직 이슈 필드, Projects
  사용자 정의 필드 또는 확립된 레이블 관례로 표현될 수 있다. 보편적인
  필드나 Linear식 매핑을 가정하지 않는다.
- 이슈 생성만으로 프로젝트 필드 설정이 증명되지는 않는다. 본문에서 언급한
  것만으로 구조화된 관계가 만들어지지 않으며, 이슈 유형은 분류할 뿐 계층을
  만들지 않는다.
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
