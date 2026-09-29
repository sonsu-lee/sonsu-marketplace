# PR 템플릿 선택과 작성 규칙

PR title과 body를 작성하기 전에 읽는다. 대상 repository의 유효한 템플릿을 우선하고, 없으면 owner의 account-level default template을 확인한다. 두 위치에 모두 템플릿이 없다고 확인된 경우에만 이 문서의 기본 템플릿을 사용한다.

## 저장소 템플릿을 먼저 찾는다

GitHub에서 실제로 적용되는 템플릿은 target repository의 default branch를 기준으로 확인한다. current feature branch에만 추가되거나 수정된 템플릿을 현재 PR의 기본 템플릿이라고 간주하지 않는다. 사용자가 해당 변경본을 사용하라고 명시한 경우는 예외다.

다음 공식 위치에서 대소문자를 구분하지 않는 `pull_request_template` 파일과 여러 템플릿 디렉터리를 찾는다. `.md`와 `.txt`처럼 GitHub가 PR template로 사용하는 text 파일을 대상으로 한다. 같은 종류의 파일이 여러 공식 위치에 있으면 GitHub의 `.github`, 저장소 root, `docs` 순서를 적용한다.

```text
.github/pull_request_template.md
pull_request_template.md
docs/pull_request_template.md

.github/PULL_REQUEST_TEMPLATE/*
PULL_REQUEST_TEMPLATE/*
docs/PULL_REQUEST_TEMPLATE/*
```

target repository에서 유효한 PR template을 찾지 못했으면 base 저장소 owner의 public `.github` 저장소 default branch에서 같은 위치와 우선순위로 account-level default template을 확인한다. target repository에 자체 template이 있으면 account-level default와 합치지 않는다.

로컬 default branch ref가 최신인지 확인할 수 없으면 현재 인증 범위 안의 GitHub API나 browser로 default branch의 파일을 읽는다. 이를 위해 fetch, checkout, branch 전환이나 working tree 변경을 수행하지 않는다. target repository나 account-level default의 원격 상태를 확인할 수 없으면 템플릿이 없다고 단정하거나 스킬 기본 템플릿으로 대체하지 않고 `unverified`로 보고한다.

공식 참고: [GitHub PR template 만들기](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository), [PR template 개요](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates), [account-level default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)

## 관련 템플릿 하나를 선택한다

선택 순서는 다음과 같다.

1. 사용자가 정확한 양식 path나 이름을 지정했으면 그 파일이 default branch에 존재하는지 확인하여 사용한다.
2. `CONTRIBUTING`, 저장소 문서나 양식 자체가 change type·경로별 선택 규칙을 제공하면 실제 diff에 맞는 파일을 사용한다.
3. 공식 위치 우선순위로 결정되는 단일 기본 template이 있으면 사용한다.
4. 여러 양식 전용 디렉터리의 후보 중 하나가 실제 변경 유형에 명확히 대응하면 그 근거를 기록하고 사용한다.
5. 유효한 후보가 하나뿐이면 그 파일을 사용한다.
6. 여러 후보가 동등하게 맞고 저장소 근거로 선택할 수 없으면 임의로 합치거나 fallback으로 대체하지 않는다. 가능한 제목, 변경 요약과 후보 목록까지 준비한 뒤 최종 본문 확정이나 publish 전에 사용자에게 양식 선택을 요청한다.

선택한 source 저장소, 양식 path, 기준 default branch와 확인한 ref를 기록한다. 같은 종류의 단일 template이 여러 공식 위치에 중복되어 있거나 내용이 충돌하면 GitHub가 문서화한 `.github`, 저장소 root, `docs` 순서를 적용한다.

## 저장소 구조를 보존한다

실제 템플릿에서 제목·항목 순서·checklist·HTML comment·required field와 안내를 읽고, 고정할 부분과
허용된 편집 범위를 작성 입력으로 전달한다. 내용 배치, 기본형과의 중복 방지, placeholder와 marker의
구분은 번들 [PR 작성 지침](pr-writing.md#양식을-보존한다)을 따른다. 작성 뒤 실제 템플릿과 대조한다.

필수 정보를 담을 항목이 없고 양식이 추가도 허용하지 않으면 Draft를 유지하고 제약을 보고한다.
첨부의 실제 업로드·본문 반영은 [미디어 첨부 규칙](media-attachments.md)을 따른다.

`gh pr create --template`은 base repository가 노출한 양식 filename을 선택하여 body의 시작점만 제공하며, 임의의 local draft file을 읽는 옵션이 아니다. 또한 `--body` 또는 `--body-file`과 함께 사용할 수 없다. 이 스킬은 선택한 저장소 template을 읽어 완성된 body를 만든 뒤 `--body-file` 하나만 사용한다. 실행 시점의 CLI help로 이 동작을 다시 확인한다. [GitHub CLI `gh pr create`](https://cli.github.com/manual/gh_pr_create)

## 출력 언어를 결정한다

양식 선택과 출력 언어 선택은 별개로 처리한다. 생성하는 제목, 설명, validation과 caption의 언어는 다음 근거를 순서대로 사용한다.

1. 사용자가 PR 언어를 명시했으면 그 언어를 사용한다.
2. repository의 `CONTRIBUTING`, PR 지침이나 일관된 최근 PR 관례가 언어를 정하면 따른다.
3. 연결할 기준 티켓, 승인된 specification이나 제품 문서가 명확한 주 언어를 사용하면 그 언어를 따른다.
4. 근거가 없으면 사용자가 요청한 출력 언어를 사용하고, 그것도 없으면 현재 대화의 주 언어를 사용한다.

저장소 template에 이미 있는 제목, checklist와 고정 안내 문구는 번역하지 않는다. 채워 넣는 내용만 결정된 PR 언어로 작성한다. template이 특정 언어로 전체 작성을 요구하면 그 지시를 따른다. 코드, 명령어, 로그, identifier, ticket ID와 URL은 번역하지 않는다. 다른 언어 플러그인이나 스킬이 설치되었다고 가정하지 않는다.

## 기본 템플릿 적용 조건을 확인한다

target repository와 owner의 account-level default에 유효한 PR template이 모두 없다고 확인된 경우에만 번들 [PR 작성 지침](pr-writing.md)의 기본 템플릿을 사용한다. 기본 항목의 의미·순서·필수 여부, 언어별 제목과 작성 안내 정리는 그 지침과 연결된 양식을 따른다. Writing을 설치하지 않아도 번들 지침과 양식으로 작성한다.

저장소나 account-level template을 확인하지 못한 `unverified` 상태에서는 임시 문구가 준비됐더라도 기본형으로 최종 본문을 확정하지 않는다. 확인된 변경 요약과 미확인 사항은 전달할 수 있지만, 양식 부재나 게시 준비 완료로 표현하지 않는다. 적용 양식과 필수 필드 확인은 위 선택 규칙과 게시 절차에서 별도로 완료한다.

검증 근거 확인과 실제 실행·미실행 결과의 구분은 [PR 품질 기준](pr-quality-bar.md)을 따른다. 양식 확인·게시·첨부 준비의 내부 절차는 본문 밖의 결과 보고에 담는다. 필요한 첨부를 준비하지 못한 상태는 시각 증거·미디어 규칙으로 보고하며, 선택 항목 생략으로 처리하지 않는다.
