# PR 티켓 연결 규칙

PR에서 GitHub Issues 또는 Linear 티켓을 참조하거나 상태 효과를 의도할 때 읽는다.

## 공통 모델을 만든다

각 티켓을 다음 정보로 정규화한다.

```text
provider: github | linear
key: #123 | owner/repository#123 | ENG-123
url: 확인된 URL
scope: repository | workspace/team
intent: complete | contribute | relate | suppress
source: user | document | tracker | pr-title | pr-body | commit | branch
verified: true | false
canonical: true | false
link_channel: body | title | provider-link | existing-branch
status_effect: close | workflow-dependent | none | unknown
```

provider와 canonical ticket은 사용자의 명시, 승인된 티켓 문서, 실제 tracker 조회, URL과 저장소 integration 설정 순서로 확인한다. `ENG-123`처럼 key 문자열 모양만으로 provider나 실제 티켓을 확정하지 않는다.

같은 작업이 GitHub Issues와 Linear 사이에 동기화되어 있으면 기준 티켓 하나에만 completion 의도를 적용한다. 실제 sync 관계를 확인하지 못한 티켓은 자동으로 같은 작업이라고 묶지 않는다.

`intent`는 PR이 티켓과 맺는 의미이고 `status_effect`는 provider와 현재 automation이 실제로 만들 결과다. 둘을 같다고 가정하지 않는다. PR 게시 전에 저장소·team의 현재 integration, event mapping과 티켓 상태를 읽는다.

## PR 본문에서만 연결한다

연결 채널은 PR 본문이다. 연결을 위해 PR 제목이나 branch 이름에 ID를 추가하지 않는다. 사용자가 요청하고 provider가 지원하는 별도 link 작업은 본문 연결에 더해서만 수행한다.

이미 존재하는 branch 문자열은 가장 낮은 신뢰도의 hint다. ID가 없다는 이유로 PR을 막지 않고, ID가 있어도 canonical ticket으로 확정하지 않는다. 이미 있는 ID가 의도하지 않은 자동 연결을 일으킬 가능성만 검사한다. branch 생성·rename은 수행하지 않는다.

## 티켓 ID에 링크를 건다

본문의 티켓 ID는 클릭해서 티켓으로 이동할 수 있어야 한다. URL은 tracker 조회 결과, 사용자가 준 URL, 승인된 문서의 URL 중 확인한 것을 쓴다. slug 없는 `https://linear.app/<workspace>/issue/ENG-123`도 된다. ID만 있고 URL을 확인할 수 없으면 workspace를 추측하지 않고 사용자에게 URL을 요청한다.

- GitHub Issues: `#123`과 `owner/repository#123`은 GitHub가 자동으로 링크하므로 그대로 쓴다.
- Linear: `Part of [ENG-123](https://linear.app/<workspace>/issue/ENG-123)`처럼 magic word 바로 뒤의 ID를 URL로 링크한다.

