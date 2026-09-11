# Codex 도구 참고

현재 노출된 도구와 입력 스키마를 확인하고 [공통 실행 계약](agent-execution.md)을 적용한다.
사용자 또는 적용되는 프로젝트·스킬 지침이 요청한 범위에서 위임한다. 도구 존재나 `ultra`
선택 자체가 위임 권한은 아니다.

## 세션 생성·재개·대기

- `spawn_agent`가 `fork_turns: "none"`을 지원하면 독립 리뷰에 사용한다. `"all"`은 전체
  이력을 전달할 수 있고 모델·추론 수준 재정의와 함께 사용할 수 없는 경우가 있다. 현재
  스키마의 허용 조합을 따른다.
- 같은 작업의 집중 수정은 지원되는 `followup_task`로 재개한다. 새 구현자가 필요하면
  현재 계약·고정 근거·미해결 지적·실패한 접근·남은 예산을 전달한다. 회차와 문맥 선택은
  공통 실행 계약을 따른다.
- 완료 이벤트와 실제 상태를 확인한다. `close_agent` 등 현재 없는 종료 도구를 만들지 않으며
  완료된 에이전트의 실행 슬롯 관리는 현재 실행 환경에 맡긴다.
- 독립적인 로컬 작업이 남아 있으면 먼저 수행한다. 기다릴 일만 남으면 `wait_agent` 같은
  이벤트 대기를 사용하고, 대기 시간·진행 알림은 현재 상위 지침의 한도를 따른다. 변화 없는
  상태를 짧게 반복 조회하지 않는다. 상태 확인이 필요할 때 `list_agents`로 대조한다.

## 설정과 관측

사용자 요청이나 적용되는 지침에 모델 지정이 없으면 지원되는 상속·기본값을 유지한다.
역할상 설정을 바꾸는 경우 현재 허용 모델과 추론 수준, 상속 조합을 확인한다. 설정의
`model_reasoning_effort`와 생성 도구의 `reasoning_effort`는 서로 다른 입력 이름이다.
설정 파일·역할 파일·호출 옵션의 우선순위도 해당 버전에서 확인한다.

도구에 필드가 없으면 제공된 역할·프리셋·기본값 중 계약을 충족하는 방식을 사용한다.
명시적 재정의가 지원되지 않는 대안은 `routing_fallback: tool-schema-no-explicit-overrides`로
기록할 수 있다. 요청값과 실제 실행 메타데이터를 구분하며 관측할 수 없으면 `unknown`으로
남긴다. 필수 기능·사용자 모델 제약을 충족할 수 없을 때 해당 실행을 `blocked`로 반환한다.

아래는 과거 로컬 확인 내용이며 현재 모든 Codex 환경의 설정 계약은 아니다.

- CLI 0.152.1의 `features --help`는 `--enable multi_agent`와
  `-c features.multi_agent=true`가 동등함을 안내했다.
- 당시 `features list`에서는 `agents.enabled=false/true`만 바꿔도 기존 활성 상태가 유지됐고,
  `features.multi_agent=false/true`는 각각 false/true로 관측됐다. 2026-09-06 공식 문서의
  `[agents] enabled = true` 안내와 구분해 기록한 결과다.
- `agents.max_concurrent_threads_per_session`은 CLI 0.152.1에서 지원을 확인했으며 주 에이전트를
  제외한다. 0.144.0-alpha.4 스키마는 해당 키를 포함하지 않는다. 최초 지원 버전이라는 뜻은 아니다.

```toml
[features]
multi_agent = true
```

사용자가 설정 변경을 요청한 경우에만 설치 버전의 지원 여부와 실제 효과를 확인해 적용한다.
사용자 지정 역할 파일 위치는 `~/.codex/agents/` 또는 `.codex/agents/`이며, 현재 스키마가
지원하는 경우에 사용한다. 작업마다 설정 변경이나 승인을 새로 요구하지 않는다.

