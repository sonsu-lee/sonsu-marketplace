# Worklog

Claude Code·Codex·omp 작업에서 일어난 도구 실패, 중단, API 오류, 사용자 교정을 프로젝트별
로컬 JSONL 로그로 남기고, `worklog-diagnose` 스킬로 그 기록과 원문 transcript를 대조해 원인
후보를 정리합니다. 세 호스트가 같은 로그 계약(`worklog-v1`)과 같은 저장 위치를 씁니다.

- **기록**: Claude Code와 Codex는 plugin hook이, omp는 runtime extension이 기록합니다.
  기록 도구는 컨텍스트를 주입하지 않고, hook stdout에 아무것도 쓰지 않으며, 실패해도 작업을
  막지 않습니다(fail-open).
- **진단**: `worklog-diagnose`는 로그와 transcript를 읽기만 하고 파일을 수정하지 않습니다.
- **조회 도구**: `scripts/worklog.py`의 `where`, `summary`, `failures`, `clusters`, `prune`. Python 3.9+
  표준 라이브러리만 사용합니다.
- **개선안 비교**: 명시적으로 요청한 `worklog-improve`가 평가 사례와 최소 diff를 만들고,
  임시 worktree에서 수정 전후를 비교합니다. 원래 작업 디렉터리의 지침에 자동 적용하지 않습니다.

memory-manager는 사람이 승인한 지식을, worklog는 가공하지 않은 작업 이벤트를 다룹니다.
두 플러그인은 서로 의존하지 않습니다([ADR 0021](../../docs/decisions/0021-add-worklog-plugin.md)).

## 설치

설치 이름은 세 호스트 모두 `worklog`입니다. 설치하면 모든 프로젝트에서 기록합니다.

```sh
codex plugin add worklog@sonsu-marketplace
claude plugin install worklog@sonsu-marketplace
omp plugin install worklog@sonsu-marketplace
```

omp에서는 기본 5개 묶음에 들어 있지 않은 opt-in 패키지이므로 필요한 경우에만 직접 설치합니다.
omp 패키지는 진단·개선 스킬과 `extension/worklog.ts`를 함께 담고 hook은 담지 않습니다.
Claude Code 배포본은 `scripts/render-claude-compat.py`가 내부 `claude/`에 생성하며,
`hooks/claude-hooks.json`을 Claude용 `hooks/hooks.json`으로 복사합니다. 생성물은 직접 고치지
않습니다.

Codex는 plugin hook을 사용자가 `/hooks`에서 신뢰해야 실행합니다. 설치 뒤 `/hooks`에서
worklog hook을 신뢰하세요. 플러그인을 업데이트한 뒤에는 `/hooks`에서 다시 신뢰해야 할 수 있습니다.

## 로그 계약 `worklog-v1`

| 항목 | 값 |
| --- | --- |
| 경로 | `<root>/<project_key>/<host>/<YYYY-MM-DD>/<session_id>.jsonl` |
| `<root>` | `SONSU_WORKLOG_HOME`(절대 경로), 없으면 `~/.sonsu/worklog`. symlink 조상이 있으면 쓰지 않음 |
| `<host>` | `claude`, `codex`, `omp` |
| 날짜 | 그 세션의 첫 기록 시점(UTC). 한 세션의 기록은 한 파일에 모임 |
| `project_key` | memory-manager `project_key()`와 같은 값. Git 공통 디렉터리(Git 밖이면 현재 디렉터리)의 실제 경로 sha256 앞 20 hex |
| 프로젝트 표지 | `<root>/<project_key>/project.json`에 `{"identity", "created"}`를 한 번 기록 |
| `session_id` | `[A-Za-z0-9._-]{1,128}`가 아니면 sha256 앞 32 hex, 없으면 `unknown` |
| 레코드 | 한 줄에 JSON 하나 |

모든 레코드는 다음 키를 가집니다. `host_version`은 알아내기 전까지 `null`입니다.

```json
{"schema":"worklog-v1","ts":"<UTC ISO8601 ms>","host":"claude|codex|omp","host_version":"<str>|null","session_id":"<str>","project_key":"<20hex>","cwd":"<abs>","turn_id":"<str>|null","event":"<event>","signal_source":"<source>","data":{}}
```

