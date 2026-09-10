# PR 품질 기준

PR 초안이나 게시 payload를 작성할 때 읽는다.

## 변경 범위를 증명한다

- 사용자가 지정한 base를 우선하고, 없으면 저장소 설정과 default branch를 확인한다.
- merge base부터 current head까지의 commit과 전체 diff를 읽는다.
- head와 base가 같거나 commit range가 비어 있으면 새 PR payload로 진행하지 않는다.
- staged·unstaged·untracked 변경을 commit range와 구분한다.
- unrelated commit이나 파일이 있으면 포함 범위를 임의로 정리하지 않고 보고한다.
- 기존 PR, PR 양식, `CONTRIBUTING`과 실제 저장소 관례를 확인한다.

## title과 body를 작성한다

title은 실제 결과를 한 문장으로 설명하고 repository의 semantic 제목 또는 Conventional Commit 관례가 있으면 따른다. 기존 commit이 관례를 어겨도 이 스킬에서 rewrite하지 않는다.

[PR 템플릿 규칙](pr-template.md)에 따라 target repository의 default branch template을 먼저 사용하고, 없으면 owner의 account-level default template을 사용한다. 둘 다 없다고 확인된 경우에는 그 문서의 기본 템플릿을 사용한다. `Background`는 기존 상황·문제와 변경이 필요한 이유를 설명하고, `Changes`는 실제 diff로 달라지는 동작·결과와 중요한 선택을 설명한다. rollout, migration, compatibility 또는 rollback 주의사항은 리뷰에 필요할 때 `Notes`에 쓴다.

저장소 template이 요구하는 section과 checklist는 보존한다. 기본형의 순서는 `Background`, `Changes`, `Related work`, `Screenshots and videos`, `Notes`다. `Background`와 `Changes`는 필수, `Related work`와 `Notes`는 선택이며, `Screenshots and videos`는 UI 변경·사용자 요청·저장소 규칙이 요구할 때 필수다. 기본형의 작성 안내와 필수·선택 표시는 완성된 초안에서 제거하고, 내용이 없는 선택 section은 생략한다. heading과 본문은 결정된 PR 언어로 작성하되 저장소 template의 고정 문구는 임의로 번역하지 않는다.

설명과 보고는 출력 언어의 Fluent Languages 스킬이 있으면 함께 적용한다. 한국어는 `fluent-languages:fluent-korean`을 사용한다. 고정 양식·코드·식별자·링크와 의무 수준은 보존하고, 해당 스킬이 없어도 작업은 계속한다.

## 티켓과 시각 증거를 확인한다

- 티켓 프로바이더, ID, URL, 관계 의도와 상태 효과를 구분한다.
- 같은 작업을 나타내는 동기화 티켓에 completion 신호를 중복으로 보내지 않는다.
- branch 이름을 티켓 연결의 필수 조건으로 만들지 않는다.
- UI 변경, 사용자 요청 또는 저장소 규칙이 요구하면 `Screenshots and videos`를 포함하고 [시각 증거 규칙](visual-evidence.md)을 따른다.
- CLI attachment를 사용할 때에도 선택한 template의 항목 순서를 유지한다. 기본형에서는 `Screenshots and videos`가 `Notes` 앞에 온다. 파일을 첨부해 remote URL을 얻은 뒤 지정된 section에 URL을 넣은 완성 body를 다시 기록하고 본문 끝의 중복 URL을 제거한다.
- placeholder, 로컬 미디어와 실제 업로드 URL을 구분한다.
- PR에 첨부하는 이미지는 애니메이션 GIF를 포함하여 변경 위치를 눈에 띄게 마킹한 사본이며, marker가 가리키는 내용을 alt text에 설명한다.
- 비디오는 alt text를 받을 수 없으므로 같은 `Screenshots and videos` section에서 `Video N`과 upload 순서를 명시하고, 목적, 관찰할 동작과 유용한 timestamp를 설명한다.
- 최종 첨부 사본의 EXIF·GPS·XMP, SVG metadata와 video container metadata를 검사하고 민감하거나 불필요한 값을 제거했는지 확인한다.
- 미디어를 넣는 PR은 첨부 없는 Draft PR을 먼저 확인하고 파일을 하나씩 추가하며, 필수 첨부를 모두 확인한 뒤에만 ready로 전환한다.

## validation을 정확히 쓴다

기본형에는 별도 `Validation` section을 두지 않고 CI에서 확인할 수 있는 결과를 반복하지 않는다. 저장소 template이 검증 항목을 요구하면 그 자리에 작성한다. 수동 확인 결과나 CI가 다루지 않는 중요한 미검증 범위는 기본형의 `Notes`에 쓴다. 본문 형식과 별개로 게시 전 검증 근거와 상태는 확인한다.

실제 실행, 정적 검사, 브라우저 확인, mock·fixture, `not_run`, `inconclusive`와 환경 부족을 구분한다. 명령이 성공했어도 검증 범위가 좁으면 그 범위만 보고한다. CI는 현재 상태를 다시 읽기 전까지 성공이라고 표현하지 않는다.

## 게시 전 검사

- 저장소, visibility, base, head, remote와 인증 주체가 정확한가?
- current head와 본문이 같은 변경을 설명하는가?
- 같은 head의 기존 PR이 없는가?
- final 제목, 본문, ticket link, validation과 미디어가 권한 범위 안에 있는가?
- 상태 미지정 publish는 Draft이고, Ready라면 사용자의 명시적인 요청 근거가 있는가?
- 비밀, token, 개인정보, 내부 URL과 제한된 보안 정보가 제거되었는가?
- 일반 push만 필요하며 fork, remote 변경 또는 force push가 필요하지 않은가?

게시 후에는 원격 PR을 다시 읽고 생성 응답과 실제 저장 상태를 대조한다.
