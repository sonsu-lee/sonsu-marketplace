# Task 1 구현 보고서

## Status

`F1`, `F6` 범위의 Figma-only plugin package rename과 connector declaration을 완료했다.

## 구현 내용

- `plugins/design/`을 `plugins/figma-workflow/`로 이동했다.
- manifest의 identifier를 `figma-workflow`, display name을 `Figma Workflow`로 변경하고 Paper 설명·keyword·prompt를 제거했다.
- `plugins/figma-workflow/.app.json`에 locally installed official Figma plugin `2.0.21`에서 확인한 registered connector ID `connector_68df038e0ba48191908c8434991bbac2`를 지정된 shape로 추가했다.
- marketplace entry의 name과 local path를 갱신했다.
- Task 1에서 지정한 Paper-only `paper-product-design` skill과 `paper-quality-contract.md`를 삭제했다. 나머지 docs/references의 Paper 정리는 Task 4/5 범위이므로 유지했다.

## 검증

- `python3 -m json.tool plugins/figma-workflow/.codex-plugin/plugin.json >/dev/null && python3 -m json.tool plugins/figma-workflow/.app.json >/dev/null && python3 -m json.tool .agents/plugins/marketplace.json >/dev/null` — 통과 (출력 없음)
- `python3 /Users/sonsu/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/figma-workflow` — `Plugin validation passed: /Users/sonsu/.codex/worktrees/c8fa/sonsu-marketplace/plugins/figma-workflow`
- 실제 connector/tool exposure(설치·reload 및 새 task)는 repository 검증 범위 밖이므로 `not_run`이다.

## 변경 파일

- `plugins/figma-workflow/.codex-plugin/plugin.json`
- `plugins/figma-workflow/.app.json`
- `.agents/plugins/marketplace.json`
- `plugins/figma-workflow/skills/paper-product-design/` 삭제
- `plugins/figma-workflow/references/paper-quality-contract.md` 삭제

## 우려 사항

- Figma Desktop에서 connector가 실제 노출되는지는 아직 검증하지 않았다(`not_run`).
- 기존 Figma 문서에 남은 Paper 언급은 후속 Task 4/5 소유 범위다.
