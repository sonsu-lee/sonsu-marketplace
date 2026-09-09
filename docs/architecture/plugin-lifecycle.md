# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-09-08

## 흐름

```text
후보 선정
  → 업스트림과 라이선스 확인
  → 원본 기준 commit 가져오기
  → 원본 동일성 검증
  → 별도 기준 commit
  → Codex 정본 manifest와 marketplace 등록
  → Claude Code native manifest 결정론적 생성
  → 플랫폼별 validation과 실제 로딩 검증
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

## 플랫폼 호환성 계층

`.agents/plugins/marketplace.json`과 plugin별 `.codex-plugin/plugin.json`이 metadata의 정본입니다.
[`scripts/render-claude-compat.py`](../../scripts/render-claude-compat.py)는 이 정본에서 root
`.claude-plugin/marketplace.json`과 plugin별 `.claude-plugin/plugin.json`을 생성합니다. 생성물을
직접 편집하지 않으며, platform-specific 필드 차이는 renderer와 fixture test에서 명시적으로
관리합니다. 공유 `skills/`, `hooks/`, `scripts/` 본문은 복제하지 않고 두 manifest가 같은 plugin
root를 가리킵니다.

## 검증

매니페스트와 JSON 문법만 확인하는 것으로 완료하지 않습니다. renderer의 `--check`, Claude Code의
strict validator와 격리 설치, Codex의 실제 플러그인 읽기 경로를 각각 확인합니다. 이름, 버전,
source, 스킬과 hook 목록을 플랫폼별 증거로 구분하며 실행하지 못한 경로는 `not_run`으로 남깁니다.
업스트림 업데이트는 [업스트림 플러그인 업데이트 런북](../runbooks/updating-upstream-plugin.md)을
따릅니다.
