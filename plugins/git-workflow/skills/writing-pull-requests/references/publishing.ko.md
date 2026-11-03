# 풀 리퀘스트 게시

> 영문 정본: [publishing.md](publishing.md) (`fed67c3` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

게시를 요청받으면 다음 순서로 진행한다.

1. 의도한 저장소, head, base를 확인한다. 사용자의 대상이나 프로젝트 대상을 쓰고,
   없으면 기본 브랜치를 쓴다. 해당 head와 base의 기존 PR을 확인한다. 의존하는
   PR이라면 [스택 PR](stacked-prs.md)을 읽는다.
2. 검증된 제목과 저장소 요구사항에 맞는 완성된 본문을 준비한다. 필요한
   [UI 증거](ui-evidence.md)는 업로드 전에 준비하고 확인한다.
3. 저장소의 워크플로에 따라 의도한 커밋만 의도한 원격 저장소와 브랜치에 push한다.
    새 PR은 Draft로 만들거나 기존 PR을 업데이트한다. 게시만으로는 강제 push, 머지,
    자동 머지 활성화, 리뷰어 요청, 저장소 설정 변경이 필요하지 않다.
4. 실제 PR의 head, base, 제목, 본문, 상태와 렌더링된 미디어를 확인한다. 명령의
   종료 상태만으로 성공을 추정하지 말고 게시나 증거가 미완료라면 보고한다.

환경에서 요구하는 게시 도구를 사용한다. GitHub CLI를 쓴다면 대상 저장소에서
`repo`는 `OWNER/REPO`, `head`와 `base`는 의도한 브랜치, `title`은 검증된 제목,
`body_file`은 완성된 UTF-8 본문 파일의 절대 경로로 설정한다.

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

구조화된 API 호출에서는 `draft: true`를 명시한다. 정확하고 템플릿에 맞는 본문 대신
`--fill`을 쓰지 않는다. CLI의 `--dry-run`도 push할 수 있다.

## 예외 상황

- **기존 PR:** 업데이트 전에 기존 내용과 Draft 또는 ready 상태를 읽고 유지한다.
  본문 교체는 전체 본문을 덮어쓴다.
- **미디어:** 로컬 경로는 작업 디렉터리 기준으로 해석한다. 설치된 CLI의 첨부 지원과
  필요한 push 권한을 확인한다. 없으면 허가된 브라우저 업로드를 이용하거나 장애를
  보고한다. 권한을 바꾸거나 URL을 만들거나 필수 증거를 조용히 생략하지 않는다.
  확인한 파일을 첨부한 뒤 렌더링된 이미지, 캡션, 비디오 재생을 확인한다. 확인하지
  못한 항목은 보고한다. 지원 형식, 배치와 크기 제한은 [GitHub CLI 첨부][attachments]를
  참고한다.
- **부분 성공:** 첨부 실패로 명령이 실패해도 PR은 생성되거나 수정되었을 수 있다.
  재시도 전에 실제 PR과 업로드된 에셋을 확인한다. 생성을 반복하지 말고 기존 PR을
  업데이트하며 빠진 미디어만 첨부한다.
- **이슈 닫기:** GitHub는 PR이 기본 브랜치를 대상으로 할 때만 닫기 키워드를
  처리한다. 다른 base에서는 링크가 만들어지지 않고, 머지해도 이슈가 닫히지
  않는다([이슈 연결][issues]). 이슈를 완료하는 PR이 반영된 뒤 이슈를 확인한다.
  아직 열려 있으면 보고하고, 사용자가 요청했다면 닫는다. 스택은
  [스택 가이드](stacked-prs.md)를 참고한다.
- **머지 메시지:** squash 메시지는 저장소 설정에 따라 달라지며 PR 제목이나 본문을
  쓰지 않을 수 있다. 머지를 준비할 때는 [writing-commits](../../writing-commits/SKILL.md)로
  최종 메시지 전체를 확인하고 검증하며 중요한 근거, 호환성을 깨는 변경과 기여자
  표기를 보존한다. 머지는 사용자가 요청할 때만 한다.

## 참고 자료

- [GitHub CLI create][create], [edit][edit], [첨부][attachments].
- [PR 템플릿][templates]과 [상속되는 기본값][defaults].
- [이슈 닫기][issues]와 [squash 메시지 설정][squash].

[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
[create]: https://cli.github.com/manual/gh_pr_create
[edit]: https://cli.github.com/manual/gh_pr_edit
[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[squash]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
[issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
