# PR 품질 기준

PR 초안이나 게시 payload의 설명과 근거를 검토할 때 읽는다. 적용 양식·언어는 [PR 템플릿 규칙](pr-template.md), 본문 구성과 표현은 [PR 작성 지침](pr-writing.md), 게시 조건과 원격 확인은 [GitHub PR 규칙](github.md)을 따른다.

## 실제 변경을 설명한다

merge base부터 current head까지의 commit과 전체 diff를 읽고 staged·unstaged·untracked 변경과 구분한다. 관련 없는 commit이나 파일이 있으면 포함 범위를 임의로 정리하지 않고 보고한다.

저장소의 semantic 제목 또는 Conventional Commit 관례를 확인하고 작성할 제목에 적용한다. 기존 commit이 관례를 어겨도 이 스킬에서 rewrite하지 않는다.

번들 작성 지침에 전달할 실제 변경, 설계 근거와 rollout·migration·호환성·rollback 제약을 확보한다. 제목·본문이 최종 head와 같은 변경을 설명하는지 확인한다.

Writing·Fluent 적용은 [공통 결합 기준](../../../references/writing-composition.md)을 따른다. 표현을 고친 뒤에도 고정 양식·코드·식별자·링크·의무 수준과 보호할 연결 문법을 다시 대조한다.

## 근거의 범위를 정확히 표현한다

티켓 연결은 [연결 규칙](ticket-linking.md)에 따라 canonical 대상, 관계 의도와 상태 효과를 구분한다. 같은 작업의 동기화 티켓에 completion 신호를 중복으로 보내지 않는다.

미디어가 있으면 [시각 증거 규칙](visual-evidence.md)과 [첨부 규칙](media-attachments.md)을 적용한다. 캡처가 보여 주는 동작, 마킹·설명과 현재 diff가 일치하는지 확인하고 로컬 파일·placeholder·실제 업로드 URL을 구분한다. 본문에 URL이 있다는 사실만으로 표시·재생 성공을 주장하지 않는다.

실제 실행, 정적 검사, 브라우저 확인, mock·fixture, `not_run`, `inconclusive`와 환경 부족을 구분한다. 좁은 검사의 성공을 전체 검증 성공으로 확대하지 않으며, 현재 CI 상태를 읽기 전에는 성공이라고 표현하지 않는다. 검증 내용을 본문에 넣을 위치는 선택한 템플릿을 따르되 게시 전 검증 근거 확인은 생략하지 않는다.

비밀·token·개인정보·공개 범위에 맞지 않는 내부 URL과 제한된 보안 정보가 없는지 확인한다. 준비한 초안과 실제 게시 결과, 부분 성공과 미확인 상태를 구분해 보고한다.