| `event` | `data` 키 |
| --- | --- |
| `session_start` | `source`, `transcript_path`, `model`, `agent_kind` |
| `context_load` | `kind`(`instructions`·`hook_output`), `file_path`, `memory_type`, `load_reason`, `bytes`, `hook_name`, `command`, `chars` (해당 kind에 있는 키만) |
| `user_prompt` | `chars`, `excerpt`(160자, 비밀 치환, `SONSU_WORKLOG_PROMPTS=off`면 생략), `correction_hint`(bool) |
| `tool_result` | `outcome`(`ok`·`failed`·`unknown`), `tool_name`, `tool_use_id`, `exit_code`, `error`(첫 의미 줄 300자), `is_interrupt`, `duration_ms`, `input_excerpt`(200자) |
| `permission_denied` | `tool_name`, `tool_use_id`, `reason`(300자) |
| `interrupt` | `{}` |
| `stop` | `last_message_chars` |
| `stop_failure` | `error`, `error_details`(300자) |
| `subagent_stop` | `agent_id`, `agent_type`, `agent_transcript_path` |
| `compact` | `trigger` |
| `session_end` | `reason` |

`tool_result`는 위 키를 유지하고 호스트가 제공하지 않은 값은 `null`로 둡니다. omp의 `input_excerpt`는 실패 때만 채웁니다.
`signal_source`는 `hook:<HookEventName>`, `rollout:item_completed`, `transcript:attachment`,
`omp:<event>` 중 하나입니다.

