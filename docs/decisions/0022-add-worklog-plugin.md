# ADR 0022: 세 호스트 공용 작업 로그 worklog

- 날짜: 2026-10-05
- 상태: 채택
- 관련 결정: [ADR 0003](0003-keep-plugins-independent.md), [ADR 0016](0016-support-claude-code.md),
  [ADR 0017](0017-use-shared-local-memory.md)

## 배경

Claude Code·Codex·omp에서 같은 스킬을 쓰지만, 어떤 도구 호출이 실패했고 사용자가 어디서 결과를
고쳤는지는 호스트마다 다른 transcript에 흩어져 있다. 반복되는 실패를 지침 개선으로 잇거나
원인을 진단하려면 세 호스트에서 같은 형식으로 모은 기록이 필요하다. 호스트가 주는 신호도 다르다.
Claude Code는 실패 전용 hook(`PostToolUseFailure`, `StopFailure`)이 있다. Codex는 실패한 명령도
`PostToolUse`로 보내며 exit code는 rollout에만 남는다. omp는 hook 대신 runtime extension의
`tool_result` 이벤트로 결과를 알린다.

## 결정

- 새 플러그인 `worklog`를 둔다. memory-manager는 사람이 승인한 지식을, worklog는 가공하지 않은
  작업 이벤트를 다루므로 목적이 다르다([ADR 0017](0017-use-shared-local-memory.md)). 두 플러그인은
  서로 의존하지 않고, 비밀 정규식과 프로젝트 키 계산은 복사해 같은 값을 유지한다
  ([ADR 0003](0003-keep-plugins-independent.md)).
- 로그 계약 `worklog-v1`을 세 호스트가 공유한다. 경로는
  `<root>/<project_key>/<host>/<YYYY-MM-DD>/<session_id>.jsonl`이고 기본 `<root>`는
  `~/.sonsu/worklog`다. 보존 기간은 90일이다. 계약 표는
  [plugins/worklog/README.md](../../plugins/worklog/README.md)가 정본이다.
- 기록은 호스트별로 구현한다. Claude Code와 Codex는 hook 정의를 따로 둔다(이벤트 집합이 다르다).
  Codex 실패는 `Stop` 시점에 rollout에서, Claude Code의 SessionStart hook 출력은 첫 `Stop`에서
  transcript로 보충한다. omp는 extension 하나로 기록한다.
- **omp 배포 정책 예외**: 기본 6개 묶음은 유지한다. omp 카탈로그에 opt-in 패키지를 허용하고,
  그 패키지에 한해 runtime extension을 허용한다. 현재 opt-in 패키지는 worklog뿐이며 hook은
  배포하지 않는다.
- 기록 도구는 컨텍스트를 주입하지 않고, 결과를 바꾸지 않으며, 실패해도 작업을 막지 않는다
  (fail-open). 진단 스킬 `worklog-diagnose`는 읽기 전용이다.

## 대안

- **memory-manager에 추가**: 저장 위치와 hook을 공유할 수 있지만, 승인된 지식 저장소에 원시
  이벤트가 섞이고 memory-manager 설치가 로그 수집 동의로 바뀐다.
- **OpenTelemetry 내보내기**: 표준 형식이지만 collector를 따로 운영해야 하고, Codex는 사용자
  레벨 설정에서만 켤 수 있다(https://learn.chatgpt.com/docs/config-file/config-advanced).
- **transcript만 파싱**: hook 없이 구현할 수 있지만, 두 호스트 모두 transcript를 안정 인터페이스로
  약속하지 않는다. 보조 신호로만 쓴다.

## 결과

- 실제 호스트가 hook·extension을 로드하는지, Codex hook 신뢰가 업데이트 뒤에 유지되는지는 단위
  테스트로 확인할 수 없으며 호스트별 실행으로 따로 확인한다([evals/worklog](../../evals/worklog/README.md)).
- omp 생성기는 opt-in 패키지에 `package.json`과 `extension/`을 생성한다. 기본 6개 패키지에는
  여전히 hook·extension이 없다.
- 설치하면 모든 프로젝트에서 기록하므로 끄는 방법(`SONSU_WORKLOG=off`, 프로젝트 `disabled` 파일)과
  프롬프트 발췌 끄기(`SONSU_WORKLOG_PROMPTS=off`)를 README에 둔다.

## 다시 볼 때

- Codex가 실패 전용 hook이나 exit code를 담은 hook 입력을 제공할 때
- omp가 공식 작업 로그 기능을 제공할 때
