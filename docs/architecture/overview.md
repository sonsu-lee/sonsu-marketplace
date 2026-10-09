# 마켓플레이스 아키텍처

- Status: Current
- Last reviewed: 2026-10-07

## 목적

Sonsu Marketplace는 Codex·Claude Code·omp 플러그인을 한 저장소에서 관리하고, 업스트림 출처와 로컬 변경을
추적하는 마켓플레이스입니다.

## 구성 요소

| 경로 | 책임 |
| --- | --- |
| `.agents/plugins/marketplace.json` | 마켓플레이스 식별자와 제공할 플러그인을 등록 |
| `plugins/<name>/.codex-plugin/plugin.json` | 개별 플러그인의 메타데이터와 구성 요소 진입점 정의 |
| `.claude-plugin/marketplace.json`, `plugins/<name>/.claude-plugin/plugin.json` | Codex 정본에서 생성한 Claude Code 배포 메타데이터 |
| `.omp-plugin/marketplace.json` | omp 기본 6개와 opt-in Worklog 카탈로그. Codex catalog에서 대상만 생성 |
| `plugins/{design,workflow,fluent-korean}/omp/` | 독자 runtime을 포함하지 않는, 생성된 omp 전용 패키지 |
| `plugins/<name>/skills/` | 플러그인이 제공하는 스킬 보관 |
| `plugins/<name>/UPSTREAM.md` | 업스트림 기준 commit, 포함 범위와 로컬 차이 기록 |
| `scripts/` | 공유 정책·연속성 참조 생성 등 저장소 유지보수 도구 |
| `docs/` | 현재 구조, 결정 이유, 요구사항과 운영 절차 보관 |
| `evals/` | 평가 fixture와 검증 도구 |

## 로딩 경계

```text
Codex: 저장소 루트
  → .agents/plugins/marketplace.json
  → source.path
  → plugins/<name>/.codex-plugin/plugin.json
  → skills, hooks와 기타 선언된 구성 요소
Claude Code: 저장소 루트
  → .claude-plugin/marketplace.json
  → plugins/<name>/.claude-plugin/plugin.json
  → skills, hooks와 지원되는 구성 요소
omp: 저장소 루트
  → .omp-plugin/marketplace.json
  → plugins/{workflow,design,fluent-korean,worklog}/omp 또는 plugins/{fluent-english,fluent-japanese,career}
  → skills와 필요한 동봉 자료(opt-in Worklog는 runtime extension도 포함)
```

Codex와 Claude Code는 대부분의 패키지에서 공통 스킬·hook·script를 각자의 로더로 읽습니다.
`memory-manager`와 `worklog`의 정본은 각각 `plugins/<name>/`이며 Claude Code 배포본은 내부
`plugins/<name>/claude/`에 생성합니다. 스킬·script·hook의 수정은 정본에서만 하고
`scripts/render-claude-compat.py`로 배포본을 갱신합니다. Codex 전용 connector 선언은 이식하지 않습니다. 구성과
검증 절차는 [플러그인 개발 가이드](../guides/adding-a-plugin.md)에 있습니다.

omp 기본 구성은 Workflow, Fluent Korean, Fluent English, Fluent Japanese, Design, Career 6개입니다.
작업 로그용 Worklog는 opt-in으로 별도 설치할 수 있습니다([ADR 0022](../decisions/0022-add-worklog-plugin.md)).
개발 실행·task·todo·session·review·메모리는 omp 순정 기능을 쓰며, 커스텀 역할 설정을 추가하지 않습니다.
`scripts/render-omp-compat.py`가 Design·Workflow·Fluent Korean·Worklog의 전용 패키지를 생성합니다.
기본 6개에는 독자 runtime extension, hook, evidence gate, `task-continuity.py`를 배포하지 않습니다.
runtime extension은 opt-in Worklog에만 포함하고, hook은 모든 omp 배포에서 제외합니다.
Fluent Korean은 Codex의 단일 호출 스킬과 참고 자료를 투영하고 현재 호스트 모델을 사용합니다.
Claude Code의 다중 호출·strict 모드와 고정 Opus 에이전트는 omp 배포에 포함하지 않습니다.
원본 패키지의 Codex·Claude Code용 파일, English·Japanese 스킬, Design의 품질 계약과 프로필,
Workflow의 권한 경계는 유지합니다. 생성된 연속성 자료는 `.sonsu`에 쓰지 않고 omp 순정 todo·session을 안내합니다.
생성물과 설치 캐시는 손으로 편집하지 않습니다.