| 호스트 | 출처 | 기록하는 event |
| --- | --- | --- |
| Claude Code | hook | `SessionStart`, `InstructionsLoaded`, `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, `PermissionDenied`, `Stop`, `StopFailure`, `SubagentStop`, `PreCompact`, `SessionEnd` |
| Claude Code | transcript | 첫 `Stop`에서 transcript 앞 2MB를 읽어 SessionStart hook 출력(`hook_success`·`hook_additional_context`)을 `context_load`로, 처음 보이는 `version`을 `host_version`으로 기록 |
| Codex | hook | `SessionStart`, `UserPromptSubmit`, `PostToolUse`(`outcome: unknown`), `Stop`, `SubagentStop`, `PreCompact`, `Interrupt`, `SessionEnd` |
| Codex | rollout | `Stop`마다 지난번 위치 이후의 완성된 줄에서 `status: failed`인 `item_completed`를 `tool_result failed`로 기록. `host_version`은 rollout 첫 줄의 `cli_version` |
| omp | extension | `session_start`, `tool_result`, `agent_end`(→ `stop`), `session_shutdown`(→ `session_end`) |

`user_prompt`의 `correction_hint`는 프롬프트가 다음 정규식에 맞으면(대소문자 무시) `true`입니다.

```text
(아니(?:야|라|요|고)|그게 아니|그거 말고|다시 해|잘못|틀렸|되돌려|원래대로|wrong|that's not|not what i|undo|revert)
```

### 기록하지 않는 것

- 도구 출력 전문과 프롬프트 전문. 실패 메시지는 첫 의미 줄, 입력은 명령이나 파일 경로의
  앞부분, 프롬프트는 160자 발췌만 남깁니다.
- 비밀값. `excerpt`·`error`·`input_excerpt`·`reason`·`error_details`에서 memory-manager와 같은
  비밀 정규식에 맞는 부분을 `[redacted]`로 바꿉니다. 정규식이 모든 비밀을 찾는다고 보장하지는
  않으므로 로그 디렉터리는 개인 파일로 다룹니다(디렉터리 0700, 파일 0600).

## 끄기와 보존

- `SONSU_WORKLOG`가 `off`·`0`·`false`이면 아무것도 쓰지 않습니다.
- `<root>/<project_key>/disabled` 파일이 있으면 그 프로젝트는 쓰지 않습니다. 경로는
  `python3 scripts/worklog.py where`로 확인합니다.
- `SONSU_WORKLOG_PROMPTS=off`이면 프롬프트 발췌 없이 길이만 남깁니다.
- 보존 기간은 90일입니다. 세션 시작 때 그 프로젝트·호스트의 날짜 디렉터리 중 90일이 지난 것을
  지우며, 24시간에 한 번만 정리하고 시각을 `<host>/.state/last-prune`에 남깁니다.
  세션 상태와 잠금 파일은 지우지 않습니다. 진행 중인 기록의 잠금과 rollout 읽기 위치를 보존하기 위해서입니다.
  `python3 scripts/worklog.py prune [--days 90]`은 모든 호스트를 즉시 정리합니다.
- 로그가 가리키는 Claude Code transcript는 Claude Code 설정 `cleanupPeriodDays`(기본 30일)에 따라
  먼저 지워질 수 있습니다. 이때 진단은 "원문 없음"으로 보고합니다.

## 조회

```sh
python3 scripts/worklog.py where
python3 scripts/worklog.py summary [--days 7] [--host claude|codex|omp] [--format text|json]
python3 scripts/worklog.py failures [--days 14] [--format jsonl]
python3 scripts/worklog.py clusters [--days 14] [--min-count 2] [--format json|text]
python3 scripts/worklog.py prune [--days 90]
```

모든 명령은 `--cwd`(기본값: 현재 디렉터리)로 프로젝트를 정합니다. `failures`는 실패한
`tool_result`, `stop_failure`, `permission_denied`, `interrupt`, 교정 표시가 있는 `user_prompt`를
내고 각 줄에 `log_path`, `line`(1부터), 그 세션의 `transcript_path`를 붙입니다.

`clusters`는 `failures`와 같은 레코드를 묶고, 최소 건수와 서로 다른 세션 ID 2개 이상을
만족하는 묶음만 반환합니다. 기본 출력은 JSON 배열이며 count 내림차순, 같으면 last_ts
내림차순입니다. 각 객체에는 `signature`, `count`, `sessions`(세션 ID 배열), `hosts`(호스트
배열), `first_ts`, `last_ts`, `examples`(최대 5개)가 있습니다. 예시는 `log_path`, `line`,
`transcript_path`, `tool_use_id`로 원본을 가리키며 원문 내용을 복제하지 않습니다.

실패 signature는 `tool_name|normalize(error)`, 교정은 `user_correction|normalize(excerpt)`입니다.
도구 이름이 없는 이벤트는 이벤트 이름을, `permission_denied`의 오류는 `reason`을 사용합니다.
정규화는 비밀 치환 뒤 소문자화 → `/\S+` 절대 경로를 `<path>`로 치환 → 8자 이상 hex·UUID를
`<id>`로 치환 → 숫자열을 `N`으로 치환 → 공백 합치기 → 120자 자르기 순입니다. 프롬프트 발췌를
끄면 교정 signature 본문이 비어 있으므로, 묶음만 보고 같은 원인이라고 판단하지 않습니다.

## 명시적으로 요청하는 개선 루프

`worklog-improve`는 자동 진단의 다음 단계가 아닙니다. 사용자가 평가 사례·수정안 비교를
명시적으로 요청했을 때만 한 묶음을 처리합니다. Claude Code에서는 수동 호출 전용
(`disable-model-invocation: true`)으로 배포하고, Codex·omp에서도 같은 요청 조건을 지킵니다.

1. 반복 신호를 고르고 transcript로 저장소 안의 원인 지침을 특정합니다. 신호가 없으면
   `no_signal`, 지침을 특정할 수 없으면 `inconclusive`로 끝냅니다.
2. 기존 `evals/<plugin>/cases.json`의 스키마로 사례 하나를 추가하고
   `origin: worklog:<host>:<session_id>:<ts>`를 남깁니다. 빈 스위트도 선언된 스키마를 따릅니다.
   스위트가 없으면 로그 프로젝트 디렉터리의 `improve/<case-id>.json`에 저장합니다.
3. 현재 지침으로 3회 기준선을 실행합니다. 관찰자와 별도인 새 컨텍스트 제안자가 항목 단위
   최소 diff를 만듭니다. 순증가 15줄을 넘으면 사용자 승인을 기다립니다.
4. 임시 worktree에서 후보를 3회, 같은 스킬의 기존 회귀 사례 최대 5개를 비교합니다. 실행자는
   기대 항목을 보지 않습니다. 결정적 검사 후 새 컨텍스트 비교자가 무작위 A/B를 판정합니다.
5. 수정 후 2/3 이상이면서 기준선보다 높고 회귀 통과 수가 줄지 않아야 통과합니다. 후보는
   최대 3개이며 결과표·사례·diff를 사람이 검토하도록 넘깁니다.

사례·비식별 fixture 작성은 허용하지만 후보 diff는 원래 작업 디렉터리에 적용하지 않습니다.
커밋·PR은 따로 요청받았을 때만 Workflow로 넘깁니다. 각 단계의 상한과 중단 조건은
[스킬](skills/worklog-improve/SKILL.md), 이 저장소의 생성·검사·게시 인계 절차는
[운영 절차](../../docs/runbooks/improving-skills-from-worklog.md)에 있습니다.

## 알려진 한계

- Claude Code의 보안 샌드박스 차단은 `PostToolUseFailure`로 오지 않습니다(로컬 실험).
- Claude Code에는 사용자 중단을 알리는 hook 이벤트가 없어 `interrupt`를 기록하지 않습니다.
- Codex는 실패한 명령도 `PostToolUse`로 보내고 exit code를 주지 않습니다. 실패 판정은 `Stop`
  시점에 rollout에서 합니다. 세션이 `Stop` 없이 끝나면 마지막 턴의 실패는 남지 않습니다.
- omp는 `user_prompt`를 기록하지 않으며 `host_version`은 항상 `null`입니다.
- transcript·rollout 형식은 호스트가 안정 인터페이스로 약속하지 않았습니다. 형식이 바뀌면
  해당 보조 기록만 빠지고 hook 기록은 계속됩니다.

검증 방법은 [evals/worklog](../../evals/worklog/README.md)에 있습니다.
