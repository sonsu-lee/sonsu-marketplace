---
name: audit-interface
description: 기존 웹·모바일·운영 UI 또는 Figma 화면·prototype의 정보·상태·상호작용·접근성과 구현 근거를 수정 없이 감사할 때 사용한다. 신규 제작과 재설계는 각 설계 스킬이 담당한다.
---

# 기존 인터페이스 감사

대상과 범위를 고정하고 현재 코드·실제 화면 또는 Figma file/page/frame을 읽기 전용으로 확인한다. 관찰한 문제와 사용자 영향, 확인하지 못한 범위를 구분해 전달한다.

## 절차

1. [선택과 산출물](../../references/delivery.md)로 제품, `DESIGN.md`, 레퍼런스, 운영 업무 여부와 Figma/코드 경로를 확인한다. 기존 `DESIGN.md`는 [품질 계약](../../references/design-quality.md#designmd-공통-절차)의 명령으로 Google 형식을 검사하고 부재·오류를 finding으로 남긴다.
2. [디자인 판단 계약](../../references/design-quality.md)으로 사용자 과업·핵심 질문·정보·표현·환경과 미확인을 복원한다. [검증](../../references/verification.md)의 DQ0 절차로 기존 요구사항 ID·출처·관련 조건과 화면·상태·흐름, 사용한 revision과 승인 근거를 기존 자료에서 읽기 전용으로 대조한다. 확인할 수 없는 대응은 미확인으로 남긴다.
3. 운영 화면이면 [Operations 품질 적용](../../references/operations/quality-contract.md)과 [증거 계약](../../references/operations/evidence-contract.md)으로 action·permission·state, 부분 실패·복구와 scenario×environment를 검사한다.
4. Figma 대상이면 [Figma 제작 경로](../../references/figma/workflow.md)의 읽기 전용 절차로 screenshot, Auto Layout·component·variable·icon, reaction과 가능한 playback을 구분해 확인한다. 공식 도구의 선행 조건을 따르고 지원되지 않는 검사는 `not_run`으로 남긴다.
5. 비교 레퍼런스를 받았거나 탐색을 요청받았으면 [레퍼런스 검색 계약](../../references/reference-search.md#작업별-적용-범위)의 감사 범위를 적용한다. 출처·locator·공급자·직접 사용한 쿼리·inspection·관찰과 비교 근거를 남기고, 사용자 과업과 DQ 기준에 미치는 영향으로 finding을 판단한다.
6. [검증](../../references/verification.md)의 명령으로 기존 계약·보고서를 검사한다. 독립 평가와 scope별 gate는 [품질 계약](../../references/design-quality.md#차원별-합격)에 따라 판정하고 runtime·resize·playback·대표 사용자 결과의 부재는 `inconclusive` 또는 `not_run`으로 남긴다.

## 결과

finding마다 정확한 대상, 관찰 근거, 사용자 영향, gate/severity와 최소 수정 방향을 기록한다. 유효한 finding이 없으면 그 사실과 실제 확인 범위를 보고한다. 미확인 상태와 실행하지 않은 검사는 별도로 적는다.

## 예시

입력:
> 박물관 오디오 안내의 언어 선택 화면을 수정 없이 감사해 줘.

결과 예:
> 대상: 언어 선택 목록의 현재 언어 표시. 관찰: 선택 여부가 색상으로만 표시되고 접근성 트리에 선택 상태가 없다. 영향: 색을 구분하기 어려운 이용자가 현재 언어를 알기 어렵다. Gate: DQ6, severity: major. 최소 수정: 선택 상태의 텍스트·semantic state 제공. 음성 재생 결과는 실행하지 않아 `not_run`이다.

## 경계

- 대상 파일·문서와 application data를 변경하지 않는다. 없는 요구사항 ID나 문서를 감사 중 새로 만들지 않는다.
- 화면에서는 scroll·focus·route/tab navigation 등 비파괴 관찰만 수행한다. submit·create·update·delete·persisted toggle은 실행하지 않는다.
- 감사 요청은 자동 수정 권한이 아니다.

## 참고 자료

- [선택과 산출물](../../references/delivery.md)
- [디자인 판단 계약](../../references/design-quality.md), [검증](../../references/verification.md)
- [레퍼런스 검색 계약](../../references/reference-search.md)
