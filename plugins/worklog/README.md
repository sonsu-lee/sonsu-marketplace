# Worklog

Claude Code·Codex·omp 작업의 도구 실패·중단·API 오류·사용자 교정을 프로젝트별 로컬 JSONL로 기록하고, 원문 transcript와 대조해 원인을 진단하거나 명시적으로 요청한 지침 수정안을 평가합니다.

기록은 Claude Code와 Codex에서는 plugin hook이, omp에서는 runtime extension이 맡습니다. 기록 도구는 컨텍스트를 주입하지 않고 hook stdout을 비워 두며, 실패해도 작업을 계속 진행합니다(fail-open). memory-manager는 사람이 승인한 지식을, worklog는 가공하지 않은 작업 이벤트를 다루며 두 플러그인은 서로 독립적입니다([ADR 0022](../../docs/decisions/0022-add-worklog-plugin.md)).

## 설치

설치 이름은 세 호스트 모두 `worklog`입니다. 설치하면 모든 프로젝트에서 기록합니다.

```sh
codex plugin add worklog@sonsu-marketplace
claude plugin install worklog@sonsu-marketplace
omp plugin install worklog@sonsu-marketplace
```

omp에서는 opt-in 패키지이므로 필요할 때 직접 설치합니다. omp 패키지는 두 스킬과 `extension/worklog.ts`를 담습니다. Claude Code 배포본은 `scripts/render-claude-compat.py`가 내부 `claude/`에 생성하며 `hooks/claude-hooks.json`을 Claude용 `hooks/hooks.json`으로 복사합니다. 정본을 고친 뒤 생성기로 갱신합니다.

Codex는 사용자가 `/hooks`에서 신뢰한 plugin hook만 실행합니다. 설치 뒤와 업데이트 뒤에 `/hooks`에서 worklog hook을 신뢰합니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| [`worklog-diagnose`](skills/worklog-diagnose/SKILL.md) | 최근 실패·중단·교정의 원인을 알고 싶을 때 | 근거 위치가 붙은 타임라인, 실패별 원인 후보, 다음 확인 사항 |
| [`worklog-improve`](skills/worklog-improve/SKILL.md) | 반복 실패를 평가 사례로 고정하고 지침 수정안을 비교해 달라고 명시적으로 요청할 때 | 사례, 최소 diff, 기준선·후보·회귀 판정과 사람 검토용 인계 |

`worklog-improve`는 Claude Code에서 수동 호출 전용(`disable-model-invocation: true`)으로 배포하며, Codex·omp에서도 같은 명시적 요청 조건으로 사용합니다. 평가 사례와 비식별 fixture만 원래 작업 디렉터리에 추가하고 후보 diff는 임시 worktree에서 비교합니다. 단계별 상한과 통과 조건은 [평가와 인계](skills/worklog-improve/references/evaluation.md)와 `scripts/validate_improvement.py`가 정본이며, 이 저장소의 생성·검사·게시 인계는 [운영 절차](../../docs/runbooks/improving-skills-from-worklog.md)를 따릅니다.

## 사용 예시

요청: "이번 주에 반복된 권한 거부가 무엇 때문인지 정리해 줘."

`worklog-diagnose`가 `summary --days 7`과 `failures`로 `permission_denied` 레코드를 찾고 transcript의 해당 `tool_use_id` 주변을 읽어 다음처럼 보고합니다.

```text
- 09:14 claude permission_denied Write .env [worklog: <log>:22] [transcript: <path> toolu_7]
  원인 후보: 환경·권한(높음) — 프로젝트 권한 설정이 .env 쓰기를 거부했다.
- 다음에 확인할 것: 해당 쓰기가 작업에 필요했는지와 프로젝트 권한 설정
```

## 구성

### 로그 계약 `worklog-v1`

| 항목 | 값 |
| --- | --- |
| 경로 | `<root>/<project_key>/<host>/<YYYY-MM-DD>/<session_id>.jsonl` |
| `<root>` | `SONSU_WORKLOG_HOME`(절대 경로), 없으면 `~/.sonsu/worklog`. symlink 조상이 있으면 쓰지 않음 |
| `<host>` | `claude`, `codex`, `omp` |
| 날짜 | 세션의 첫 기록 시점(UTC). 보존 기간이 지난 세션을 재개하면 현재 날짜의 새 파일로 기록 |
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

