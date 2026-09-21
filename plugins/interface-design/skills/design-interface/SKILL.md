---
name: design-interface
description: 새 웹·모바일 앱 화면이나 사용자 흐름을 디자인하고 요청한 명세·시안·Figma 또는 기존 프로젝트의 구현을 완성할 때 사용한다. 새 설정 화면, 가입·입력 흐름, 콘텐츠·탐색 화면 설계 요청에서 자동 선택하며 이름으로 직접 호출할 수도 있다. 기존 UI 재설계, 수정 없는 감사, 브랜드 전략만의 작업은 제외한다. 운영 업무 전문 설계나 Figma 파일 자체의 편집은 해당 전문 스킬이 있으면 우선한다.
---

# 새 인터페이스 설계

사용자가 무엇을 이해하고 판단하고 실행해야 하는지에서 화면과 흐름을 설계한다. 특정 도구,
스타일이나 화면 비율을 모든 제품에 적용하지 않는다.

## 시작과 범위

1. 요청과 기존 프로젝트·디자인 시스템을 읽어 사용자, 핵심 과업, 콘텐츠, 상태, 플랫폼,
   입력 방식과 요청 산출물을 확인한다. 이미 확인한 내용은 다시 묻지 않는다.
2. [선택과 산출물](../../references/delivery.md)을 읽어 자동 선택·직접 호출·조합과 완료 범위를 정한다.
3. [디자인 판단 계약](../../references/design-quality.md)에 따라 사용자·맥락·핵심 질문·오판 비용,
   과업별 정보·표현·환경과 사전 등록 지표를 `design-decision-contract-v1`으로 만들고 잠근다.
4. [공통 디자인 절차](../../references/design-process.md)를 적용한다. 웹이면
   [웹](../../references/web.md), iOS·Android 앱이면 [모바일](../../references/mobile.md)을 함께 읽는다.
5. 기존 UI가 발견되면 요청이 신규 흐름 추가인지 재설계인지 판단한다. 명시적 호출은 존중하되
   범위 차이를 짧게 설명하고 기존 의미의 보존 절차를 적용한다. 스킬 전환을 위한 새 요청을 요구하지 않는다.

결정되지 않은 제품 규칙이나 실제 수치를 만들지 않는다. 예시와 가정을 표시하고 중요한 결정이
필요한 부분만 확인한다. 작은 화면 추가에 전체 제품 탐색을 반복하지 않는다.

## 제작과 확인

[DESIGN.md 형식과 CLI 검증](../../references/design-quality.md#designmd-형식과-cli-검증)에 따라
제품의 `DESIGN.md`를 작성·갱신하고 공식 CLI lint 결과를 완료 근거에 포함한다.

정보 구조 → 공간 배분 → 시각 체계 → 정보 자산 → 상태·흐름 순서로 실제 산출물을 만든다.
지도·차트·도식·표가 과업의 중심이면 [정보 자산](../../references/information-assets.md)을 읽고
영역 내부를 별도로 설계·검증한다. 코드·Figma·이미지 도구에는 이번 명세와 보존 조건을 전달한다.

[검증](../../references/verification.md)에 따라 요청한 환경과 실제 결과를 확인하고 실패 원인이
있는 단계로 돌아간다. 최종 결과, 중요한 결정, 확인한 범위와 미확인을 전달한다.

```bash
python3 <interface-design-plugin-root>/scripts/validate_design_quality.py contract <contract.json>
python3 <interface-design-plugin-root>/scripts/validate_design_quality.py report <report.json> <contract.json>
```

Proposal은 DQ0–DQ6, Figma와 implementation은 DQ0–DQ7, live 평가는 DQ0–DQ8을 요구한다.
DQ1–DQ6은 작성자가 아닌 독립 평가자 2명이 같은 revision을 평가한다. live 이전 결과를
`end_to_end_status: passed`로 올리지 않는다.

여러 단계의 작업은 [작업 연속성](../task-continuity/SKILL.md)으로 현재 명세·산출물·검증을 이어 간다.
단발 작업, 다른 작업의 부분 역할과 파일 쓰기가 금지된 작업에는 별도 기록을 만들지 않는다.