Linear 문서가 예시로 든 형식은 `magic word + ID`와 `magic word + issue URL`이고 Markdown 링크 형식은 명시하지 않는다. 다만 2026-10-01에 Linear linkback 댓글이 달린 공개 PR을 조사했을 때, ID가 제목·branch·commit에 없고 본문의 `Fixes`·`Closes`·`Resolves`·`Refs`·`Relates to`·`Part of` + `[ID](URL)`로만 나온 독립 사례 11건이 모두 연결됐다. 같은 Markdown 링크라도 magic word가 없으면 연결되지 않았다. linkback으로는 closing·non-closing 구분까지 확인할 수 없으므로, 게시 뒤 canonical ticket을 다시 읽어 연결과 상태를 확인하는 [결과 확인](#status-effect를-판정한다) 절차는 그대로 적용한다.

## GitHub Issues

PR body를 기본 채널로 사용한다. closing keyword는 PR이 저장소 default branch를 대상으로 할 때만 연결과 merge 후 종료 효과를 가진다.

| 의도 | 표현 | 효과 |
| --- | --- | --- |
| `complete` | `Closes #123` 또는 `Fixes owner/repository#123` | default branch 대상에서 close |
| `contribute` | `Part of #123` | 일반 reference, 자동 close 아님 |
| `relate` | `Related to #123` | 일반 reference, 자동 close 아님 |

non-default base에서는 PR 본문의 closing keyword가 무시되므로 자동 연결이나 종료를 주장하지 않는다. default branch에 합쳐지는 commit message의 closing keyword도 issue를 닫을 수 있으므로 부분 PR의 포함 commit을 확인한다. GitHub Development sidebar 연결은 사용자가 요청한 별도 원격 동작으로 취급한다. branch에 issue 번호를 넣도록 요구하지 않는다.

Draft PR 생성은 GitHub Issue나 Project item의 review 시작을 뜻하지 않는다. merge가 release·deployment 전 단계일 뿐인 티켓에는 closing keyword를 사용하지 않고 `contribute` 또는 `relate`로 표현한다.

공식 참고: [GitHub의 PR과 issue 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

## Linear

PR body의 magic word로 기여·완료 의도를 명시한다. 연결을 위해 새 branch 이름이나 PR 제목에 ID를 넣지 않고, PR 단계에서 기존 branch에 ID를 추가하거나 이름을 바꾸지 않는다.

| 의도 | 표현 | 효과 |
| --- | --- | --- |
| `complete` | `Fixes ENG-123` | configured merge automation 적용 가능 |
| `contribute` | `Part of ENG-123` | 연결하지만 merge completion은 적용하지 않음 |
| `relate` | `Related to ENG-123` | 관계만 표시하고 상태를 바꾸지 않음 |
| `suppress` | `Ignore ENG-123` | 해당 ID의 자동 연결을 막음 |

표의 `ENG-123`에는 [링크 규칙](#티켓-id에-링크를-건다)을 적용한다. `Ignore`는 연결을 막는 표현이므로 링크를 걸지 않는다.

`part of`는 두 단어다. branch에 Linear ID가 있으면 PR body의 비종결·종결 의도와 실제 Linear 관계가 일치하는지 확인한다. commit linking이 활성화된 경우에는 포함 commit의 magic word도 별도 연결·완료 신호로 검사한다. 여러 PR 중 일부만 완료하는 PR이 `Closes` 관계로 반영되거나 관계를 확인할 수 없으면 Ready 진행을 보류하고 결과를 보고한다. 원하지 않는 ID가 branch에 있으면 rename하지 않고 `Ignore ENG-123`가 필요한지 판단한다. 여러 ID에 모두 `Fixes`를 붙이지 않는다.

Linear의 drafted, opened, review requested, ready for merge와 merged event mapping은 team·저장소 설정에 따라 다르다. `Part of`는 merge 완료 전이를 억제하지만 다른 PR 이벤트의 상태 전이는 적용될 수 있다. 부분 PR을 게시하거나 Ready로 전환하기 전에 실제로 발생할 이벤트와 그 목표 상태를 티켓의 남은 작업에 대조한다. Draft 생성·Open·Ready 등의 이벤트가 완료 상태로 옮기도록 설정됐다면 그 이벤트를 일으키는 게시·전환을 보류하고 설정 충돌을 보고한다. Draft PR 자체를 review 시작으로 해석하거나, configured mapping과 같은 status를 직접 중복 적용하지 않는다. merge 뒤 release·deployment가 완료 조건이면 `Fixes` 대신 completion을 만들지 않는 intent를 사용한다.

공식 참고: [Linear GitHub integration](https://linear.app/docs/github)

## status effect를 판정한다

부분 PR을 준비할 때는 PR 본문뿐 아니라 제목, source branch와 대상 base, 포함될 commit message의 티켓 키·종료 표현을 함께 확인한다. 현재 연동 설정에서 게시·Ready·merge 등의 이벤트가 티켓을 완료 상태로 옮기는지 확인한다. 기존 branch·commit을 이 스킬에서 변경할 수 없거나 이벤트 자동화와 충돌하면 해당 게시·전환을 보류하고 필요한 별도 Git 작업이나 자동화 조정을 보고한다.

PR 생성·review 요청·ready·merge·decline·deployment 같은 event마다 다음 순서로 판단한다.

1. 해당 event의 native integration 또는 automation과 정확한 status mapping이 확인되면 그 자동화를 단일 소유자로 둔다.
2. PR과 canonical ticket을 다시 읽어 link와 status를 별도로 확인한다.
3. 비동기 실행 여부가 불명확하면 `status_effect: unknown`으로 보고하고 직접 transition하지 않는다.
4. automation 부재 또는 이 event의 비적용, 현재 상태, 정확한 목표 transition과 권한이 확인되고, 전이 근거가 직접 사용자 의도 또는 확인된 저장소·team lifecycle 정책일 때만 직접 lifecycle fallback을 넘긴다.

프로바이더 reference가 저장됐다는 사실은 `link: applied`일 수 있지만 상태가 바뀌었다는 증거는 아니다. 반대로 상태 automation이 실행됐더라도 기대한 reference가 저장됐는지는 따로 검증한다. Draft PR은 명시적인 review 요청 event가 아니며, release·deployment가 완료 조건이면 merge만으로 `complete`를 주장하지 않는다.
