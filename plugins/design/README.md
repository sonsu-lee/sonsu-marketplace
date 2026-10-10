# Design

웹·앱·운영 화면을 Figma 또는 코드로 설계·재설계하고, 수정 없는 감사와 디자인 레퍼런스 선별을 지원합니다.

## 설치

```sh
codex plugin add design@sonsu-marketplace
claude plugin install design@sonsu-marketplace
omp plugin install design@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `design-interface` | 새 화면·흐름을 만들 때 | 명세·시안·Figma 또는 구현과 검증 근거 |
| `redesign-interface` | 기존 화면·흐름을 개선할 때 | 보존·변경 사항을 대조한 결과와 전후 차이 |
| `audit-interface` | 코드·화면·Figma를 수정 없이 감사할 때 | 관찰·사용자 영향·최소 수정 방향을 담은 finding |
| `find-references` | 화면·흐름·컴포넌트·스타일 사례를 선별할 때 | 출처·관찰·차용 범위 또는 `no_verified_match` |

## 사용 예시

> 도서관 앱에 대출 중인 책과 반납 기한을 보는 새 화면을 코드로 구현해 줘. 대출 데이터와 기존 목록 컴포넌트는 프로젝트에 있어.

`design-interface`가 기존 컴포넌트로 제목·반납 기한·연체 상태를 구성하고 빈 목록과 긴 제목 등 요청 환경을 확인합니다. 결과에는 구현 위치, 실제 실행 근거와 미확인을 구분해 적습니다. 대표 이용자 검증을 실행하지 않았다면 그 단계는 `not_run`으로 남깁니다.

> 같은 화면을 수정하지 말고 문제점만 감사해 줘.

`audit-interface`가 읽기 전용으로 관찰해 finding을 전달합니다. 감사 결과를 자동 수정 권한으로 사용하지 않습니다.

## 구성

[작업 선택과 산출물](references/delivery.md)에서 대상 제품·기존 디자인 시스템·사용자 과업과 완료 범위를 정합니다. 반복 판단·권한·대량 처리·부분 실패가 핵심이면 [Operations 계약](references/operations/screen-contract.md)을 적용합니다.

Figma 캔버스 작업은 호스트의 공식 Figma MCP 연결과 도구의 필수 스킬을 사용합니다. Codex connector와 Claude Code MCP 연결은 별도로 설정합니다. [Figma 실행 경로](references/figma/workflow.md)로 native 화면·상태·요청한 prototype을 만들고 readback합니다. Figma 결과를 코드로 옮기기 전에는 검토 가능한 결과를 제시하고 해당 revision의 명시적 허가를 받습니다. 코드 직접 구현 요청은 기존 앱에서 화면과 동작을 확인합니다. Desktop companion은 [수동 사용 설명](figma-plugin/README.md)을 따릅니다.

대상 앱의 `DESIGN.md`와 DQ 판정은 [품질 계약](references/design-quality.md), 실제 증거와 명령은 [검증](references/verification.md)을 따릅니다. 감사에서는 기존 파일을 읽기 전용으로 검사합니다. [레퍼런스 검색 계약](references/reference-search.md)은 공급자 자격·출처·확인 수준과 차용 범위를 정하며, 설계 중 탐색은 사용자의 요청·동의 범위에서 진행합니다. 여러 단계 작업은 [작업 연속성](references/continuity.md)으로 이어 갑니다.

[설계 구조](../../docs/architecture/design.md)와 [출처](UPSTREAM.md)를 참고하세요.

## 검증

저장소 루트에서 실행합니다.

```bash
python3 plugins/design/scripts/validate_design_quality.py design-md <DESIGN.md>
python3 plugins/design/scripts/validate_design_quality.py contract <contract.json>
python3 plugins/design/scripts/validate_design_quality.py report <report.json> <contract.json>
python3 plugins/design/scripts/validate_design_quality.py references <reference-set.json>
python3 plugins/design/scripts/validate_operations_contracts.py evals evals/operations-ui/cases.json
python3 -B -m unittest discover -s plugins/design/tests -p 'test_*.py'
```
