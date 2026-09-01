# PR 티켓 연결 규칙

PR에서 GitHub Issues, Linear 또는 Jira 티켓을 참조하거나 상태 효과를 의도할 때 읽는다.

## 공통 모델을 만든다

각 티켓을 다음 정보로 정규화한다.

```text
provider: github | linear | jira
key: #123 | owner/repository#123 | ENG-123 | PROJ-123
url: 확인된 URL
scope: repository | workspace/team | Jira site/project
intent: complete | contribute | relate | suppress
source: user | document | tracker | pr-title | pr-body | commit | branch
verified: true | false
canonical: true | false
link_channel: body | title | provider-link | existing-branch
status_effect: close | workflow-dependent | none | unknown
```

provider와 canonical ticket은 사용자의 명시, 승인된 티켓 문서, 실제 tracker 조회, URL과 repository integration 설정 순서로 확인한다. `ENG-123`처럼 Linear와 Jira가 모두 사용할 수 있는 문자열 모양만으로 provider를 정하지 않는다.

같은 작업이 GitHub Issues와 Linear 사이에 동기화되어 있으면 canonical ticket 하나에만 completion 의도를 적용한다. 실제 sync 관계를 확인하지 못한 티켓은 자동으로 같은 작업이라고 묶지 않는다.

## PR metadata를 우선한다

연결 채널은 Git history와 branch naming에 미치는 결합도가 낮은 순서로 고른다.

1. provider가 지원하는 PR body 문법
2. body로 부족할 때 PR title
3. 사용자가 요청하고 provider가 지원하는 별도 link operation
4. 이미 존재하는 branch ID
5. branch 생성·rename은 수행하지 않고 별도 Git workflow로 넘김

branch 문자열은 가장 낮은 신뢰도의 hint다. ID가 없다는 이유로 PR을 막지 않고, ID가 있어도 canonical ticket으로 확정하지 않는다. 이미 있는 ID가 의도하지 않은 자동 연결을 일으킬 가능성만 검사한다.

## GitHub Issues

PR body를 기본 채널로 사용한다. closing keyword는 PR이 repository default branch를 대상으로 할 때만 연결과 merge 후 종료 효과를 가진다.

| 의도 | 표현 | 효과 |
| --- | --- | --- |
| `complete` | `Closes #123` 또는 `Fixes owner/repository#123` | default branch 대상에서 close |
| `contribute` | `Part of #123` | 일반 reference, 자동 close 아님 |
| `relate` | `Related to #123` | 일반 reference, 자동 close 아님 |

non-default base에서는 closing keyword가 무시되므로 자동 연결이나 종료를 주장하지 않는다. GitHub Development sidebar 연결은 사용자가 요청한 별도 원격 동작으로 취급한다. branch에 issue 번호를 넣도록 요구하지 않는다.

공식 참고: [GitHub의 PR과 issue 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

## Linear

PR body의 magic word를 기본 채널로 사용한다. title의 ID는 repository 관례나 사용자의 명시가 있을 때만 사용한다.

| 의도 | 표현 | 효과 |
| --- | --- | --- |
| `complete` | `Fixes ENG-123` | configured merge automation 적용 가능 |
| `contribute` | `Part of ENG-123` | 연결하지만 merge completion은 적용하지 않음 |
| `relate` | `Related to ENG-123` | 관계만 표시하고 상태를 바꾸지 않음 |
| `suppress` | `Ignore ENG-123` | 해당 ID의 자동 연결을 막음 |

`part of`는 두 단어다. 기존 branch에 Linear ID가 있으면 사용자가 원하는 티켓과 관계 의도에 맞는지 확인한다. 원하지 않는 ID가 branch에 있으면 rename하지 않고 `Ignore ENG-123`가 필요한지 판단한다. 여러 ID에 모두 `Fixes`를 붙이지 않는다.

공식 참고: [Linear GitHub integration](https://linear.app/docs/github)

## Jira

Jira development information에는 PR title의 work item key를 기본 채널로 사용한다. repository 관례에 맞춰 `PROJ-123: title` 또는 `[PROJ-123] Title`처럼 key를 포함하고, body에는 확인된 Jira URL과 관계를 기록할 수 있다.

branch나 commit의 기존 key는 보조 evidence다. key가 없어도 branch를 rename하거나 commit을 rewrite하지 않는다. title에도 key를 넣을 수 없으면 body URL은 사람이 읽는 reference일 뿐 integration을 보장하지 못할 수 있음을 보고하고, branch 정책은 별도 Git workflow 결정으로 남긴다.

Jira 상태 전이는 site의 workflow trigger와 automation 설정에 따라 달라진다. title에 key를 넣거나 `Fixes PROJ-123`라고 썼다는 이유만으로 종료를 주장하지 않는다.

공식 참고: [GitHub development information을 Jira에 연결](https://support.atlassian.com/jira-cloud-administration/docs/use-the-github-for-jira-app/)
