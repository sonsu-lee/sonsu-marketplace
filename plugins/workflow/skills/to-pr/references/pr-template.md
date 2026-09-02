# PR 템플릿 선택과 작성 규칙

PR title과 body를 작성하기 전에 읽는다. 대상 repository의 유효한 템플릿을 우선하고, 없으면 owner의 account-level default template을 확인한다. 두 위치에 모두 템플릿이 없다고 확인된 경우에만 이 문서의 기본 템플릿을 사용한다.

## repository 템플릿을 먼저 찾는다

GitHub에서 실제로 적용되는 템플릿은 target repository의 default branch를 기준으로 확인한다. current feature branch에만 추가되거나 수정된 템플릿을 현재 PR의 기본 템플릿이라고 간주하지 않는다. 사용자가 해당 변경본을 사용하라고 명시한 경우는 예외다.

다음 공식 위치에서 대소문자를 구분하지 않는 `pull_request_template` 파일과 여러 템플릿 디렉터리를 찾는다. `.md`와 `.txt`처럼 GitHub가 PR template로 사용하는 text 파일을 대상으로 한다. 같은 종류의 파일이 여러 공식 위치에 있으면 GitHub의 `.github`, repository root, `docs` 순서를 적용한다.

```text
.github/pull_request_template.md
pull_request_template.md
docs/pull_request_template.md

.github/PULL_REQUEST_TEMPLATE/*
PULL_REQUEST_TEMPLATE/*
docs/PULL_REQUEST_TEMPLATE/*
```

target repository에서 유효한 PR template을 찾지 못했으면 base repository owner의 public `.github` repository default branch에서 같은 위치와 우선순위로 account-level default template을 확인한다. target repository에 자체 template이 있으면 account-level default와 합치지 않는다.

로컬 default branch ref가 최신인지 확인할 수 없으면 현재 인증 범위 안의 GitHub API나 browser로 default branch의 파일을 읽는다. 이를 위해 fetch, checkout, branch 전환이나 working tree 변경을 수행하지 않는다. target repository나 account-level default의 원격 상태를 확인할 수 없으면 템플릿이 없다고 단정하거나 스킬 기본 템플릿으로 대체하지 않고 `unverified`로 보고한다.

공식 참고: [GitHub PR template 만들기](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository), [PR template 개요](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates), [account-level default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)

## 관련 템플릿 하나를 선택한다

선택 순서는 다음과 같다.

1. 사용자가 정확한 template path나 이름을 지정했으면 그 파일이 default branch에 존재하는지 확인하여 사용한다.
2. `CONTRIBUTING`, repository 문서나 template 자체가 change type·경로별 선택 규칙을 제공하면 실제 diff에 맞는 파일을 사용한다.
3. 공식 위치 우선순위로 결정되는 단일 기본 template이 있으면 사용한다.
4. 여러 template 전용 디렉터리의 후보 중 하나가 실제 변경 유형에 명확히 대응하면 그 근거를 기록하고 사용한다.
5. 유효한 후보가 하나뿐이면 그 파일을 사용한다.
6. 여러 후보가 동등하게 맞고 repository 근거로 선택할 수 없으면 임의로 합치거나 fallback으로 대체하지 않는다. 가능한 title, 변경 요약과 후보 목록까지 준비한 뒤 최종 body 확정이나 publish 전에 사용자에게 template 선택을 요청한다.

선택한 source repository, template path, 기준 default branch와 확인한 ref를 기록한다. 같은 종류의 단일 template이 여러 공식 위치에 중복되어 있거나 내용이 충돌하면 GitHub가 문서화한 `.github`, repository root, `docs` 순서를 적용한다.

## repository 구조를 보존한다

repository 템플릿은 이 스킬의 기본 템플릿보다 우선한다.

