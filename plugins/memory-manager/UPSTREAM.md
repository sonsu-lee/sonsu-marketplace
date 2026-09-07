# Memory Manager 출처

- 작성 방식: 독자 작성. 외부 스킬·스크립트·템플릿의 파일을 복사하거나 번역해 포함하지 않음.
- 확인일: 2026-09-07
- 배포 범위: Codex plugin manifest, 스킬 하나와 에이전트별 참고 지침. 별도 runtime dependency 없음.
- 라이선스: 이 플러그인에는 현재 별도 라이선스를 선언하지 않음.

## 설계 참고

| 출처와 고정 revision | 참고한 관점 | 포함하지 않은 부분 |
| --- | --- | --- |
| [stark-ai-de/agent-skills](https://github.com/stark-ai-de/agent-skills/blob/284d2688146ed99f89a4ca0466cf4db92ced8126/skills/codex-operations/codex-memory-curator/SKILL.md), v0.2.2, Apache-2.0 표기 | 기억을 검증 가능한 주장으로 분류하고 generated state와 수정 노트를 구분 | 8개 workflow, Plan mode 강제, 보고서 template와 Node scripts |
| [agentic-utils/skills](https://github.com/agentic-utils/skills/blob/64274f6024e366a5c1c61d65d3a0bb1b27b86d4a/plugins/claude-code/skills/dream/SKILL.md) | 근거를 확인한 병합·갱신·정리, 조건과 날짜의 보존 | Claude 경로 추정, 직접 수정 명령과 스킬 원문 |
| [alexknowshtml/claude-memory-health](https://github.com/alexknowshtml/claude-memory-health/blob/09c5f8fd08787b680ec5717ac13334c4caaa0f7b/SKILL.md) | 인덱스 비대화, 깨진 링크와 참조 누락 점검 | cold storage 이동, scheduler, 자동 Git commit과 Bun scripts |

뒤의 두 저장소는 확인한 revision의 tree에서 라이선스 파일을 찾지 못했습니다. 재사용 허가를
추정하지 않으며 동작 관점만 참고했습니다. 검색 인덱스의 오래된 버전과 저장소의 실제 revision을
구분했고, 검색 결과에만 남은 다른 `claude-dream` 저장소는 기준 원본으로 채택하지 않았습니다.

## 공식 계약

- [Codex skills](https://developers.openai.com/codex/skills/): 명시적 호출과 `allow_implicit_invocation`.
- [Claude Code memory](https://code.claude.com/docs/en/memory): auto memory 경로, worktree 공유와 인덱스 로딩.
- Codex update note의 구체적인 경로·수정 권한은 실행 세션에 주어진 호스트 지침을 따릅니다.
  특정 세션의 메모리 계약을 모든 Codex 버전의 공개 API로 일반화하지 않습니다.
