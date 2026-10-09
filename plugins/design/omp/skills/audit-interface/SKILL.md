---
name: audit-interface
description: 기존 웹·모바일·운영 UI 또는 Figma 화면·prototype의 구성, 정보, 상태, 상호작용, 접근성과 구현 근거를 수정 없이 감사할 때 사용한다. 신규 화면 제작과 재설계에는 사용하지 않는다.
---

# 기존 인터페이스 감사

대상과 범위를 고정하고 현재 코드·실제 화면 또는 Figma file/page/frame을 읽기 전용으로 확인한다.
대상 파일과 application data를 변경하지 않는다. 화면에서는 scroll·focus·route/tab navigation 등
비파괴 관찰만 수행하고 submit·create·update·delete·persisted toggle은 실행하지 않는다.

1. [선택과 산출물](../../references/delivery.md)로 대상 제품, `DESIGN.md`, 레퍼런스,
   운영 업무 여부와 Figma/코드 경로를 확인한다. 기존 `DESIGN.md`는 Google 형식으로 검증하고
   부재나 오류는 finding으로 보고한다. 감사 중 문서를 만들거나 수정하지 않는다.
2. [공통 디자인 품질 계약](../../references/design-quality.md)으로 사용자 과업·핵심 질문·정보·
   표현·환경과 미확인을 복원한다. DQ1–DQ6은 독립 평가자 2명의 근거가 없으면 통과시키지 않는다.
   DQ0에서는 입력의 기존 요구사항 ID·출처·관련 조건과 화면·상태·흐름의 대응을 기존 명세·annotation에서 읽기 전용으로 대조한다. 확인할 수 없는 대응은 미확인으로 남기고 없는 ID나 문서를 만들지 않는다.
3. 운영 화면이면 [Operations 품질 적용](../../references/operations/quality-contract.md)과
   [증거 계약](../../references/operations/evidence-contract.md)으로 action·permission·state,
   부분 실패·복구와 scenario×environment를 검사한다.
4. Figma 대상이면 [Figma 제작 경로](../../references/figma/workflow.md)의 읽기 전용 절차로
   screenshot, Auto Layout·component·variable·icon, reaction과 가능한 playback을 구분해 확인한다.
   공식 Figma 도구의 선행 조건을 따르고 지원되지 않는 검사는 `not_run`으로 남긴다.
5. 비교할 레퍼런스를 받았거나 탐색을 요청받았으면 [레퍼런스 검색 계약](../../references/reference-search.md)의
   검색 전 확인·쿼리·공급자 자격·수집과 확인·근거 수준·저작권과 보관을 적용한다. 출처·locator·
   공급자와 쿼리(직접 찾은 경우)·inspection·관찰과 비교 근거를 감사 결과에 남긴다. 비교만 하는
   감사에서는 primary 선정·차용 잠금이나 `design-reference-set-v1`·`extensions.references` 작성을
   요구하지 않는다. 레퍼런스와 다르다는 사실만으로 finding을 만들지 않고 사용자 과업과 DQ 기준의 영향으로 판단한다.
6. finding마다 정확한 대상, 관찰 근거, 사용자 영향, gate/severity와 최소 수정 방향을 기록한다.
   실제 runtime, resize, playback 또는 대표 사용자 결과를 확인하지 못했으면 `inconclusive`나
   `not_run`으로 표시한다. 감사 요청을 자동 수정 권한으로 해석하지 않는다.

```bash
python3 <design-plugin-root>/scripts/validate_design_quality.py contract <contract.json>
python3 <design-plugin-root>/scripts/validate_design_quality.py report <report.json> <contract.json>
```

운영 확장 계약은 `scripts/validate_operations_contracts.py`도 사용한다. Live 결과 증거 없이
DQ8이나 `end_to_end_status: passed`를 주장하지 않는다.