- heading, section 순서, checklist, HTML comment, required field와 안내 문구를 읽고 그 지시를 따른다.
- 기존 section에 대응하는 정보가 있으면 그 자리에 작성한다. fallback heading을 중복으로 추가하지 않는다.
- template이 요구하는 빈 section이나 checklist를 일반적인 빈 section 삭제 규칙으로 제거하지 않는다. `N/A` 사용 여부도 repository 지침과 기존 PR 관례를 따른다.
- ticket, validation, risk나 visual evidence에 해당하는 위치가 전혀 없지만 검토에 꼭 필요하면 가장 가까운 기존 free-text field에 넣는다. template이 추가 section을 금지하지 않을 때만 최소 section 하나를 추가하며, 금지되어 있고 기존 field에도 넣을 수 없으면 Draft를 유지하고 제약을 보고한다.
- CLI native attachment가 body 끝에 추가되지만 template의 visual section은 다른 위치에 고정되어 있으면 먼저 Draft PR에 파일을 첨부한다. 저장된 remote URL을 확인한 뒤 그 URL을 지정된 section에 배치한 완성 body를 `gh pr edit --body-file`로 다시 기록하고, append된 중복 URL이 제거되었는지 확인한다.
- HTML comment는 자동화 marker나 숨은 안내일 수 있으므로 기본적으로 보존하고, template이 명시적으로 제거하거나 치환하라고 지시한 부분만 변경한다. visible placeholder와 작성 안내는 지시에 따라 실제 내용으로 바꾸거나 제거하며 실제 결과처럼 남기지 않는다.

`gh pr create --template`은 base repository가 노출한 template filename을 선택하여 body의 시작점만 제공하며, 임의의 local draft file을 읽는 옵션이 아니다. 또한 `--body` 또는 `--body-file`과 함께 사용할 수 없다. 이 스킬은 선택한 repository template을 읽어 완성된 body를 만든 뒤 `--body-file` 하나만 사용한다. 실행 시점의 CLI help로 이 동작을 다시 확인한다. [GitHub CLI `gh pr create`](https://cli.github.com/manual/gh_pr_create)

## 출력 언어를 결정한다

template 선택과 출력 언어 선택은 별개로 처리한다. 생성하는 title, 설명, validation과 caption의 언어는 다음 근거를 순서대로 사용한다.

1. 사용자가 PR 언어를 명시했으면 그 언어를 사용한다.
2. repository의 `CONTRIBUTING`, PR 지침이나 일관된 최근 PR 관례가 언어를 정하면 따른다.
3. 연결할 canonical ticket, 승인된 specification이나 제품 문서가 명확한 주 언어를 사용하면 그 언어를 따른다.
4. 근거가 없으면 사용자가 요청한 출력 언어를 사용하고, 그것도 없으면 현재 대화의 주 언어를 사용한다.

repository template에 이미 있는 heading, checklist와 고정 안내 문구는 번역하지 않는다. 채워 넣는 내용만 결정된 PR 언어로 작성한다. template이 특정 언어로 전체 작성을 요구하면 그 지시를 따른다. 코드, 명령어, 로그, identifier, ticket ID와 URL은 번역하지 않는다. 다른 언어 플러그인이나 스킬이 설치되었다고 가정하지 않는다.

## repository와 account template이 없으면 기본 템플릿을 사용한다

target repository와 owner의 account-level default에 유효한 PR template이 모두 없다고 확인된 경우에만 아래 구조를 사용한다. heading은 결정된 PR 언어의 자연스러운 표현으로 바꾸되 section의 의미와 순서를 유지한다.

| 의미 | English | 한국어 | 日本語 |
| --- | --- | --- | --- |
| Summary | Summary | 요약 | 概要 |
| Changes | Changes | 변경 사항 | 変更内容 |
| Related work | Related work | 관련 작업 | 関連作業 |
| Validation | Validation | 검증 | 検証 |
| Risks | Risks | 위험 및 참고 | リスク・注意事項 |
| Visual evidence | Visual evidence | 시각 증거 | 画面確認 |

```markdown
## <Summary heading>

<Why the change is needed and what behavior results>

## <Changes heading>

- <Change that exists in the reviewed diff>

## <Related work heading, only when verified>

- <Ticket relationship and canonical URL>

## <Validation heading>

- `<command or check>` — <actual result>
- <Not run and the reason, when applicable>

## <Risks heading, only when material>

- <Known limitation, compatibility concern or follow-up>

## <Visual evidence heading, only when required>

<Marked image descriptions, video captions and attachment order>
```

`Summary`, `Changes`와 `Validation`은 기본 section이다. `Related work`, `Risks`와 `Visual evidence`는 실제 근거가 있을 때만 포함한다. `Validation`을 실행하지 않았다면 section을 숨기지 않고 `not_run`과 이유를 정확히 적는다. 위 기본 템플릿 code block의 angle-bracket placeholder와 작성 안내는 draft를 보여 주거나 publish하기 전에 실제 내용으로 바꾸거나 제거한다.
