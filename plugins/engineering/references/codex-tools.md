# Codex 기본 하네스 대응

현재 노출된 도구 스키마를 읽고 [실행 계약](agent-execution.md)을 적용한다. 플러그인은 작업
계약과 품질 전이를 소유하며 기본 실행 루프·세션 관리·권한 도구를 다시 구현하지 않는다.

- 독립 리뷰는 이전 이력을 전달하지 않는 `fresh`로 실행한다. 지원하면
  `spawn_agent(fork_turns="none", model=..., reasoning_effort=...)`를 사용한다.
  전체 이력 fork와 모델 override의 조합을 추측하지 않는다.
- 같은 작업의 수정은 `followup_task` 등 현재 지원되는 재개를 사용한다. 새 문맥이 필요하면
  계약·현재 소스·유효 지적·관찰 결과·남은 라운드를 전달한다.
- root가 할당한다. worker는 추가 할당 요청을 root로 반환한다. 지원하지 않는 종료/대기 API를
  만들지 않는다. 완료 이벤트를 기다리고 독립 로컬 작업이 있으면 진행한다.
- 현재 프로젝트·세션에서 역할이 실제로 발견되고 선택 가능한지 확인한 뒤 해당 Codex 역할을
  사용한다. host가 이름 선택을 지원한다는 사실만으로 프로젝트 역할이 로드됐다고 가정하지
  않는다. untrusted 프로젝트처럼 `.codex/` 설정 계층이 로드되지 않거나 역할 선택이 실패하면
  프로젝트 역할 정의를 읽어 그 경계를 작업별 brief에 포함하고 모델 프로필을 호출 인자로
  전달한다. 플러그인 설치만으로 소비자 프로젝트에 역할 파일이 생긴다고 가정하지 않으며,
  native 역할이 선택됐다고 주장하지 않는다.
  이 fallback은 agent 파일의 `sandbox_mode`를 적용하지 않으므로 실제 상속된 권한과 brief의
  읽기 전용 지침을 구분해 기록한다.
- 기본 세션 동작과 gate 상태를 구분한다. `Stop`은 관찰 알림이며 현재 증거를 통과시키거나
  모든 임의 명령을 차단하지 않는다. 등록 unit은 `enter`/`complete-unit`의 거부를 따른다.
- 사용자 설정 파일을 작업마다 수정하지 않는다. 실행 도구가 선택 프로필을 지원하지 않으면
  지원되는 동등 수단을 확인하고 명시 모델 조건을 충족할 수 없을 때 해당 실행을 `blocked`로 둔다.

정확한 역할별 model+effort와 검증 날짜는 [생성된 프로필](model-profiles.md)에
있다. 모델 API 문서의 effort 값이나 pro 모드를 Codex native 설정으로 그대로 옮기지 않는다.
호스트 업데이트는 지원 스키마·상속·완료 이벤트를 확인한 뒤 대표 행동 평가로 채택한다.

Code Mode에서는 독립 검색·읽기·파싱·검사를 묶고 수정과 의존 작업은 순차 처리한다.
같은 명령을 반복 호출하는 대신 결과를 프로그램으로 판정한다. AI는 해당 결과로 작업 경로를
결정한다. 전체 도구 호출을 감시하는 별도 scheduler는 추가하지 않는다.

사용자가 goal을 명시 요청한 경우에만 goal 도구를 사용한다. 모든 필수 현재 근거를 충족해야
완료이며 토큰/시간 소진은 완료가 아니다. Git·배포 권한은 모델/하네스 기능과 별개다.

근거: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform),
[Hooks](https://learn.chatgpt.com/docs/hooks).
