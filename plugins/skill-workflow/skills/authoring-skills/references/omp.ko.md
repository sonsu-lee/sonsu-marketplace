# omp 작성 시 고려사항

> 영문 정본: [omp.md](omp.md) (`57da0f4` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

작성하는 스킬이 omp를 대상으로 할 때 읽는다.

1. **로딩 경로 확인:** 프로젝트의 기여·설치 안내를 읽고 [omp 스킬 문서][skills]를
   확인한다. 일반 스킬 디렉터리와 이식 가능한 Agent Plugins 패키지는 메타데이터
   검증 방식이 다르다.
2. **이식 가능한 구조 유지:** 루트 `plugin.json`이 있는 패키지에서는 스킬을
   `skills/<name>/SKILL.md`에 두고 공통 Agent Skills frontmatter를 쓴다.
3. **임시 `HOME`에서 검증:** 프로젝트의 설치 절차를 따른 뒤 `omp skill list`에서
   스킬과 `warning:` 줄을 확인한다. 관련 요청을 따로 실행해 로딩과 동작을 확인한다.

## 주의할 점

- 허용적인 스캐너가 받아 준다는 이유로 omp의 `hide`, `globs`, `alwaysApply`나 다른
  클라이언트의 확장을 넣지 않는다.
- 수동 명령, 파일 범위 규칙, 실행 시 강제는 해당 omp 구성 요소가 필요하다. 스킬
  텍스트로는 제공되지 않는다.
- 지원 파일은 스킬 디렉터리 안에 두고 `skill://<name>/<path>`로 읽는다. 설치 캐시
  경로를 스킬에 적지 않는다.
- 파일을 읽을 수 있다는 것은 발견의 증거가 아니다.
- 카탈로그 필드, 버전, 게시는 해당 프로젝트가 관리한다. 패키징이 범위에 있을 때만
  [마켓플레이스 가이드][marketplaces]를 읽는다.

[skills]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills.md
[marketplaces]: https://github.com/can1357/oh-my-pi/blob/main/docs/skills/authoring-marketplaces.md