`user_prompt`의 `correction_hint`는 프롬프트에 "아니야", "다시 해", "wrong", "undo" 같은 한국어·영어 교정 표현이 있으면 `true`입니다. 표현 목록은 `scripts/worklog.py`의 `CORRECTION_RE`에 있습니다. 표현 일치만 보는 신호이므로 실제 교정 여부는 transcript로 확인합니다.

#### 기록하지 않는 것

- 도구 출력 전문과 프롬프트 전문. 실패 메시지는 첫 의미 줄, 입력은 명령이나 파일 경로의
  앞부분, 프롬프트는 160자 발췌만 남깁니다.
- 비밀값. `excerpt`·`error`·`input_excerpt`·`reason`·`error_details`·hook `command`에서 memory-manager와 같은
  비밀 정규식에 맞는 부분을 `[redacted]`로 바꿉니다. 정규식이 모든 비밀을 찾는다고 보장하지는
  않으므로 로그 디렉터리는 개인 파일로 다룹니다(디렉터리 0700, 파일 0600).

### 끄기와 보존

- `SONSU_WORKLOG`가 `off`·`0`·`false`이면 아무것도 쓰지 않습니다.
- `<root>/<project_key>/disabled` 파일이 있으면 그 프로젝트는 쓰지 않습니다. 경로는
  `python3 scripts/worklog.py where`로 확인합니다.
- `SONSU_WORKLOG_PROMPTS=off`이면 프롬프트 발췌 없이 길이만 남깁니다.
- 보존 기간은 90일입니다. 세션 시작 때 그 프로젝트·호스트의 날짜 디렉터리 중 90일이 지난 것을
  지우며, 24시간에 한 번만 정리하고 시각을 `<host>/.state/last-prune`에 남깁니다.
  세션 상태와 잠금 파일은 지우지 않습니다. 진행 중인 기록의 잠금과 rollout 읽기 위치를 보존하기 위해서입니다.
  만료된 날짜는 재개 시 현재 날짜로 바꾸고 시작 메타데이터를 다시 남깁니다. rollout 읽기 위치는 유지합니다.
  `python3 scripts/worklog.py prune [--days 90]`은 모든 호스트를 즉시 정리합니다.
- 로그가 가리키는 Claude Code transcript는 Claude Code 설정 `cleanupPeriodDays`(기본 30일)에 따라
  먼저 지워질 수 있습니다. 이때 진단은 "원문 없음"으로 보고합니다.
- 로그 경로의 어느 디렉터리 성분이든 symlink이면 기록·보존 정리를 거부합니다. omp의 새 세션·재개·분기
  이벤트에서는 세션 ID와 transcript 연결을 새로 읽습니다.

### 조회

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

### 알려진 한계

- Claude Code의 보안 샌드박스 차단은 `PostToolUseFailure`로 오지 않습니다(로컬 실험).
- Claude Code에는 사용자 중단을 알리는 hook 이벤트가 없어 `interrupt`를 기록하지 않습니다.
- Codex는 실패한 명령도 `PostToolUse`로 보내고 exit code를 주지 않습니다. 실패 판정은 `Stop`
  시점에 rollout에서 합니다. 세션이 `Stop` 없이 끝나면 마지막 턴의 실패는 남지 않습니다.
- omp는 `user_prompt`를 기록하지 않으며 `host_version`은 항상 `null`입니다.
- transcript·rollout 형식은 호스트가 안정 인터페이스로 약속하지 않았습니다. 형식이 바뀌면
  해당 보조 기록만 빠지고 hook 기록은 계속됩니다.

## 검증

```sh
python3 -B -m unittest discover -s evals/worklog -p 'test_*.py' -v
python3 -B -m unittest -v plugins/worklog/tests/test_validate_improvement.py
node --experimental-strip-types --test evals/worklog/test_omp.mjs
```

실제 호스트 확인과 개선 루프 행동 사례는 [evals/worklog](../../evals/worklog/README.md)에 있습니다.
