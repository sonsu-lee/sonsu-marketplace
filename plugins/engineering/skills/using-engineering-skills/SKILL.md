---
name: using-engineering-skills
description: 개발 작업을 시작하거나 작업 성격이 바뀔 때 요청에 맞는 Engineering 스킬과 수행 절차를 선택한다.
---

# Engineering 스킬 선택

요청의 목적과 각 스킬의 적용 조건을 대조해 필요한 지침을 선택한다. 구체적인 작업을 위임받은
에이전트는 전달받은 범위와 해당 스킬부터 실행한다.

## 작업에 맞는 절차를 고른다

1. 사용자의 요청, 현재 승인 범위와 저장소 지침을 확인한다. 이미 확인한 내용은 이어서 사용한다.
2. 아래 기준으로 필요한 스킬을 읽고 적용 목적을 짧게 알린다. 여러 스킬이 필요하면 접근 방법을
   정하는 스킬부터 적용하고, 같은 작업에서 읽은 지침은 재사용한다.
3. 진행 중 목적이나 위험이 달라지면 관련 단계의 조건을 다시 판단한다. 기존 승인 안에서
   절차를 조정하고, 새로운 사용자 결정이 필요한 부분과 그 의존 작업만 확인을 기다린다.

| 현재 작업 | 적용할 스킬 |
| --- | --- |
| 변경 범위·요구사항·설계 결정 | `engineering:brainstorming` |
| 원인이 불명확한 오류나 예상 밖 동작 | `engineering:systematic-debugging` |
| 여러 흐름·파일·검증을 연결하는 구현 계획 | `engineering:writing-plans` |
| 승인된 계획의 직접 실행 | `engineering:executing-plans` |
| 독립 작업의 위임 | `engineering:dispatching-parallel-agents` |
| 동작 변경을 테스트로 보호 | `engineering:test-driven-development`의 적용 기준 확인 |
| 개발 절차의 리뷰·명시적 독립 리뷰 | `engineering:requesting-code-review`의 워크플로우 분기 |
| 지정 코드·diff의 일반 직접 리뷰 | 설치된 일반 품질 리뷰 전용 스킬 우선. 없거나 이 스킬을 명시했으면 `engineering:requesting-code-review`의 직접 리뷰 분기 |
| 리뷰 피드백 검증·처리 | `engineering:receiving-code-review` |
| 완료나 검사 성공 보고 | `engineering:verification-before-completion` |
| 스킬 작성·수정 | `engineering:writing-skills` |

단순 설명이나 짧은 문장 수정은 필요한 답변을 바로 작성한다. 다른 플러그인은 사용자가
지정했거나, 저장소 지침이 요구하거나, 현재 작업에 필요한 기능을 제공할 때 함께 적용한다.

## 독립 산출물과 자동 선택

스킬 이름을 지정하지 않은 요청도 description의 시작·제외 조건으로 선택한다. 명시적 호출은
우선하고 이름 지정 자체로 쓰기 권한을 확대하지 않는다. 별도의 만능 router를 만들지 않는다.
PR 상태 조회·복구, 독립적인 심층 PR 리뷰, 일반 UI 설계·재설계는 해당 설치된 전문 스킬이
있으면 바로 시작한다. PR URL만 있는 일반 리뷰는 심층 리뷰로 승격하지 않는다. 웹/앱 설계와
운영 업무·Figma 파일 편집의 목적을 구분하고, 전체 개발 절차가 요청된 경우에만 필요한 단계를
조합한다. 기존에 선언한 필수 검증을 독립 스킬로 임의 대체하지 않는다.

## 승인 범위를 이어서 적용한다

사용자 지시와 프로젝트 지침을 우선한다. 구현·계획·재개·작업 경로 전환은 이미 확인한 승인
범위에서 진행한다. 설계만 요청받았다면 설계를 완성하고, 구현 전 확인이 요청됐다면 검토할
산출물을 완성한 뒤 해당 의존 작업의 답변을 기다린다.

Git 작업은 사용자가 승인한 동작과 범위에 맞춰 수행한다. staging은 staging 요청이나 승인된
commit의 일부로, commit·push·PR·merge·배포는 각각 해당 승인을 근거로 수행한다. 구현만
요청받았다면 변경과 검증을 완성해 diff를 보고한다. 스킬이나 계획의 문구는 이 권한을 추가하지 않는다.

## 필요한 공통 지침을 읽는다

- 여러 단계의 작업을 맡았다면 [작업 연속성](../task-continuity/SKILL.md)으로 진행과 근거를 기록한다.
- 단계에서 품질 판정을 요구하면 [품질 게이트 계약](references/quality-gates.md)을 적용한다.
- 계획 기반 작업에서 완료 근거의 누락·리비전 변화를 자동 관찰하려면
  [완료 근거 관찰 도구](references/evidence-gates.md)로 고정 task ID와 필수 검사를 등록한다.
  관찰 pilot은 선택 사항이며 Fast Path에 새 필수 단계를 추가하지 않는다.
- 에이전트를 위임·재개할 때에는 [실행 계약](references/agent-execution.md)을 적용한다.
- 플랫폼별 도구 대응이 필요하면 현재 환경의 자료를 읽는다:
  [Codex](references/codex-tools.md), [Claude Code](references/claude-code-tools.md),
  [Gemini](references/gemini-tools.md), [Pi](references/pi-tools.md),
  [Antigravity](references/antigravity-tools.md), [Hermes](references/hermes-tools.md).
