# Engineering 원본 출처

이 파일은 우리 마켓플레이스에서 추가한 출처 기록입니다.
이번 가져오기에서는 아래에 포함된 원본 파일의 내용과 실행 권한을 변경하지 않았습니다.

- 원본 기준 커밋: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`
- 저장소 내 가져오기 commit: `2e760c5dd6beb71c703b0a20e1bf123cd34c2f8b`
- 원본 플러그인 버전: `6.3.0`
- 가져온 날짜: `2026-09-01`
- 라이선스: [MIT, Copyright (c) 2025 Jesse Vincent](LICENSE)

## 포함 범위

원본 Codex 패키징 스크립트의 소스 파일 포함 범위를 따릅니다.

- `.codex-plugin/plugin.json`
- `skills/` 전체: 스킬 14개와 참고 문서, 프롬프트, 보조 스크립트
- `assets/` 전체
- `README.md`, `LICENSE`, `CODE_OF_CONDUCT.md`

원본 저장소의 다른 플랫폼용 매니페스트, 세션 훅, 개발용 지침,
최상위 `docs/`, `tests/`, `scripts/` 등은 Codex 플러그인 소스 구성에서 제외합니다.
가져오기 commit에는 원본 README와 원본 저장소·기준 commit을 식별하는 출처 기록이 포함되어
있습니다. 현재 README는 로컬 Engineering 배포를 설명하도록 교체했으며, 원본의 다른 플랫폼용
안내와 출처는 저장소 내 가져오기 commit에서 확인할 수 있습니다.

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
산출물 요청과 구분합니다. Engineering은 다른 플러그인을
호출하거나 설치되었다고 가정하지 않으며, 여러 플러그인이 필요한 요청은 Codex의 runtime
routing으로 순서대로 조합합니다.

`6.3.0-sonsu.3`부터 bootstrap skill은 `using-engineering-skills`, 내부 skill namespace는
`engineering:*`를 사용합니다. 로컬 fork의 manifest는 로컬 배포·유지관리 주체를 표시하고, 원본 저작권과
출처는 `LICENSE`와 이 문서에 보존합니다.

`6.3.0-sonsu.4`부터 공통 quality gate 상태·증거 계약과 stage-owned gate를 적용합니다.
design document, plan, task, whole-change review와 final verification은 exact artifact revision에
묶이며 실패하면 전체 workflow를 재귀적으로 다시 시작하지 않고 가장 가까운 소유 단계로
되돌아갑니다. 반복에는 변경된 입력과 유한한 상한이 필요하며, 상한에 남은 실제 필수 finding은
human `accepted_risk` 없이 pass나 complete로 바뀌지 않습니다.

`6.3.0-sonsu.5`부터 구현 plan이 필요한 개발 작업은 언어 중립적인 의사코드로 전체 동작과
제어 흐름을 먼저 정의합니다. 각 흐름을 파일, task, dependency와 검증 방법에 연결한 뒤
동작·회귀 위험과 검증 실익에 따라 TDD 또는 다른 검증을 선택하고 이유를 기록합니다. TDD를
선택한 task의 RED–GREEN–REFACTOR 규칙은 유지하며, plan이 필요 없는 단순 작업과 문서,
metadata, 단순 configuration에는 긴 의사코드나 가치 없는 테스트를 강제하지 않습니다. 실행 중
승인된 설계나 관찰 가능한 계약을 바꾸는 차이는 사용자 재승인을 받고, 새 plan 리비전의 영향을
받는 완료 task는 다시 열어 구현·검증·리뷰합니다.

`6.3.0-sonsu.6`부터 scratch plan, subagent workspace와 brainstorming session은
`.engineering/` 경로만 사용합니다. visual companion은 외부 브랜드 이미지와 원격 요청 없이
Engineering 버전을 텍스트로 표시합니다. 현재 유지관리자의 비공개 신고 채널로 연결되지 않는
원본 `CODE_OF_CONDUCT.md`와 사용하지 않는 원본 브랜드 asset은 배포 subtree에서 제거합니다.

로컬 변경의 이유는 [문서·커밋 승인 결정](../../docs/decisions/0002-separate-doc-and-commit-approval.md),
[플러그인 독립성 결정](../../docs/decisions/0003-keep-plugins-independent.md),
[quality gate 결정](../../docs/decisions/0007-use-stage-owned-quality-gates.md),
[스킬 라우팅 문서](../../docs/architecture/skill-routing.md)에 기록합니다.
