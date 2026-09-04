# 마켓플레이스 아키텍처

- Status: Current
- Last reviewed: 2026-09-03

## 목적

Sonsu Marketplace는 개인적으로 사용하는 Codex 플러그인을 한 저장소에서 등록하고,
업스트림 출처와 로컬 정책 변경을 추적하기 위한 로컬 마켓플레이스입니다.

## 구성 요소

| 경로 | 책임 |
| --- | --- |
| `.agents/plugins/marketplace.json` | 마켓플레이스 식별자와 제공할 플러그인을 등록 |
| `plugins/<name>/.codex-plugin/plugin.json` | 개별 플러그인의 메타데이터와 구성 요소 진입점 정의 |
| `plugins/<name>/skills/` | 플러그인이 제공하는 스킬 보관 |
| `plugins/<name>/UPSTREAM.md` | 업스트림 기준 commit, 포함 범위와 로컬 차이 기록 |
| `docs/` | 현재 구조, 결정 이유, 요구사항과 운영 절차 보관 |

## 로딩 경계

```text
저장소 루트
  → .agents/plugins/marketplace.json
  → source.path
  → plugins/<name>/.codex-plugin/plugin.json
  → skills 및 기타 선언된 구성 요소
```

마켓플레이스 등록은 저장소의 파일을 변경하거나 커밋하는 작업과 별개입니다. Codex에
등록하거나 설치하는 작업도 각각 외부 상태 변경이므로 사용자가 요청한 범위에서만 수행합니다.

플러그인은 책임과 업데이트 경계에 따라 독립적으로 설치됩니다. Engineering은 개발 lifecycle,
Quality Engineering은 코드 shape·단순성·유지보수성·실패 모드·운용 가능성, Workflow는 Git과
delivery 산출물, Research는 외부 다중 출처 조사, Prompting은 프롬프트 산출물, Fluent Languages는
출력 언어를 담당합니다. Product는 제품 기회·문제·근거·도메인 규칙·검증과 PRD 변환을,
Figma Workflow는 Figma 제품 화면·prototype의 구조, interaction과 handoff 품질을 담당합니다.
Figma canvas의 agent mutation은 registered official Figma MCP가 단독으로 소유하고, companion은
사용자가 Desktop에서 직접 실행합니다. 한 요청에서 여러 책임이 필요하면 runtime이 설치된 스킬을
조합하며 manifest dependency나 공통 router를 전제하지 않습니다.

단일 upstream fork뿐 아니라 Quality Engineering처럼 여러 source를 합성한 플러그인도 원본을
별도 baseline commit에 byte-for-byte로 보존한 뒤 최종 경로로 이동해 수정합니다. 현재 파일의
출처는 `UPSTREAM.md`의 source·baseline·final mapping으로 추적합니다.

## 문서 경계

현재 구조는 이 디렉터리에서 갱신하고, 선택의 이유와 대안은
[`decisions/`](../decisions/)에 보존합니다. 구현 계획은 장기간 유지할 아키텍처 지식과
구분하며 기본적으로 `docs/` 밖에서 관리합니다.
