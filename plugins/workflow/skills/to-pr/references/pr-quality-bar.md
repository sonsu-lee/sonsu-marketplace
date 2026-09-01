# PR 품질 기준

PR 초안이나 게시 payload를 작성할 때 읽는다.

## 변경 범위를 증명한다

- 사용자가 지정한 base를 우선하고, 없으면 repository 설정과 default branch를 확인한다.
- merge base부터 current head까지의 commit과 전체 diff를 읽는다.
- head와 base가 같거나 commit range가 비어 있으면 새 PR payload로 진행하지 않는다.
- staged·unstaged·untracked 변경을 commit range와 구분한다.
- unrelated commit이나 파일이 있으면 포함 범위를 임의로 정리하지 않고 보고한다.
- 기존 PR, PR template, `CONTRIBUTING`과 실제 repository 관례를 확인한다.

## title과 body를 작성한다

title은 실제 결과를 한 문장으로 설명하고 repository의 semantic title 또는 Conventional Commit 관례가 있으면 따른다. 기존 commit이 관례를 어겨도 이 스킬에서 rewrite하지 않는다.

PR template을 우선한다. template이 없으면 필요한 항목만 사용한다.

```markdown
## Summary

## Changes

## Tickets

## Validation

## Visual evidence

## Risks
```

빈 섹션은 만들지 않는다. `Summary`는 변경 이유와 결과를 설명하고, `Changes`는 실제 diff에 있는 내용만 기록한다. rollout, migration, compatibility 또는 rollback 위험이 실제로 있을 때만 해당 내용을 추가한다.

## 티켓과 시각 증거를 확인한다

- 티켓 provider, ID, URL, 관계 의도와 상태 효과를 구분한다.
- 같은 작업을 나타내는 동기화 티켓에 completion 신호를 중복으로 보내지 않는다.
- branch 이름을 티켓 연결의 필수 조건으로 만들지 않는다.
- UI 변경이 있거나 사용자가 요청한 경우에만 `Visual evidence`를 포함한다.
- placeholder, 로컬 이미지와 실제 업로드 URL을 구분한다.
- 각 이미지에는 목적을 설명하는 alt text를 붙인다.

## validation을 정확히 쓴다

실제 실행, 정적 검사, browser 확인, mock·fixture, `not_run`, `inconclusive`와 환경 부족을 구분한다. 명령이 성공했어도 검증 범위가 좁으면 그 범위만 보고한다. CI는 현재 상태를 다시 읽기 전까지 성공이라고 표현하지 않는다.

## 게시 전 검사

- repository, visibility, base, head, remote와 인증 주체가 정확한가?
- current head와 본문이 같은 변경을 설명하는가?
- 같은 head의 기존 PR이 없는가?
- final title, body, ticket link, validation과 이미지가 권한 범위 안에 있는가?
- 비밀, token, 개인정보, 내부 URL과 제한된 보안 정보가 제거되었는가?
- 일반 push만 필요하며 fork, remote 변경 또는 force push가 필요하지 않은가?

게시 후에는 원격 PR을 다시 읽고 생성 응답과 실제 저장 상태를 대조한다.
