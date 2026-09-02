# Superpowers 원본 출처

이 파일은 우리 마켓플레이스에서 추가한 출처 기록입니다.
이번 가져오기에서는 아래에 포함된 원본 파일의 내용과 실행 권한을 변경하지 않았습니다.

- 원본 저장소: [obra/superpowers](https://github.com/obra/superpowers)
- 기준 커밋: [`b36e0829c6d0140e93cfef2ca599b1b07d4a7797`](https://github.com/obra/superpowers/commit/b36e0829c6d0140e93cfef2ca599b1b07d4a7797)
- 원본 플러그인 버전: `6.3.0`
- 가져온 날짜: `2026-09-01`
- 라이선스: [MIT, Copyright (c) 2025 Jesse Vincent](LICENSE)

## 포함 범위

원본 [Codex 패키징 스크립트](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/scripts/package-codex-plugin.sh)의 소스 파일 포함 범위를 따릅니다.

- `.codex-plugin/plugin.json`
- `skills/` 전체: 스킬 14개와 참고 문서, 프롬프트, 보조 스크립트
- `assets/` 전체
- `README.md`, `LICENSE`, `CODE_OF_CONDUCT.md`

원본 저장소의 다른 플랫폼용 매니페스트, 세션 훅, 개발용 지침,
최상위 `docs/`, `tests/`, `scripts/` 등은 Codex 플러그인 소스 구성에서 제외합니다.
가져오기 commit에는 원본 README가 포함되어 있습니다. 현재 README는 로컬 Engineering 배포를
설명하도록 교체했으며, 원본의 다른 플랫폼용 안내는 위 기준 커밋에서 확인할 수 있습니다.

공식 배포 아카이브를 재현한 것은 아닙니다. 원본 패키징 스크립트가 별도의 공식 배포본에서
가져오는 `skills/*/agents/openai.yaml` 메타데이터는 이번 원본 소스 가져오기에 추가하지 않았습니다.

## 호환성과 커스텀 기준

원본 Codex 매니페스트의 `hooks: {}`를 유지하고 세션 훅 파일은 포함하지 않습니다.
Codex CLI `0.149.1`의 `plugin/read`로 로컬 매니페스트와 스킬을 읽을 수 있는지 확인합니다.
`hooks` 필드를 지원하지 않는 별도 스캐폴드 검증기는 원본 매니페스트를 거부할 수 있습니다.

가져오기 commit `2e760c5dd6beb71c703b0a20e1bf123cd34c2f8b`는 커스텀 작업의 비교
기준입니다. 이 commit에서는 스킬 적용 조건, worktree 처리, 문서 작성·커밋, TDD,
리뷰 절차와 원본 시각 도구의 동작을 수정하지 않았습니다. 후속 변경은 이 기준 commit과
구분하여 기록합니다.

## 로컬 커스텀 버전

`6.3.0-sonsu.1`부터 다음 로컬 정책을 적용합니다.

- 원본 `using-git-worktrees` 파일과 worktree 감지·생성 흐름은 유지합니다. 해당 스킬 안의
  commit 문구도 실제 실행 시 로컬 전역 Git 승인 게이트를 우선 적용합니다.
- 날짜 기반 spec과 plan을 `docs/`에 자동 생성하지 않습니다.
- 기존 문서를 먼저 확인하고 [문서 라우팅 정책](../../docs/README.md)에 따라 갱신하거나 생성합니다.
- 문서 작성, 구현과 Git 커밋 권한을 각각 구분합니다.
- TDD는 코드의 동작 변경과 버그 수정에 적용하고, 문서·메타데이터·단순 설정에는 변경에 맞는 검증을 사용합니다.

`6.3.0-sonsu.2`부터 완료된 개발 branch의 통합 결정을 일반적인 branch·commit·push·ticket·PR
산출물 요청과 구분합니다. 당시 `Superpowers`라는 이름의 로컬 플러그인은 다른 플러그인을
호출하거나 설치되었다고 가정하지 않으며, 여러 플러그인이 필요한 요청은 Codex의 runtime
routing으로 순서대로 조합합니다.

`6.3.0-sonsu.3`부터 로컬 플러그인의 공개 이름과 ID를 `Engineering`과 `engineering`으로
변경합니다. bootstrap skill은 `using-engineering-skills`, 내부 skill namespace는
`engineering:*`를 사용합니다. 로컬 fork의 manifest는 로컬 배포·유지관리 주체를 표시하고, 원본 저작권과
출처는 `LICENSE`와 이 문서에 보존합니다.

`6.3.0-sonsu.4`부터 공통 quality gate 상태·증거 계약과 stage-owned gate를 적용합니다.
design document, plan, task, whole-change review와 final verification은 exact artifact revision에
묶이며 실패하면 전체 workflow를 재귀적으로 다시 시작하지 않고 가장 가까운 소유 단계로
되돌아갑니다. 반복에는 변경된 입력과 유한한 상한이 필요하며, 상한에 남은 실제 필수 finding은
human `accepted_risk` 없이 pass나 complete로 바뀌지 않습니다.

기존 실행 artifact와 스크립트 호환성을 위해 `.superpowers/` scratch 경로와
`SUPERPOWERS_DISABLE_TELEMETRY` 환경 변수는 유지합니다. 새 이름인
`ENGINEERING_DISABLE_TELEMETRY`도 같은 opt-out으로 인식합니다. 원본 아이콘 파일은 provenance
비교를 위해 남겨 두지만 Engineering manifest에서는 사용하지 않습니다.

로컬 변경의 이유는 [문서·커밋 승인 결정](../../docs/decisions/0002-separate-doc-and-commit-approval.md),
[플러그인 독립성 결정](../../docs/decisions/0003-keep-plugins-independent.md)과
[이름 변경 결정](../../docs/decisions/0005-rename-superpowers-to-engineering.md),
[quality gate 결정](../../docs/decisions/0007-use-stage-owned-quality-gates.md),
[스킬 라우팅 문서](../../docs/architecture/skill-routing.md)에 기록합니다.
