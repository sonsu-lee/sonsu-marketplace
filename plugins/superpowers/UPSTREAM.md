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
따라서 보존한 원본 README의 다른 플랫폼용 상대 링크에는 이 패키지에 없는 경로가 있습니다.
해당 문서는 위 기준 커밋의 원본 저장소에서 확인할 수 있습니다.

공식 배포 아카이브를 재현한 것은 아닙니다. 원본 패키징 스크립트가 별도의 공식 배포본에서
가져오는 `skills/*/agents/openai.yaml` 메타데이터는 이번 원본 소스 가져오기에 추가하지 않았습니다.

## 호환성과 커스텀 기준

원본 Codex 매니페스트의 `hooks: {}`를 유지하고 세션 훅 파일은 포함하지 않습니다.
Codex CLI `0.149.1`의 `plugin/read`로 로컬 매니페스트와 스킬을 읽을 수 있는지 확인합니다.
`hooks` 필드를 지원하지 않는 별도 스캐폴드 검증기는 원본 매니페스트를 거부할 수 있습니다.

이번 커밋은 커스텀 작업의 비교 기준입니다. 스킬 적용 조건, worktree 처리,
문서 작성·커밋, TDD, 리뷰 절차와 원본 시각 도구의 동작은 수정하지 않았습니다.
후속 변경은 이 기준 커밋과 구분하여 기록합니다.
