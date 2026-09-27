# UI Design

`interface-design`는 일반 웹·앱, 운영 화면과 Figma 제품 화면을 한 작업 흐름에서 설계·재설계·감사하는
Codex·Claude Code 플러그인입니다. 공개 스킬은 작업 유형으로 고르고 Figma와 코드는 실행 경로로 선택합니다.

```sh
codex plugin add interface-design@sonsu-marketplace
```

| 작업 | 스킬 |
| --- | --- |
| 새 화면·흐름 | `design-interface` |
| 기존 화면·흐름 변경 | `redesign-interface` |
| 수정 없는 코드·화면·Figma 감사 | `audit-interface` |

작업은 대상 제품, 기존 화면·디자인 시스템, 레퍼런스, 사용자 과업과 산출물부터 정합니다.
반복 판단·권한·대량 처리·부분 실패가 핵심이면 [Operations 계약](references/operations/screen-contract.md)을
조건부로 적용합니다. Figma가 정본이면 [Figma 실행 경로](references/figma/workflow.md)로 화면·상태·
요청한 prototype을 만들고 readback합니다. Figma 결과를 코드로 옮기기 전에는 검토 가능한
결과를 제시하고 그 revision에 대한 명시적 허가를 받습니다. Figma를 쓰지 않으면 기존 앱에서
직접 구현하고 실제 화면과 동작을 확인합니다.

새 설계·재설계·Figma 화면은 대상 앱의 가장 가까운 `DESIGN.md`를 사용하고 Google 형식으로
작성·검증합니다. 감사는 읽기 전용으로 검사합니다. 공통 Design Decision Contract와 DQ0–DQ8은
[품질 계약](references/design-quality.md)을 따릅니다. Proposal은 DQ0–DQ6, Figma/implementation은
DQ0–DQ7, live는 DQ0–DQ8을 요구하며, 미실행 단계의 통과를 주장하지 않습니다.

```bash
python3 scripts/validate_design_quality.py design-md <DESIGN.md>
python3 scripts/validate_design_quality.py contract <contract.json>
python3 scripts/validate_design_quality.py report <report.json> <contract.json>
python3 scripts/validate_operations_contracts.py evals ../../evals/operations-ui/cases.json
```

[작업 선택과 산출물](references/delivery.md), [설계 구조](../../docs/architecture/interface-design.md),
[출처](UPSTREAM.md)를 참고하세요. Figma Desktop companion은 [수동 사용 설명](figma-plugin/README.md)을
따릅니다. 여러 단계 작업은 [연속성 참고 자료](references/continuity.md)로 이어 갑니다.
