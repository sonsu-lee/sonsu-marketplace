# 0005 Rename the Local Superpowers Fork to Engineering

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None
- Approval: 사용자가 2026-09-02 현재 대화에서 `Engineering` 이름과 적용을 명시적으로 승인했습니다.

## Context

이 마켓플레이스는 `obra/superpowers` v6.3.0을 기준으로 가져온 뒤 문서 라우팅, 계획 저장,
Git 승인, TDD 적용 범위, subagent 실행과 branch 완료 절차를 로컬 정책에 맞게 변경했습니다.
계속 `Superpowers`라는 공개 이름을 사용하면 이 로컬 fork와 공식 upstream 배포본을 구분하기
어렵고, 현재 책임도 이름에서 드러나지 않습니다.

마켓플레이스에는 Git·ticket·pull request 산출물을 담당하는 Workflow, 다중 출처 조사를
담당하는 Research와 출력 언어를 담당하는 Fluent Languages가 별도로 있습니다. 이름을 바꿔도
이 독립성과 runtime 조합 경계는 유지해야 합니다.

## Decision

로컬 플러그인의 공개 표시 이름을 `Engineering`, 플러그인 ID와 디렉터리를 `engineering`과
`plugins/engineering/`으로 변경합니다. bootstrap skill은 `using-engineering-skills`, 내부 skill
참조는 `engineering:*` namespace를 사용합니다. `brainstorming`, `writing-plans`,
`systematic-debugging` 같은 개별 skill 이름은 역할이 명확하므로 유지합니다.

Engineering은 개발 작업을 분석하고 계획하고 구현하고 디버깅하고 검증하고 리뷰하는 방법을
담당합니다. 직접적인 branch·commit·ticket·push와 pull request 산출물은 Workflow, 외부의 다중
출처 근거 조사는 Research, 결과 표현은 Fluent Languages가 담당합니다. 어느 플러그인도 다른
플러그인의 설치를 필수로 가정하지 않습니다.

로컬 manifest에는 로컬 fork의 배포·유지관리 주체를 표시합니다. 원본 이름, 저작권, 기준 commit과 repository는
`LICENSE`와 `UPSTREAM.md`에 유지하여 Engineering을 공식 Superpowers 배포본으로 오인하지 않게
합니다. 이전 ADR에서 사용하는 `Superpowers`는 당시 로컬 플러그인의 이름이며, 이 결정 이후의
현재 아키텍처와 평가 자료에서는 `Engineering`을 사용합니다.

`.superpowers/` scratch 경로와 `SUPERPOWERS_DISABLE_TELEMETRY`는 기존 plan, ledger, brainstorming
session과 사용자 설정의 호환성을 위해 유지합니다. 새 `ENGINEERING_DISABLE_TELEMETRY`도 같은
opt-out으로 지원합니다. 선택적인 visual companion은 Engineering 이름을 표시하되, telemetry가
활성화된 경우에만 기존 upstream Prime Radiant 이미지를 출처 링크와 함께 사용합니다.

## Alternatives Considered

- `Development Playbook` 또는 `dev-playbook`: 실행 지침 모음이라는 의미는 정확하지만, 개인용
  마켓플레이스의 다른 기능 중심 이름보다 길고 문서 모음으로 읽힐 수 있습니다.
- `Sensible Engineering`: 비례적인 검증이라는 로컬 철학은 드러나지만 `sensible`이 주관적인
  자기평가로 보일 수 있습니다.
- `Engineering Practices`: 여러 방법의 집합이라는 뜻은 분명하지만 조직 규정이나 정적인
  모범 사례 문서처럼 들릴 수 있습니다.
- `Sonsu Superpowers`: upstream 계보는 쉽게 알 수 있지만 로컬 fork와 공식 배포본의 정체성을
  계속 결합합니다.

## Consequences

설치 식별자가 바뀌므로 기존 `superpowers`와 새 `engineering`을 동시에 설치하면 동일한 skill이
중복 노출될 수 있습니다. 설치 시 기존 플러그인을 제거하고 새 ID를 사용해야 합니다. marketplace,
문서, skill 간 참조와 routing fixture도 새 ID와 namespace를 기준으로 유지합니다.

upstream 갱신 시에는 `plugins/engineering/`을 원본 `plugins/superpowers/`와 경로가 다른 fork로
비교해야 합니다. `UPSTREAM.md`의 pinned commit과 import commit을 기준으로 원본 변경과 로컬
변경을 계속 분리합니다.

호환성 경로에 원본 이름이 남으므로 문자열 검색만으로 rename 완료를 판단할 수 없습니다.
현재 공개 정체성, 의도적인 upstream provenance와 호환성 표면을 구분해서 검토해야 합니다.

## Revisit When

이 플러그인을 개인용 마켓플레이스 밖에 배포하여 더 고유한 이름이 필요할 때, Codex가 plugin ID
alias나 migration 계약을 제공할 때, 또는 `.superpowers/` 경로와 환경 변수를 안전하게 이전할 수
있는 호환성 정책을 마련했을 때 이름과 legacy surface를 다시 검토합니다.
