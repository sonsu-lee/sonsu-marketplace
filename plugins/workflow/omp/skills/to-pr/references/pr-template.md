# PR 템플릿 선택과 작성 규칙

PR title과 body를 작성하기 전에 읽는다. 대상 repository의 유효한 템플릿을 우선하고, 없으면 owner의 account-level default template을 확인한다. 번들 기본 템플릿의 적용 조건은 [기본 템플릿 적용 조건](#기본-템플릿-적용-조건을-확인한다)을 따른다.

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

`CONTRIBUTING`, `AI_POLICY.md`, `AGENTS.md`의 PR 본문 요구는 양식의 필수 항목과 같이 확인한다. 다만 AI 공개 요구는 [공통 AI 사용 표기 규칙](../../../references/tracker-prose.md#ai-사용-표기)에 따라 작성 권한과 충돌을 처리하며 자동으로 채우지 않는다.

## 관련 템플릿 하나를 선택한다

선택 순서는 다음과 같다.

1. 사용자가 정확한 양식 path나 이름을 지정했으면 그 파일이 default branch에 존재하는지 확인하여 사용한다.
2. `CONTRIBUTING`, 저장소 문서나 양식 자체가 change type·경로별 선택 규칙을 제공하면 실제 diff에 맞는 파일을 사용한다.
3. 공식 위치 우선순위로 결정되는 단일 기본 template이 있으면 사용한다.
4. 여러 양식 전용 디렉터리의 후보 중 하나가 실제 변경 유형에 명확히 대응하면 그 근거를 기록하고 사용한다.
5. 유효한 후보가 하나뿐이면 그 파일을 사용한다.
6. 여러 후보가 동등하게 맞고 저장소 근거로 선택할 수 없으면 임의로 합치거나 fallback으로 대체하지 않는다. 가능한 제목, 변경 요약과 후보 목록까지 준비한 뒤 최종 본문 확정이나 publish 전에 사용자에게 양식 선택을 요청한다.

선택한 source 저장소, 양식 path, 기준 default branch와 확인한 ref를 기록한다.

## 출력 언어를 결정한다

양식 선택과 출력 언어 선택은 별개로 처리한다. 생성하는 제목, 설명, validation과 caption의 언어는 다음 근거를 순서대로 사용한다.

1. 사용자가 PR 언어를 명시했으면 그 언어를 사용한다.
2. repository의 `CONTRIBUTING`, `AGENTS.md`·`CLAUDE.md`, PR 지침이나 일관된 최근 PR 관례가 언어를 정하면 따른다.
3. 연결할 기준 티켓, 승인된 specification이나 제품 문서가 명확한 주 언어를 사용하면 그 언어를 따른다.
4. 근거가 없으면 영어를 사용한다. 대화 언어와 결과 보고 언어는 PR 언어의 근거가 아니다.

저장소 template에 이미 있는 제목, checklist와 고정 안내 문구는 번역하지 않는다. 채워 넣는 내용만 결정된 PR 언어로 작성한다. template이 특정 언어로 전체 작성을 요구하면 그 지시를 따른다. 코드, 명령어, 로그, identifier, ticket ID와 URL은 번역하지 않는다. 다른 언어 플러그인이나 스킬이 설치되었다고 가정하지 않는다.

고정 제목이 한국어나 일본어라는 사실만으로 자유 설명의 언어를 정하지 않는다. 전체 작성 언어를 요구하는 지침이나 위의 언어 근거가 없으면 고정 제목은 원문대로 보존하고 자유 설명은 영어로 쓴다.

## 기본 템플릿 적용 조건을 확인한다

target repository와 owner의 account-level default에 유효한 PR template이 모두 없다고 확인된 경우에만 번들 [PR 기본 양식](../assets/templates/pull-request.md)을 사용한다. 저장소나 account-level template을 확인하지 못한 `unverified` 상태에서는 임시 문구가 준비됐더라도 기본형으로 최종 본문을 확정하지 않는다. 확인된 사실로 준비 가능한 설명만 작성하고, 양식 확인 상태와 남은 게시 조건을 본문 밖에서 알린다. 확인된 변경 요약과 미확인 사항은 전달할 수 있지만, 양식 부재나 게시 준비 완료로 표현하지 않는다.
