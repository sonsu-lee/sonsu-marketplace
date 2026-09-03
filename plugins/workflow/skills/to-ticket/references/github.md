# GitHub Issues 게시 규칙

GitHub Issues용 payload를 작성하거나 게시하라는 요청이 있을 때만 읽는다.

## 대상과 관례를 확인한다

- 정확한 `[HOST/]OWNER/REPOSITORY`와 public·private 가시성을 확인한다.
- `.github/ISSUE_TEMPLATE/**`, issue form, `CONTRIBUTING`과 기존 issue 관례를 읽는다.
- 같은 목적의 열린 issue를 제목뿐 아니라 본문과 범위까지 검색한다.
- assignee, label, milestone, issue type, project, parent와 dependency는 repository에 존재하고 사용자가 요청했거나 근거가 있을 때만 사용한다.

GitHub가 별도 필드로 지원하지 않거나 현재 도구가 노출하지 않는 중립 필드는 Markdown 본문에 보존한다. 새 issue의 기본 상태를 유지하며 별도 요청 없이 생성 직후 상태를 바꾸지 않는다.

조직에 실제 issue type이 있으면 중립 `kind`를 repository 관례에 따라 매핑한다. 일반적으로 `defect`는 `bug`, 새로운 사용자 결과는 `feature`, 일반 유지 작업은 `task`와 대응할 수 있지만 실제 type, label과 최근 issue 근거 없이 확정하지 않는다. `investigation`과 `maintenance`를 위해 존재하지 않는 custom type을 만들지 않는다.

parent와 sub-issue는 hierarchy이며 issue type을 대신하지 않는다. 하나의 결과를 담은 issue가 너무 커서 독립적으로 판정 가능한 결과로 나뉠 때만 sub-issue 관계를 제안하거나 사용한다.

## 현재 interface에 맞춘다

전용 GitHub MCP가 있으면 먼저 현재 tool schema를 확인한다. 일반적인 `create_issue` 도구는 `owner`, `repo`, `title`, `body`와 선택적인 `assignees`, `labels`, `milestone`을 받지만, connector마다 project, type과 관계 지원 범위가 다르다.

GitHub CLI를 사용한다면 실행 시점의 `gh issue create --help`를 확인한다. 현재 CLI는 `--repo`, `--title`, `--body-file`, `--assignee`, `--label`, `--milestone`, `--project`, `--type`, `--parent`, `--blocked-by`, `--blocking`을 지원할 수 있다. 본문은 임시 파일에 정확히 기록하고 `--body-file`로 전달하며 shell 문자열 보간으로 payload를 만들지 않는다.

milestone은 MCP에서 숫자 ID를, CLI에서 이름을 요구할 수 있다. 이름과 ID를 임의 변환하지 말고 현재 repository에서 조회한다. project 연결에 추가 scope가 필요해도 `gh auth refresh`나 권한 확대를 자동 실행하지 않는다.

priority, estimate와 Status가 GitHub Project custom field이면 issue field가 아니다. issue를 한 번 생성한 뒤 확인된 project item으로 추가하고, 실제 project·item·field와 option ID 또는 현재 CLI가 검증한 이름을 사용하여 field별로 갱신한다. 권한이나 project scope가 없으면 issue 생성 성공과 project field 미적용을 분리해 보고한다. 생성만 요청받은 issue를 임의의 In Progress 계열 Status로 바꾸지 않는다.

## 게시하고 검증한다

1. 접근 가능한 repository와 인증 주체를 비밀값 없이 확인한다.
2. 최종 제목, Markdown 본문과 지원되는 metadata를 확정한다.
3. issue를 한 번 생성하고 반환된 번호와 URL을 기록한다.
4. parent가 생성 payload에 필요하면 부모를 먼저 만들고 번호를 확인한 뒤 자식을 만든다. 나머지 관계와 Project custom field는 번호와 project item이 확인된 뒤 지원되는 도구로 하나씩 적용한다.
5. 각 별도 operation 뒤 번호나 URL로 issue와 필요한 project item을 다시 읽어 제목, 상태, assignee, label, milestone, type, project field와 관계를 확인한다.

관계나 project 연결이 별도 원격 작업이고 기존 게시 권한 범위에 포함되지 않으면 수행하지 않는다. 도구가 구조화된 관계를 지원하지 않으면 본문에 의미를 보존하고 제한을 보고한다. 생성 응답이 불명확하면 같은 명령을 반복하지 않고 repository에서 제목과 본문을 검색하며, 확인되지 않으면 `unknown`으로 남긴다. 후속 operation은 재조회에서 미적용이 확인된 경우에만 재시도한다.

공식 interface와 개념 참고: [GitHub CLI `gh issue create`](https://cli.github.com/manual/gh_issue_create), [GitHub Project item 추가](https://cli.github.com/manual/gh_project_item-add), [GitHub Project field 변경](https://cli.github.com/manual/gh_project_item-edit), [GitHub issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types-in-an-organization), [GitHub sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)
