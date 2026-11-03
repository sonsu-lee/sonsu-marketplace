# 풀 리퀘스트 게시

> 영문 정본: [publishing.md](publishing.md) (`b57290e` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

1. **대상 확인:** 의도한 저장소, head, base를 쓰고 기존 PR이 있는지 확인한다.
   의존하는 PR이면 [스택 PR](stacked-prs.md)을 읽는다.
2. **내용 준비:** 검증한 제목과 완성한 본문을 쓴다.
   [UI 증거](ui-evidence.md)가 있으면 먼저 준비한다.
3. **push와 생성:** 의도한 커밋만 push하고 Draft를 만들거나 기존 PR을 수정한다.
   게시에는 강제 push, 머지, 자동 머지, 리뷰어 요청, 설정 변경이 포함되지 않는다.
4. **결과 확인:** PR의 head, base, 제목, 본문, Draft 상태, 렌더링된 미디어를
   확인한다. 미완료 항목은 보고한다. 종료 코드는 증거가 아니다.

GitHub CLI라면 대상 저장소에서 다음을 실행한다.

```sh
gh pr create --draft --repo "$repo" --base "$base" --head "$head" \
  --title "$title" --body-file "$body_file"
```

## 주의할 점

- API 호출에서는 `draft: true`를 명시해야 한다.
- `--fill`은 작성한 본문을 대신하지 못하고, `--dry-run`도 push할 수 있다.
- `gh pr edit`의 `--body-file`은 본문 전체를 바꾼다. 수정할 때는 기존 내용과 PR의
  Draft/ready 상태를 유지한다.
- ready 전환은 요청이 있고 저장소의 준비 요건을 충족했을 때만 한다.
- `--attach`로 미디어를 올리려면 CLI 지원과 push 권한이 필요하다. 없으면 허가된
  브라우저 업로드를 쓰거나 장애를 보고하며, URL을 지어내지 않는다. 형식과 제한은
  [GitHub CLI 첨부][attachments]를 참고한다.
- 첨부가 실패해도 PR은 생성되거나 수정됐을 수 있다. 다시 시도하기 전에 PR을
  확인하고 빠진 것만 첨부한다.

## 예외 상황

- **이슈 닫기:** GitHub는 PR이 기본 브랜치를 대상으로 할 때만 closing 키워드를
  처리한다([이슈 연결][issues]). 완료하는 PR이 반영된 뒤 이슈를 확인하고, 아직
  열려 있으면 보고하거나 사용자가 요청했다면 닫는다.
- **머지 메시지:** squash 메시지는 저장소 설정을 따르며 PR 제목이나 본문을 쓰지
  않을 수 있다. 머지를 준비할 때는 [writing-commits](../../writing-commits/SKILL.md)로
  최종 메시지를 검증하고 근거, 호환성을 깨는 변경, 기여자 표기를 유지한다. 머지는
  사용자가 요청할 때만 한다.

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
