# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-09-25

## 흐름

```text
후보 선정
  → 업스트림과 라이선스 확인
  → 원본 기준 commit 가져오기
  → 원본 동일성 검증
  → 별도 기준 commit
  → Codex 정본 manifest와 marketplace 등록
  → package 검증과 실제 로딩 검증
  → 로컬 정책 변경
  → 로컬 변경 commit
  → 이후 업스트림 업데이트
```

## 업스트림 기준선

외부 플러그인은 원본 파일과 실행 권한을 먼저 보존하고, 업스트림 출처와 기준 commit을
`UPSTREAM.md`에 기록합니다. 여러 upstream의 일부 파일을 합성할 때는 source path, 임시 baseline
path, 최종 path와 hash를 함께 기록합니다. 원본 가져오기와 로컬 커스텀을 서로 다른 commit으로
남겨 이후 업데이트에서 두 변경의 출처를 구분할 수 있게 합니다.

## 로컬 커스텀

로컬 정책은 원본 기준선 이후에 적용합니다. 하나의 upstream plugin을 fork한 매니페스트 버전은
업스트림 버전 뒤에 `-sonsu.<revision>`을 붙여 원본 릴리스와 구분합니다. 여러 source를 합성하거나
로컬에서 새로 설계한 plugin은 독립 semantic version을 사용합니다. 여러 source를 합성했다면
`UPSTREAM.md`에서 각 source와 변환을 추적하고, 가져온 source가 없는 독립 plugin은 upstream
기준선을 만들지 않습니다. 정책 변경은 관련 결정 기록과 현재 아키텍처 문서를 함께 갱신합니다.

Engineering은 [독립 플러그인 결정](../decisions/0009-maintain-engineering-as-an-independent-plugin.md)에
따라 독립 semantic version을 사용하며 upstream 동기화나 이전 호환 경로를 배포 계약으로 두지
않습니다.

## Codex 배포

`.agents/plugins/marketplace.json`과 각 `.codex-plugin/plugin.json`이 Codex 패키지의 정본입니다.
기존 연구·라이선스·upstream 기록은 유지합니다. `shared/agent-policy`와 `shared/task-continuity`에서
각 플러그인에 필요한 자료를 생성해 다른 패키지 설치 없이 실행되게 합니다.

## Claude Code 배포

Codex catalog와 manifest를 정본으로 두고 `python3 scripts/render-claude-compat.py`로
`.claude-plugin/marketplace.json` 및 각 패키지 manifest를 생성합니다. 대부분의 스킬·hook·script는
같은 패키지 파일을 사용합니다. `memory-manager`는 네 스킬과 저장 스크립트·훅을 별도 Claude
패키지에 생성합니다. 정리·승격 스킬만 Claude의 수동 호출 제한을 적용합니다. 모델 프로필은 호스트별로 분리하며, Codex connector와
Claude Code MCP 구성은 별도의 실행 환경 상태입니다.

## 검증

생성기의 `--check`, 양쪽 catalog와 스킬 경로·frontmatter 검증, 실제 loader·행동 평가를
구분합니다. 정적 JSON 통과만으로 실제 스킬 선택이나 host별 hook 실행을 주장하지 않습니다.
미실행은 `not_run`, 원인 불명은 `inconclusive`로 기록합니다.
[업데이트 런북](../runbooks/updating-upstream-plugin.md)과
[ADR 0015](../decisions/0015-independent-skills.md)를 따릅니다. 이전 Engineering 게이트 결정은
[ADR 0014](../decisions/0014-use-codex-managed-engineering.md)에 역사적 근거로 보존합니다.
