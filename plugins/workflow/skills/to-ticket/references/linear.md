# Linear 작성·게시 규칙

Linear용 payload를 작성·게시하거나 기존 제목·본문을 조회·수정할 때 읽는다.

## 대상과 필드를 확인한다

- 연결된 workspace와 필수 team을 확인한다.
- 제목과 Markdown description을 준비한다.
- project, cycle, state, priority, estimate, assignee, delegate, label, milestone과 due date는 사용자 요청이나 workspace 근거가 있을 때만 사용한다.
- parent, `blockedBy`, `blocks`, `relatedTo`, duplicate와 release는 사용자가 요청하고 현재 도구가 지원할 때만 사용한다.

team과 제목 이외의 값을 추정하지 않는다. 이름을 ID로 해석해야 하면 현재 workspace에서 정확히 조회한다. priority 숫자, state와 estimate 체계는 현재 tool schema와 team 설정을 확인하지 않고 만들지 않는다.

작업 분류는 workspace의 기존 label group과 양식 관례를 따른다. 기본 양식과 별개로 실제 schema가 지원하는 값만 사용하고, 새 label·양식·property를 만들거나 공통 `kind`로 강제 매핑하지 않는다.

project, parent와 sub-issue는 작업 종류가 아니라 hierarchy다. 큰 범위를 project로 바꾸거나 sub-issue를 추가하는 것은 사용자가 요청했거나 근거 문서의 분해가 이를 요구할 때만 수행한다.

milestone은 확인된 project에 속하므로 project 없이 추정하여 지정하지 않는다. 생성만 요청받으면 양식·team의 기본 초기 status를 유지한다. 명시적인 초기 status가 create interface에서 허용될 때만 사용하며, 작업 시작 요청은 생성·재조회 뒤 별도 lifecycle intent로 처리한다.

## 현재 interface에 맞춘다

Linear MCP의 현재 tool schema를 먼저 확인한다. Codex connector에서 일반적인 생성 도구는 `save_issue`이며, 새 티켓에는 `team`과 `title`을 사용하고 `description`, `project`, `cycle`, `state`, `priority`, `estimate`, `assignee`, `labels`, `milestone`, `parentId`, `blockedBy`, `blocks`, `relatedTo` 등을 선택적으로 받을 수 있다. 실제 이름과 인자는 connector 버전에 따라 달라질 수 있으므로 이 목록만 믿고 호출하지 않는다.

필요한 값만 `list_teams`, `list_issue_statuses`, `list_issue_labels`, project·cycle 조회 도구로 확인한다. 유사 티켓은 `list_issues`나 검색 도구에서 team, 제목, 설명과 범위를 함께 비교한다. 여러 workspace를 추정하여 전환하거나 새 인증 context를 만들지 않는다.

## 생성하고 검증한다

[공통 생성 절차](../SKILL.md#새-티켓을-게시한다)를 따른다. workspace·team과 필요한 필드를 확인하고 이슈를 한 번 생성해 ID를 보존한다. 여러 티켓이면 `client_key`를 원격 ID에 매핑하고, 모든 대상이 존재한 뒤 생성 시 적용하지 못한 필드·parent·관계를 하나씩 연결한다.

각 작업 뒤 관계를 포함해 이슈를 다시 읽고 URL·제목·team·state·필드·관계를 대조한다. 인증 만료나 workspace 전환이 필요하면 자동 로그인·전환 없이 미적용 범위를 보고한다.

## 기존 제목·본문 수정

`revise`에서는 정확한 workspace·team의 canonical ID와 현재 제목·전체 description을 먼저 읽는다. 생성에 쓰는 `save_issue`가 갱신도 지원한다면 현재 schema에서 확인한 기존 ID 인자를 반드시 포함한다. ID가 없거나 갱신 경로를 확인할 수 없으면 생성 호출로 대체하지 않는다.

갱신 payload에는 식별자와 요청한 제목·description만 넣는다. state·assignee·label·parent·relation이나 생성 양식 기본값을 함께 보내지 않는다. 최신 원문·수정 시각을 쓰기 직전에 다시 확인하고, drift·conditional update·불명확한 응답은 공통 Revise 규칙으로 처리한다. 갱신 후 제목·전체 description을 읽어 요청 밖의 내용도 보존됐는지 확인한다.

공식 interface와 개념 참고: [Linear MCP server](https://linear.app/docs/mcp), [Linear issue 생성 규칙](https://linear.app/docs/creating-issues), [Issue relation](https://linear.app/docs/issue-relations), [Issue labels](https://linear.app/docs/labels), [Issue templates](https://linear.app/docs/issue-templates), [Jira와의 issue type 차이](https://linear.app/docs/jira)

## 이미지와 동영상을 첨부한다

[공통 첨부 규칙](media-attachments.md)과 현재 MCP schema를 확인한다. 다음 도구가 노출된 연결에서는 정확한 기존 이슈 ID로 파일마다 전 과정을 마친다.

1. `prepare_attachment_upload`에 `issue`, `filename`, `contentType`, 정확한 바이트 `size`를 전달한다.
2. 반환된 `uploadRequest.url`로 파일 원본 바이트를 `PUT`한다. MCP 밖의 `curl --data-binary` 등 지원되는 전송 수단을 사용한다. 반환된 서명 헤더는 대소문자를 포함해 그대로 보내고 파일을 base64로 변환하지 않는다.
3. PUT 성공을 확인한 뒤 `create_attachment_from_upload`에 동일 이슈와 반환된 `assetUrl`을 전달한다. 이 도구는 파일 전송이 아니라 첨부 연결을 담당한다.
4. `assetUrl`을 description의 재현 자료 위치에 넣고 이슈·첨부·본문 표시를 다시 확인한다. 첨부 연결만으로 본문 안에 표시됐다고 판단하지 않는다.

현재 도구 설명의 서명 URL 유효 시간은 60초다. 실행 시 schema를 다시 확인하고, 여러 파일의 업로드 URL을 미리 일괄 발급하지 않는다. 헤더 누락·변경이나 만료로 PUT이 실패했다고 확인되면 원인을 해결한 뒤 다시 준비한다. 전송 여부가 불명확하면 재업로드하지 않고 공통 복구 규칙을 따른다.

`create_attachment`의 base64 전송은 현재 연결에서 작은 파일용의 폐기 예정 대체 경로다. 직접 PUT 경로를 우선한다. 대체 경로를 써야 한다면 원본에서 기계적으로 인자를 만들고 SHA-256·크기를 대조한다. base64를 출력해 모델이 복사하거나 영상 전체를 도구 인자에 넣지 않는다.

공식 API는 접근 가능한 이미지·영상 URL을 Markdown에 넣어 가져오는 방식도 지원한다. 이미 사용할 수 있는 URL이 있을 때만 이 경로를 검토하고, 업로드 편의를 위해 새 공개 저장소를 만들지 않는다. Linear 파일은 비공개 저장소에 있으므로 외부 열람에는 인증이 필요하다. 전송용 서명 URL이나 만료되는 임시 다운로드 URL을 영구 본문 참조로 쓰지 않는다.

공식 참고: [파일 업로드](https://linear.app/developers/how-to-upload-a-file-to-linear), [이슈 첨부 연결](https://linear.app/developers/attachments), [파일 접근 인증](https://linear.app/developers/file-storage-authentication)
