# GitHub Issues 작성·게시 규칙

GitHub Issues용 payload를 작성·게시하거나 기존 제목·본문을 조회·수정할 때 읽는다.

## 대상과 관례를 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY`와 public·private 가시성을 확인한다.
- `.github/ISSUE_TEMPLATE/**`, issue form, `CONTRIBUTING`과 기존 issue 관례를 읽는다.
- 같은 목적의 열린 issue를 제목뿐 아니라 본문과 범위까지 검색한다.
- assignee, label, milestone, issue type, project, parent와 dependency는 repository에 존재하고 사용자가 요청했거나 근거가 있을 때만 사용한다.

GitHub가 별도 필드로 지원하지 않거나 현재 도구가 노출하지 않는 중립 필드는 Markdown 본문에 보존한다. 새 issue의 기본 상태를 유지하며 별도 요청 없이 생성 직후 상태를 바꾸지 않는다.

작업 분류는 저장소에 실제로 있는 issue type과 label을 따른다. 기본 양식과 별개로 필요한 값만 설정하며, 플러그인 공통 `kind`나 새 custom type을 만들지 않는다.

parent와 sub-issue는 hierarchy이며 issue type을 대신하지 않는다. 하나의 결과를 담은 issue가 너무 커서 독립적으로 판정 가능한 결과로 나뉠 때만 sub-issue 관계를 제안하거나 사용한다.

## 현재 interface에 맞춘다

전용 GitHub MCP가 있으면 먼저 현재 tool schema를 확인한다. 일반적인 `create_issue` 도구는 `owner`, `repo`, `title`, `body`와 선택적인 `assignees`, `labels`, `milestone`을 받지만, connector마다 project, type과 관계 지원 범위가 다르다.

GitHub CLI를 사용한다면 실행 시점의 `gh issue create --help`를 확인한다. 현재 CLI는 `--repo`, `--title`, `--body-file`, `--assignee`, `--label`, `--milestone`, `--project`, `--type`, `--parent`, `--blocked-by`, `--blocking`을 지원할 수 있다. 본문은 임시 파일에 정확히 기록하고 `--body-file`로 전달하며 shell 문자열 보간으로 payload를 만들지 않는다.

milestone은 MCP에서 숫자 ID를, CLI에서 이름을 요구할 수 있다. 이름과 ID를 임의 변환하지 말고 현재 repository에서 조회한다. project 연결에 추가 scope가 필요해도 `gh auth refresh`나 권한 확대를 자동 실행하지 않는다.

priority, estimate와 Status가 GitHub Project custom field이면 issue field가 아니다. issue를 한 번 생성한 뒤 확인된 project item으로 추가하고, 실제 project·item·field와 option ID 또는 현재 CLI가 검증한 이름을 사용하여 field별로 갱신한다. 권한이나 project scope가 없으면 issue 생성 성공과 project field 미적용을 분리해 보고한다. 생성만 요청받은 issue를 임의의 In Progress 계열 Status로 바꾸지 않는다.

## 생성하고 검증한다

[공통 생성 절차](../SKILL.md#새-티켓을-게시한다)를 따른다. 정확한 저장소와 인증 주체를 확인하고 이슈를 한 번 생성해 번호·URL을 보존한다. parent가 생성 시 필요하면 부모 번호를 먼저 확인한다. 나머지 관계와 Project 필드는 이슈 번호·project item을 확인한 뒤 허가된 범위에서 하나씩 적용한다.

각 작업 뒤 이슈와 필요한 project item을 읽어 상태·담당자·label·milestone·type·Project 필드·관계를 대조한다. 이슈 생성과 후속 필드 적용의 부분 성공을 구분한다. 관계 기능이 없으면 본문에 의미를 남기고 제한을 보고한다.

## 기존 제목·본문 수정

`revise`에서는 정확한 host·저장소·issue 번호와 최신 제목·전체 body를 먼저 읽는다. PR을 issue로 오인하지 않도록 대상 종류도 확인한다. MCP의 현재 update schema 또는 `gh issue edit --help`를 확인하고 기존 issue locator와 요청한 제목·body만 보낸다. CLI 본문은 정확한 임시 파일을 `--body-file`로 전달한다.

label·assignee·milestone·Project field·sub-issue·dependency는 내용 수정 payload에 섞지 않는다. 생성 form을 다시 적용해 기존 제목·작업 기록을 삭제하지 않는다. 쓰기 직전 원문과 지원되는 revision marker를 확인하고 공통 Revise 규칙을 따른다. 수정 뒤 제목·전체 body를 재조회해 실제 변경과 보존 내용을 비교한다.

공식 interface와 개념 참고: [GitHub CLI `gh issue create`](https://cli.github.com/manual/gh_issue_create), [GitHub Project item 추가](https://cli.github.com/manual/gh_project_item-add), [GitHub Project field 변경](https://cli.github.com/manual/gh_project_item-edit), [GitHub issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization), [GitHub sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)

## 이미지와 동영상을 첨부한다

[공통 첨부 규칙](media-attachments.md)을 적용하고 `gh --version`, `gh issue create --help`, `gh issue edit --help`에서 `--attach` 지원을 확인한다. 지원되는 CLI는 이미지·영상을 GitHub 첨부 저장소에 올리고 본문에 URL을 넣는다. 저장소 push 권한과 host·token·파일 제한을 확인한다. 권한이 없거나 CLI가 지원하지 않으면 공식 브라우저 첨부로 전환한다.

새 이슈는 로컬 경로가 없는 본문으로 생성해 번호를 확인한다. 파일마다 `gh issue edit ISSUE_URL --attach FILE`로 첨부하고 저장된 본문에서 실제 URL을 읽는다. 설명·순서와 URL을 `재현 정보`에 배치한 본문을 `--body-file`로 반영하고 끝에 붙은 중복 첨부를 제거한다. 수정 전에는 최신 본문을 읽어 다른 변경을 보존한다.

이미지는 Markdown image와 alt text를, 영상은 단독 문단의 업로드 URL과 별도 설명을 사용한다. `--attach`의 이미지 설명은 `FILE#ALT_TEXT` 형식이며 영상에는 지원되지 않는다. 로컬 경로를 본문에 넣어 자동 치환하는 방식은 부분 실패 시 경로가 남을 수 있으므로 기본 흐름에서 사용하지 않는다.

CLI는 일부 업로드가 실패해도 성공한 첨부로 이슈를 갱신할 수 있다. 종료 코드만 보고 재실행하지 말고 본문을 재조회한다. 파일 전송과 본문 갱신은 원자적이지 않으므로 응답이 불명확하면 공통 복구 규칙을 따른다.

공식 참고: [CLI 첨부](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli), [첨부 형식·크기](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files), [`gh issue edit`](https://cli.github.com/manual/gh_issue_edit)
