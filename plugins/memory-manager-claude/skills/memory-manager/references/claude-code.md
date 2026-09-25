# Claude Code 메모리 접근

Claude Code 메모리를 대상으로 할 때만 읽는다. 현재 호스트 지침과 사용자가 지정한 경로가
접근 범위와 수정 권한을 결정한다. 메모리 점검 요청만 있으면 읽기 전용으로 시작한다.

## 대상 구분

- 프로젝트의 `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/`는 지시 파일이다.
  저장된 대화 메모리와 구분하고, 메모리 정리만으로 자동 수정하지 않는다.
- Claude Code의 자동 메모리는 현재 프로젝트에 대응하는
  `~/.claude/projects/<project>/memory/` 아래에서 찾는다. 디렉터리 이름을 추측해
  다른 프로젝트의 메모리를 열지 말고 현재 세션이 보여 주는 경로나 정확한 프로젝트
  대응을 확인한다.
- 사용자 홈의 다른 프로젝트 기록, transcript, 캐시와 설치 플러그인은 범위 밖이다.

## 반영

Claude Code의 현재 호스트 정책이 직접 편집을 허용하고 사용자가 정리를 요청한 경우에만
정확히 확인한 대상 파일을 백업·재조회하며 수정한다. 현재 환경이 수정 노트 방식만 허용하면
그 방식과 경로를 따른다. 자동 메모리 로더의 반영은 저장 후 다음 세션에서 별도로 확인한다.

공식 참고: [Claude Code 메모리](https://code.claude.com/docs/en/memory),
[설정 디렉터리](https://code.claude.com/docs/en/claude-directory).