| omp에서의 책임 | 담당 |
| --- | --- |
| 개발 실행·task·todo·session·review | omp 순정 기능 |
| Git·티켓·PR 작업 권한과 산출물 | Workflow |
| 언어별 문장 품질·보호 규칙 | Fluent Korean·English·Japanese |
| UI·prototype·handoff 품질과 native tool 전제 | Design |
| 경력 원본·지원 서류·면접 준비 | Career |
| 필요할 때 쓰는 조사·제품 탐색·글 구성 | Research·Product·Writing. 기본 배포에 추가하지 않는 선택 후보 |
| 작업 로그 기록·읽기 전용 진단 | Worklog. opt-in으로 별도 설치 |

Engineering의 omp 프로필은 직접 설치해 선택한 legacy 사용자의 gate·실행·독립 리뷰가 참조하므로
보존합니다. 기본 6개 설정에는 쓰지 않으며, 독자 세션 ID 주입이나 Stop hook도 제공하지 않습니다.

`main`에 공개해도 기존 설치에 바로 반영되지는 않습니다. 공개·자동 업데이트 조건과 세션 재시작은
[배포 생명주기](plugin-lifecycle.md)를 참고하세요.

마켓플레이스 등록은 저장소의 파일을 변경하거나 커밋하는 작업과 별개입니다. 호스트에
등록하거나 설치하는 작업도 각각 외부 상태 변경이므로 사용자가 요청한 범위에서만 수행합니다.

플러그인은 책임과 업데이트 경계에 따라 독립적으로 설치됩니다. Engineering은 개발 lifecycle과
코드 shape·단순성·유지보수성·실패 모드·운용 가능성 및 PR 리뷰·통합 결과 게시, Workflow는 Git과
delivery 산출물·PR 상태 조회·복구, Research는 외부 다중 출처 조사, Prompting은 프롬프트 산출물, Fluent Languages는
출력 언어를 담당합니다. Writing은 독자·목적에 맞는 정보 선별, 문서 배치와 글의 구성을 담당합니다.
Memory Manager는 명시적으로 호출하는 에이전트 메모리 점검·정리를
담당하며 저장 방식과 수정 권한은 대상 호스트의 계약을 따릅니다. Product는 제품 기회·문제·근거·도메인 규칙·검증과 PRD 변환을,
[Design](design.md)은 일반·운영 웹·앱 화면의 신규 설계·재설계·감사를 하나의 플러그인에서 담당합니다.
Figma를 사용하는 경우 native 화면·prototype과 handoff 품질을 확인하고, 코드 이전에는 해당 결과의 명시적 허가를 받습니다.
Figma가 정본이 아니면 기존 앱에 직접 구현합니다. 운영 업무 계약은 필요할 때 내부 참고 자료로 적용합니다.
Design Patterns는 실제 설계 forces와 필요한 guarantee에 근거한 named pattern 선택과 기존 적용의
읽기 전용 검토를 담당합니다. 전체 개발 lifecycle이나 broad code quality review는 소유하지 않습니다.
Career는 개발자 이직을 위한 경력 원본 정리, 미국식 resume·履歴書·職務経歴書 작성과 면접 준비·모의면접·회고를 담당합니다.
Figma canvas의 agent mutation은 registered official Figma MCP가 단독으로 소유하고, companion은
사용자가 Desktop에서 직접 실행합니다. 한 요청에서 여러 책임이 필요하면 runtime이 설치된 스킬을
조합하며 manifest dependency나 공통 router를 전제하지 않습니다.
세부 책임과 함께 적용하는 방식은 [스킬 라우팅](skill-routing.md)에서 관리합니다.

단일 upstream fork뿐 아니라 Engineering으로 이동한 품질 자료처럼 여러 source를 합성한 영역도 원본을
별도 baseline commit에 byte-for-byte로 보존한 뒤 최종 경로로 이동해 수정합니다. 현재 파일의
출처는 `UPSTREAM.md`의 source·baseline·final mapping으로 추적합니다.

## 문서 경계

현재 구조는 이 디렉터리에서 갱신하고, 선택의 이유와 대안은
[`decisions/`](../decisions)에 보존합니다. 구현 계획은 장기간 유지할 아키텍처 지식과
구분하며 기본적으로 `docs/` 밖에서 관리합니다.
