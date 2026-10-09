# Worklog 평가

`test_worklog.py`는 임시 `SONSU_WORKLOG_HOME`과 `git init`한 임시 프로젝트에서
`plugins/worklog/scripts/worklog.py`를 하위 프로세스로 실행해 다음을 확인합니다. 실제 사용자
로그는 fixture로 사용하지 않습니다.

- Claude `PostToolUseFailure`의 exit code와 첫 의미 줄 분리
- Codex `Stop`의 rollout 실패 항목 기록과 중복 방지(미완성 마지막 줄은 다음 `Stop`에서 처리)
- Codex `PostToolUse`의 `outcome: unknown`
- 프롬프트 발췌의 비밀 치환, 교정 표시, `SONSU_WORKLOG_PROMPTS=off`
- `SONSU_WORKLOG` 끄기와 프로젝트 `disabled` 파일
- memory-manager `project_key()`와 같은 프로젝트 키
- 보존 기간 정리와 24시간 정리 간격
- 잘못된 stdin에서 exit 0, 출력 없음
- Claude transcript의 SessionStart hook 출력 1회 기록
- `summary`·`failures` 출력 형식
- 두 hook 정의 파일의 호스트별 이벤트 집합과 `--host` 인자
- 로그 하위 symlink를 통한 외부 기록 차단, hook command의 비밀 치환, 만료 세션 재개 시 날짜 갱신과 offset 보존

```sh
python3 -B -m unittest discover -s evals/worklog -p 'test_*.py' -v
```

`test_omp.mjs`는 Node.js 22.6+의 TypeScript 실행 기능으로 정본 extension의 이벤트 핸들러를
호출합니다. 새 세션·재개·분기의 ID와 transcript 연결, symlink 대상의 기록·삭제 차단,
만료 세션의 날짜 갱신을 임시 디렉터리에서 확인합니다.

```sh
node --experimental-strip-types --test evals/worklog/test_omp.mjs
```

## Fixture

- `fixtures/codex-rollout.jsonl`: 실제 Codex 0.160.0 `codex exec` rollout에서 `session_meta`
  1줄(`timestamp`, `type`, `payload.cli_version`만)과 `item_completed` 2줄(`echo hi` 성공,
  `ls ./no-such-file-xyz` 실패)만 남겼습니다. item은 `type`, `id`, `status`, `exit_code`,
  `aggregated_output`, `stdout`, `stderr`, `command`, `duration`과 `payload.turn_id`만 보존합니다.
- `fixtures/claude-transcript.jsonl`: 합성. Claude Code transcript의 `version` 레코드 1줄,
  SessionStart `hook_success`(stdout 1,000자) 1줄, `hook_additional_context` 1줄입니다. attachment
  필드 구조는 실제 Claude Code transcript에서 확인한 것을 따릅니다.
- `fixtures/claude-post-tool-use-failure.json`: 합성. 로컬 실험에서 관찰한 `PostToolUseFailure`
  필드(`error`, `is_interrupt`, `duration_ms`)를 사용합니다.

## 실제 호스트 확인

이 단위 테스트는 실제 호스트가 hook·extension을 로드하고 호출하는지, Codex hook 신뢰가 어떻게
적용되는지, omp extension이 Python과 같은 프로젝트 키를 계산하는지를 대신하지 않습니다.
Claude Code(`--plugin-dir`), Codex(임시 `CODEX_HOME`), omp(`-e`)에서 실패 명령을 한 번 실행하고
`failures`·`summary`로 기록을 따로 확인합니다. macOS에서 `SONSU_WORKLOG_HOME`은 symlink 조상이
없는 실제 경로(`/private/tmp/...`)여야 합니다. 실행하지 못한 항목은 `not_run`, 원인을 특정할 수
없는 결과는 `inconclusive`로 보고합니다.