근거: [공식 설정과 우선순위](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents),
[0.144.0-alpha.4 설정 스키마](https://github.com/openai/codex/blob/rust-v0.144.0-alpha.4/codex-rs/core/config.schema.json).

## 역할별 모델 선택 참고

아래는 역할에 따라 설정을 선택할 때의 잠정 운영값이다. 현재 허용 목록과 사용자 지정을
우선하며 측정으로 보장된 최적 조합으로 취급하지 않는다. 정확한 문자열·경로·메타데이터
변환과 Fast Path 판정·구현은 조정자의 결정론적 도구를 기본으로 한다.

| 역할 | 선택 후보 | 추론 수준 |
| --- | --- | --- |
| 좁은 탐색·명확한 작은 구현·국소 수정·기계적 재리뷰 | `gpt-5.6-luna` | `medium` |
| 탐색 정리·일반 작업 리뷰 | `gpt-5.6-terra` | `medium` |
| 계약이 분명한 여러 모듈·상태·복구·파일시스템 통합 구현과 디버깅 | `gpt-5.6-terra` | `high` |
| 요구 해석·해법 선택이 모호한 구현·디버깅 | `gpt-5.6-sol` | `medium`, 복잡한 논리·경계는 `high` |
| 영향 큰 설계·계획·어려운 원인 판단 | `gpt-5.6-sol` | `high` |
| 일반 전체 변경 리뷰 | `gpt-5.6-sol` | `medium`, 복잡한 논리·경계는 `high` |
| 독립 red-team | `gpt-5.6-sol` | `high` |
| 여러 시스템·도구·단계를 연결하며 지속적인 판단이 필요한 가장 어려운 작업 | `gpt-6-astra` | `medium`, 깊은 경계 검증은 `high` |

모델·추론 수준·역할 구성을 따로 선택한다. 파일 수보다 불확실성·실패 비용·재탐색·도구 왕복·
재작업을 포함한 총 완료 비용을 본다. 특정 모델들을 순서대로 거치거나 수정 회차만으로
상향할 필요는 없다. `low`는 명확한 조회·추출, `xhigh`·`max`는 추가 분석의 실익이 있는 어려운
문제에서 비교할 수 있다. `ultra`도 실제 호스트 지원, 위임 권한과 동시수·재위임 제한을
별도로 확인한다. 같은 추론 수준 이름이 다른 모델에서 같은 품질·계산량을 뜻하지 않는다.

작업 요약은 Luna에 좁은 입력·기대 결과·반환 조건, Terra에 담당 범위·근거·인계 지점,
Sol에 목표·선택의 장단점·완료 조건, Astra에 승인 작업의 지속·질문 조건·허용 위임 범위·검증
종료 조건을 분명히 제공한다. 이는 별도 전용 프롬프트의 검증 결과가 아닌 운영 권고다.

기존 소규모 실험은 Sol 제외나 모든 리뷰의 `high` 강제를 뒷받침하지 않았다. 공식 안내,
로컬 관찰과 미검증 선택은 [ADR 0012](../../../../../docs/decisions/0012-use-role-routing-and-execution-evidence.md)에
구분돼 있다. 출처의 모델 목록을 현재 도구의 허용 목록으로 대체하지 않는다.

공식 참고: [모델·추론 수준](https://learn.chatgpt.com/docs/models),
[GPT-5.6 프롬프트 가이드](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6),
[Astra 프롬프트 가이드](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices).

## Code Mode

`functions.exec` 또는 동등한 JavaScript 실행 도구가 있으면 독립적인 읽기·검색·파싱·생성·
검증을 한 호출에서 구성할 수 있다. 의존 작업과 수정은 순서를 유지하며 현재 파일 편집·
권한 규칙을 적용한다. 이 실행 방식 자체는 Fast Path 자격이나 품질 통과 근거가 아니다.

기계적 변환은 전체 참조를 먼저 확인하고, 변경 뒤 기존 패턴 잔여·예상 밖 패턴·무관한 변경을
검사한다. 구문·파서와 실제 소비자가 쓰는 최소 빌드·테스트·로더를 결과 조건으로 삼는다.
계약·권한·의존 경계 변경처럼 의미 판단이 필요한 작업은 해당 절차로 분류한다.

## Goal 도구

사용자가 goal 사용을 명시적으로 요청할 때만 만든다. 구현 계획이 있는 작업은 상위 goal
하나와 기존 세부 작업 기록으로 추적한다. 토큰 예산은 사용자가 숫자로 명시한 경우에만 설정한다.

계획의 목표와 사용자 관찰 결과를 연결하고, red-team 묶음에는 원래 목표를 포함한다.
필수 검증·일반 최종 리뷰·red-team까지 충족한 뒤 `complete`로 갱신한다. 상한·시간·토큰 소진은
완료 근거가 아니다. `blocked`는 현재 goal 도구가 요구하는 반복 차단 조건을 충족할 때 사용한다.
도구가 없으면 계획과 진행 기록으로 추적하고 도구를 실행한 것으로 보고하지 않는다.

## 작업 공간과 앱 인계

읽기 전용 Git 명령으로 현재 위치를 확인한다.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

`GIT_DIR != GIT_COMMON`이면 이미 연결된 worktree다. `BRANCH`가 비면 detached HEAD이며,
브랜치·push 가능 여부는 실제 호스트 권한과 도구로 따로 확인한다. 각 단계의 처리는
[using-git-worktrees](../../using-git-worktrees/SKILL.md)와
[finishing-a-development-branch](../../finishing-a-development-branch/SKILL.md)를 따른다.

앱이 작업 공간을 관리하면 지원되는 브랜치 생성·로컬 인계 기능을 사용할 수 있다. 현재
도구나 UI에 표시된 동작을 기준으로 하며, staging·commit·push·PR·merge에는 각각 기존
승인 범위가 필요하다. 권한이나 기능이 없으면 검증한 변경을 보존하고 실제 제약을 보고한다.
