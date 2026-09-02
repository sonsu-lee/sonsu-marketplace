# Codex pull request 리뷰

## 목적

Codex가 리뷰 가능한 pull request에만 자동으로 리뷰를 요청하도록 구성합니다. 리뷰 요약과
인라인 코멘트는 한국어로 작성하며, Draft pull request와 `skip-codex-review` 라벨이 붙은
pull request에는 자동 리뷰를 요청하지 않습니다.

## 동작 계약

| GitHub 이벤트 | Draft | `skip-codex-review` | 결과 |
| --- | --- | --- | --- |
| `opened` 또는 `reopened` | 아니요 | 없음 | `@codex review` 요청 |
| `opened` 또는 `reopened` | 예 | 관계없음 | 실행하지 않음 |
| `ready_for_review` | 아니요 | 없음 | `@codex review` 요청 |
| `ready_for_review` | 아니요 | 있음 | 실행하지 않음 |

라벨로 Draft에서 Open으로 바뀔 때의 리뷰를 막으려면 Draft 상태에서
`skip-codex-review` 라벨을 먼저 붙인 뒤 **Ready for review**로 전환합니다. 라벨을 나중에
제거하더라도 자동으로 밀린 리뷰를 요청하지 않으며, 필요하면 pull request에
`@codex review`를 직접 작성합니다.

## 사전 설정

1. 리뷰 요청을 작성할 GitHub 계정을 Codex에 연결하고, 이 저장소의 Code review를
   활성화합니다.
2. Codex Code review 설정에서 Automatic reviews를 끕니다. 이 기능을 켜 두면
   `.github/workflows/codex-review.yml`의 Draft·라벨 조건과 별개로 Codex가 리뷰를 시작할
   수 있습니다.
3. 같은 GitHub 계정으로 이 저장소 하나에만 접근하는 fine-grained personal access token을
   만듭니다. Repository permissions에서는 `Pull requests: Read and write`만 추가합니다.
4. 토큰을 저장소 Actions secret `CODEX_REVIEW_TOKEN`으로 등록합니다. 토큰 값은 저장소
   파일, pull request 본문이나 로그에 기록하지 않습니다.
5. 저장소에 `skip-codex-review` 라벨을 만듭니다.

Actions가 작성한 기본 봇 댓글은 Codex를 호출할 GitHub 사용자로 인증되지 않을 수
있습니다. 따라서 workflow는 `GITHUB_TOKEN` 대신 Codex에 연결된 사용자 계정의 제한된
토큰으로 정확히 `@codex review` 코멘트를 작성합니다. `pull_request_target` 이벤트는
repository secret을 사용할 수 있으므로, workflow에서 pull request 코드를 checkout하거나
실행하지 않습니다.

## 검증

1. Draft pull request를 만들고 Actions에서 `Request Codex review` job이 skipped인지
   확인합니다.
2. Draft에 `skip-codex-review` 라벨을 붙인 뒤 Ready for review로 전환하고, job이
   skipped이며 `@codex review` 코멘트가 생성되지 않았는지 확인합니다.
3. 라벨이 없는 별도 pull request를 Open 상태로 만들고, workflow가 연결된 사용자 명의로
   `@codex review` 코멘트를 하나 작성하는지 확인합니다.
4. Codex가 코멘트에 반응하고 한국어 리뷰 또는 문제가 없다는 반응을 남기는지 확인합니다.

workflow가 `CODEX_REVIEW_TOKEN is not configured`로 실패하면 Actions secret을 확인합니다.
코멘트는 작성되었지만 Codex가 반응하지 않으면 토큰 소유자의 GitHub 계정이 Codex에 연결되어
있는지와 저장소의 Code review가 활성화되어 있는지 확인합니다.
