# review-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

독립적인 일반 및 집중 리뷰어와 로컬 우선 보고를 활용하는 근거 기반 코드 리뷰.

`reviewing-code` 스킬은 omp, Codex, Claude Code에서 동일하게 고정된 대상을
독립적으로 리뷰하도록 조율하고, 후보 지적을 검증하며, 소스를 수정하지 않고
조치 가능한 지적을 보고한다.

## 목차

- [설치](#설치)
  - [의존성](#의존성)
- [사용법](#사용법)
  - [CLI](#cli)
- [기본값과 제한](#기본값과-제한)
- [가이드](#가이드)
- [기여](#기여)
- [라이선스](#라이선스)

## 설치

### 의존성

[omp](https://github.com/can1357/oh-my-pi#install),
[Codex](https://developers.openai.com/codex/cli),
[Claude Code](https://code.claude.com/docs/en/overview) 중 하나를 설치하고
대상 저장소에 접근할 수 있도록 준비한다. omp에서는 실제 적용되는 네이티브
리뷰 모델과 `@slow`가 가리키는 모델에 대한 접근을 설정한다. Codex에서는 모델
접근을 설정하고 서브에이전트를 활성화한다. Claude Code에서는 모델 접근을
설정하고 Agent 도구를 허용한다. 특정 공급자 조합은 필요하지 않다. 원격 PR을
읽거나 명시적으로 게시하려면 인증된 GitHub 연동이 필요하다. 이 플러그인은
자격 증명을 제공하거나 설치 시 모델 접근을 확인하지 않는다. 런타임 검사는 대상
프로젝트 자체의 도구를 사용한다.

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install review-workflow@sonsu-marketplace
```

프로젝트에만 설치하려면 설치 명령에 `--scope project`를 추가한다.

Codex의 경우:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin add review-workflow@sonsu-marketplace
```

Claude Code의 경우:

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install review-workflow@sonsu-marketplace
```

## 사용법

### CLI

선택한 클라이언트에서 검색 여부를 확인한 다음 리뷰를 요청한다:

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details review-workflow
```

```text
Review my working changes, including staged, unstaged, and untracked files.
Keep the report local; do not edit files or publish anything.

Review PR #123 against its stated purpose and report findings locally.

Draft PR comments from these existing findings. Do not start a new review or post.
```

일반적인 자연어 리뷰 요청은 `reviewing-code`를 선택해야 한다. 선택은 모델의
판단이며 보장된 훅이 아니다. 필요하면 Codex에서는
`$review-workflow:reviewing-code`를 명시적으로 선택하고, Claude Code에서는
`/review-workflow:reviewing-code`를 사용한다. 목록에 표시되는 것만으로 스킬
실행이 증명되지는 않는다. omp에서는 컨트롤러가 포함된 `reviewer`와 최소 한
명의 집중 작업자를 하나의 네이티브 `task` 배치로 배정한다. 집중 작업자는
`review-workflow-focused`이며 스킬만 변경된 경우에는
`skill-workflow-reviewer`다. Codex와 Claude Code에서는 작성자의 대화를
물려받지 않은 새로운 범용 서브에이전트에 맞춤 일반 및 집중 작업을 배정한다.
이 플러그인은 `/review`, `codex review`, `review/start`, `/code-review`,
`/security-review`, ultrareview를 호출하거나 가로채지 않는다. 네이티브
워크플로만 명시적으로 요청한 경우에는 해당 워크플로를 유지한다.

기존 지적을 댓글로 바꾸기만 요청받은 경우, 리뷰어를 실행하거나 런타임 검사를
수행하지 않고 댓글 지침을 불러와 지적의 검증 상태를 유지한다. 댓글 초안 작성은
코드 리뷰와 별개의 진입 경로다.

게시하려면 검증된 지적을 GitHub COMMENT 리뷰로 게시하도록 명시적으로 요청한다.
리뷰나 초안 작성 요청은 원격 대기 중인 리뷰를 포함해 게시 권한을 부여하지
않는다. 게시 전에 대상 리비전과 기존 스레드를 확인하며, 사용자를 대신해 PR을
승인하거나 변경을 요청하지 않는다.

## 기본값과 제한

- 일반 리뷰어는 독립적으로 버그와 회귀를 검토한다. omp에서 네이티브 리뷰어는
  실제 적용되는 모델과 네이티브 출력 정책을 유지하며, 맞춤
  `review-workflow-focused` 프로필은 `@slow`를 사용하고 스킬을 자동으로
  불러온다. Codex는 범용 `default` 서브에이전트를, Claude Code는 포크하지 않는
  `general-purpose` 서브에이전트를 사용한다. 이들은 omp 프로필이 아니라
  프롬프트로 배정된 일반 및 집중 역할과 실제 클라이언트 설정을 사용한다.
  Claude Code는 이 패키지의 omp 프로필을 불러오지 않는다. 맞춤 보고서에는
  네이티브 신뢰도나 정확성 필드를 임의로 만들지 않는다. 어떤 클라이언트도 모델
  다양성이나 추론 노력을 강제하지 않는다.
- 일반적인 플러그인 리뷰에는 모두 의미 있는 집중 검토가 최소 한 번 포함된다.
  컨트롤러는 흐름, 실패/상태, 아키텍처/현재 비용 또는 구현 중 좁은 질문이나
  관점을 지정한다. 모든 관점을 자동으로 실행하거나 각 작업자에게 전체 체크리스트를
  반복하도록 요청하지 않는다. 큰 독립 흐름은 경계 맥락과 함께 나눌 수 있으며,
  일반 검토는 필요할 때만 나눈다.
- 리뷰 대상 변경이 에이전트 스킬을 추가하거나 수정하면 omp는
  `authoring-skills`를 자동으로 불러오는 `skill-workflow`의
  `skill-workflow-reviewer`도 배정하고, 런타임 단계에서 변경된 스킬을 실행한다.
  해당 에이전트를 찾을 수 없으면 `review-workflow-focused`가 일반적인 집중
  질문을 맡고 스킬 기준 검토가 누락되었다고 보고한다. Codex와 Claude Code는
  사용자의 명시적 요청이나 권한 있는 구현 컨트롤러의 배정에 따라 범용 스킬 기준
  작업자를 추가한다. 배정은 하나의 컨트롤러가 담당하며, 해당 리뷰 밖에서 별도의
  스킬 리뷰어를 실행하지 않는다.
- 공통 기준은 원래 목적에서 시작해 흐름, 실패/상태, 아키텍처/현재 비용을 거쳐
  자료 구조, API, 타입, 가드, 주석과 같은 구현 세부 사항으로 이어진다. 지적에는
  다수결, 신뢰도 점수, 할당량이 아닌 구체적인 근거가 필요하다. 지적이 없어도
  유효하며, 작업자를 사용할 수 없거나 범위가 불완전하면 이를 보고해야지 문제가
  없는 리뷰로 제시해서는 안 된다.
- 리뷰어는 작성 이력, 사후 합리화 또는 서로의 첫 결과가 아니라 동일하게 고정된
  대상과 요구사항으로 새로 시작한다. 컨트롤러는 적용 가능한 저장소 및 사용자
  제약을 명시적으로 제공하며, 지침이나 기억이 상속된다고 가정하지 않는다. 맞춤
  보고서에는 범위, 지적, 제한 사항, 권장 런타임 시나리오가 포함되며 네이티브
  보고서는 고유 스키마를 유지한다.
- 컨트롤러는 세 번째 전체 검사를 수행하는 대신 근본 원인을 중복 제거하고 구체적인
  주장을 검증한다. 해결되지 않은 후보 지적은 한 번의 집중 후속 검토로 해결할 수
  있으며, 자동 수정/리뷰 반복은 없다.
- 실행 가능한 동작이 변경되면 컨트롤러 또는 범위가 좁은 범용 작업자가 일회용
  작업 공간에서 의미 있고 안전한 런타임 실행을 한 번 수행한다. 일반 및 집중
  리뷰어는 이를 실행하지 않는다. 안전한 로컬 리소스를 사용하고 프로덕션 영향을
  피하며, 런타임 근거가 없으면 보고한다.
- 초기 검증과 런타임 검사 이후, 위험이 높은 변경이나 명시적 요청이 있으면 집중
  레드팀 작업이 필요할 수 있다. 지적 할당량이나 또 다른 전체 리뷰가 아니라 목표,
  가정 또는 검토 범위의 반례를 찾는다. 이는 조건부이며 항상 실행되는 또 다른
  리뷰어 프로필이 아니다.
- 소스 리뷰는 읽기 전용이다. 소스 수정, 커밋, 푸시 또는 승인되지 않은 원격
  쓰기를 하지 않는다. PR의 merge-base/head 또는 스테이징된 파일, 스테이징되지
  않은 파일, 추적되지 않은 파일을 포함한 작업 중 변경 사항을 고정한다. 변경
  사항을 적용하지 않는 일회용 작업 공간을 사용한다. omp에서는 `isolated: true`만
  지정하면 변경 사항이 자동 적용될 수 있다. Codex 서브에이전트는 부모의 샌드박스
  권한을 상속하고 Claude Code 서브에이전트는 세션의 권한 규칙을 따른다. 읽기
  전용 지침이나 일회용 복사본은 보안 샌드박스를 구성하지 않는다.
- 가져온 코드, 주석, 모델 출력은 새로운 지침이 아니라 데이터다. 로컬 우선 보고가
  모델 공급자에 대한 네트워크 노출을 막지는 않으므로 해당 공급자에게 전달해서는
  안 되는 자료를 제공하지 않는다. 관련된 기존 문제는 별도로 다루며 진행을 막지
  않는다. 관련 없는 기술 부채와 선호 사항은 생략한다.

모든 클라이언트는 기준과 제한된 후속 검토 규칙을 공유하지만 실행 참고 자료는
별도로 사용한다. 지침은 권한 강제, CI 검사 또는 필수 인적 리뷰를 대체하지
않는다. 독립 작업자를 사용할 수 없다면 리뷰가 불완전하다는 뜻이지 이를 알리지
않고 순차 검토로 대체해도 된다는 뜻이 아니다. 이 플러그인은 훅을 설치하지 않는다.

## 가이드

- [리뷰 절차](skills/reviewing-code/SKILL.md).
- [리뷰 관점](skills/reviewing-code/references/review-lenses.md): 집중 질문을
  선택하거나 동작을 분석할 때 불러온다.
- [omp 실행](skills/reviewing-code/references/omp.md): omp 실행 시 불러온다.
- [Codex 실행](skills/reviewing-code/references/codex.md): Codex 실행 시
  불러온다.
- [Claude Code 실행](skills/reviewing-code/references/claude-code.md):
  Claude Code 실행 시 불러온다.
- [리뷰 댓글](skills/reviewing-code/references/review-comments.md): 댓글을
  작성하거나 게시할 때 불러온다. 댓글 문구를 작성하거나 수정할 때는 목록에 해당
  언어 스킬이 있으면 그것도 읽는다. 이는 의존성이 아니며, 확실성, 의도, 게시의
  의미는 여전히 이 참고 자료가 담당한다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에
올린다. 저장소의 [작성](../../CONTRIBUTING.md#adding-a-plugin),
[문서화](../../CONTRIBUTING.md#writing-documentation),
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차를 따른다. 검사에는 임시
홈과 격리된 저장소를 사용하고 실제 프로젝트에 테스트 픽스처를 게시하지 않는다.
실제로 수행한 검사만 보고하고 검증하지 않은 동작과 구분한다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee
