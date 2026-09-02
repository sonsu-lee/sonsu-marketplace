# 0004 Keep Research Independent and Providers Optional

- Status: Accepted
- Date: 2026-09-02
- Supersedes: None
- Superseded by: None
- Naming note: 이 문서의 `Superpowers`는 [0005](0005-rename-superpowers-to-engineering.md)에서 `Engineering`으로 이름이 변경되었습니다.
- Approval: 사용자가 2026-09-02 현재 대화에서 이 설계와 커밋을 명시적으로 승인했습니다.

## Context

Research는 여러 외부 출처를 찾아 교차 검증하고, 상충하는 근거를 정리하는 조사 방법을
제공합니다. Superpowers의 설계·계획·구현 과정에서도 이런 조사가 필요할 수 있지만, 모든 개발
작업에 외부 조사가 필요한 것은 아닙니다. 두 플러그인 중 하나만 설치한 환경에서도 각자의 핵심
기능이 동작해야 합니다.

Exa와 Perplexity 같은 전문 provider는 검색 범위, 최신성 또는 인용 작성에 도움을 주지만 항상
설치되거나 인증되어 있지는 않습니다. 특정 provider를 필수 의존성으로 만들면 사용할 수 있는
일반 web·browser·local 도구가 있어도 Research 전체가 시작되지 못하거나, 설치와 인증이 사용자의
의도와 무관하게 변경될 수 있습니다.

## Decision

Research를 Superpowers와 분리된 독립 플러그인으로 유지합니다. 두 플러그인의 manifest에 서로의
dependency를 선언하지 않고, 한 플러그인의 지침에서 다른 플러그인의 특정 skill ID를 필수로
호출하지 않습니다. Codex는 설치된 스킬의 description과 요청의 직접 목적을 바탕으로 runtime에
필요한 스킬을 선택합니다.

직접적인 다중 출처 조사, 사실 검증과 문헌 검토는 Research가 단독으로 처리할 수 있습니다.
설계·계획·구현 중 외부의 다중 출처 근거가 결과를 좌우하면 Superpowers가 작업 흐름을 유지하면서
Research의 조사 결과를 받아 다음 결정과 구현에 반영합니다. local debugging, 단순한 repository
탐색과 하나의 공식 문서에서 답을 찾는 조회에는 Research를 기본적으로 선택하지 않습니다.

Exa, Perplexity와 그 밖의 전문 provider는 선택 사항입니다. 현재 노출되고 사용할 수 있는
provider를 선택하되, 없으면 generic web·browser·local 기능으로 조사합니다. Research는 provider
plugin이나 도구를 자동으로 설치·연결·인증하지 않습니다.

Codex나 호스트가 관리하는 provider는 읽기 전용 도구 노출, 현재 schema와 인증된 호출 가능
상태로 자격을 판단하며 plugin README 선언이나 환경 변수를 요구하지 않습니다. 사용자가 직접
구성한 API·CLI adapter에는 이 플러그인의 opt-in 선언, secret 값이 아닌 존재 여부, 실제 읽기
전용 도구·schema·인증을 모두 확인하는 별도 gate를 적용합니다.

## Alternatives Considered

- Research를 Superpowers 안에 포함: 개발 흐름과 조사는 한곳에서 관리할 수 있지만 Research만
  필요한 사용자도 Superpowers를 설치해야 하고 두 upstream의 변경 경계가 섞입니다.
- Superpowers가 `research:research`를 직접 필수 호출: 실행 순서는 명확하지만 Research가 없는
  환경에서 Superpowers의 독립성이 깨지고 skill 이름 변경에도 강하게 결합됩니다.
- Exa 또는 Perplexity를 필수 provider로 지정: 결과 품질을 일정하게 맞추기 쉽지만 인증되지 않은
  환경에서 Research를 사용할 수 없고 provider 선택권도 줄어듭니다.
- Research에 Exa·Perplexity MCP나 CLI를 함께 배포: 설치 직후 경로는 고정할 수 있지만 사용자가
  선택하지 않은 외부 연결과 인증 정책을 플러그인에 결합하고 관리형 연결도 중복하게 됩니다.
- 별도 orchestrator 플러그인으로 조합: 복잡한 고정 흐름을 표현할 수 있지만 현재 필요한
  description 기반 조합보다 설치와 유지 관리가 복잡합니다.

## Consequences

Research만 설치한 환경에서는 조사와 근거 보고를 끝까지 수행할 수 있고, Superpowers만 설치한
환경에서는 기존 개발 흐름이 유지됩니다. 둘을 함께 설치하면 외부 근거가 필요한 구간에서만
Research를 조합할 수 있습니다. Fluent Languages 같은 출력 문체 스킬도 이 책임과 독립적으로
적용할 수 있습니다.

전문 provider가 없는 환경에서는 검색 범위나 속도가 달라질 수 있습니다. 이 차이가 현재성,
완전성, 독립성이나 결론에 실제로 영향을 줄 때에는 확인하지 못한 내용과 근거의 한계를
밝힙니다. description 경계와 provider fallback은 repository-level 라우팅 사례와 실제 사용
결과로 계속 검토해야 합니다.

## Revisit When

Superpowers와 Research 사이의 누락 또는 중복 선택이 실제 작업에서 반복될 때, Codex가 공식적인
plugin dependency·orchestration 계약을 제공할 때, generic fallback으로 필요한 근거를 반복해서
확보하지 못할 때, 또는 특정 provider가 모든 지원 환경의 필수 기반으로 확정될 때 재검토합니다.
