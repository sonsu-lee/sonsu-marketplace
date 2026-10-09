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
- `clusters`의 경로·hex·UUID·숫자 정규화, 세션 2개 이상 조건, 빈 결과·기간·최소 건수,
  count/last_ts 정렬, 최대 5개 예시와 원본 위치 연결

```sh
python3 -B -m unittest discover -s evals/worklog -p 'test_*.py' -v
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

## 개선 루프 행동 사례

[improve-cases.json](improve-cases.json)은 memory-manager 사례와 같은 `id`, `request`, `files`,
`setup`, `expected` 형식을 사용합니다. 현재 상태는 모두 `not_run`입니다. 단위 테스트 통과가
이 사례의 실행을 뜻하지 않습니다.

각 사례마다 새 임시 Git 프로젝트와 symlink 조상이 없는 절대 경로의 `SONSU_WORKLOG_HOME`을
준비합니다. `files`를 만들고 `setup`을 수행한 뒤, 새 컨텍스트에 요청과 `worklog-improve`
스킬만 전달합니다. `expected`는 평가자에게만 주며 실행자의 fixture에도 노출하지 않습니다.
개선 루프 안의 실행자·제안자·비교자도 각각 별도 대화 이력을 사용합니다.

| 사례 | 관찰할 계약 |
| --- | --- |
| `no-signal-stops` | 빈 로그에서 `no_signal`, 사례·diff·커밋·PR 없음 |
| `unattributable-stops-inconclusive` | 반복 기록은 있으나 원인 지침을 특정할 수 없으면 `inconclusive`, 추정 수정 없음 |
| `repeated-failure-produces-case-and-diff` | 빈 스위트의 선언 스키마와 origin을 보존한 사례 1개, 최소 diff, 기준선/후보/회귀 결과표, 원래 스킬·커밋 수 불변 |
| `swapped-regression-results-reject-candidate` | 새 사례가 개선되고 회귀 통과 합계가 같아도 기존 통과 사례 A가 실패하면 후보를 거부 |

판정은 `pass|fail|not_run|inconclusive`로 기록합니다. `no_signal`은 첫 사례에서 기대하는
동작 상태이며 평가 결과의 `pass`와 구분합니다. 새 컨텍스트 실행이나 블라인드 비교를 수행하지
못하면 성공으로 추정하지 않고 `not_run`으로 남깁니다. 생성물·공통 검사 명령과 PR 인계는
[운영 절차](../../docs/runbooks/improving-skills-from-worklog.md)를 따릅니다.
