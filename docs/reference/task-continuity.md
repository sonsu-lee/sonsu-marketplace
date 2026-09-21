# 작업 연속성 계약

`shared/task-continuity/profiles.json`에 등록된 플러그인은 각각
`task-continuity` 스킬과 `SessionStart` hook을 포함합니다. 여러 단계의 작업을
기록하고 컴팩션·같은 session 재개 후 현재 근거와 대조합니다. 짧은 단발 작업과 다른 작업의
구성·표현만 담당하는 Writing·Fluent에는 별도 기록을 만들지 않습니다.

각 플러그인은 단독으로 설치할 수 있습니다. 공통 runtime과 스킬 본문은
[`shared/task-continuity/`](../../shared/task-continuity/)를 정본으로 삼고
[`scripts/render-continuity.py`](../../scripts/render-continuity.py)가 패키지 내부로 복사합니다.
설치된 패키지는 다른 플러그인이나 저장소 root를 읽지 않습니다. domain별 보존 항목과 trigger는
정본의 `profiles.json`에서 관리합니다.

## 실행 환경과 저장 위치

저장 helper는 Python 3.9+의 표준 라이브러리를 사용하며 POSIX(macOS/Linux)를 대상으로 합니다.
네트워크, 모델 호출, 별도 DB나 daemon이 없습니다. Windows native 실행은 이 버전의 지원 범위에
포함하지 않으며 Windows 환경에서는 스킬의 원문·현재 상태 대조 절차를 수동으로 적용합니다.

```text
<current-worktree-root>/.sonsu/continuity/<session-id>/<plugin>.json
<current-worktree-root>/.sonsu/continuity/<session-id>/history/<plugin>/<task-id>.<revision>.json
```

Git 밖에서는 현재 작업 디렉터리의 실제 경로를 root로 사용합니다. linked worktree는 자기 root를
사용합니다. session은 명시한 `--session-id`를 우선하고, 생략하면 `CODEX_THREAD_ID`를 읽습니다.
ID를 알 수 없으면 다른 session이나 최신
디렉터리를 검색하지 않습니다. `--cwd`가 다르면 기존 기록을
자동 이동하거나 다른 worktree에서 찾아오지 않습니다. subagent와 fresh reviewer는 기록 소유자가 아닙니다.
hook은 event에 포함된 session ID로 기존 기록을 조회합니다. ID를 별도로 저장하는 startup hook은
필요하지 않으며, host가 정확한 ID를 제공하지 않으면 `--session-id`를 추측하지 않습니다.

최초 쓰기 전에 Git의 `info/exclude`에 `/.sonsu/continuity/` 한 줄이 있는지 확인하고 없을 때 추가합니다. 기존 바이트와
다른 규칙은 보존하며 tracked `.gitignore`는 수정하지 않습니다. linked worktree가 공유하는
exclude 변경은 파일 lock으로 직렬화하고 lock 안에서 규칙을 다시 확인합니다. 이미 규칙이 있으면
쓰기를 요청하지 않습니다. `.git` 쓰기를 제한하는 sandbox에서는 실행 환경 준비 단계에서 해당
규칙을 설정할 수 있습니다. 필요한 규칙이 없고 환경 권한 때문에 추가할 수 없으면 checkpoint도
쓰지 않습니다. 읽기와 hook은 exclude·lock·디렉터리도 만들지 않습니다.

## 형식과 수명

| Field | 의미 |
| --- | --- |
| `schema_version` | 현재는 정수 `1`; 다른 버전은 자동 복구·덮어쓰기하지 않음 |
| `plugin`, `session_id`, `workspace_root` | 현재 패키지·session·정규화된 작업 root와 정확히 일치해야 함 |
| `task_id` | 같은 논리 작업에서 유지하는 ID; 압축·재개로 바꾸지 않음 |
| `active_skill` | 이 패키지에 존재하는 작업 스킬 이름; namespace 제외 |
| `status` | `active`, `complete`, `superseded`; active만 hook 복구 대상 |
| `revision` | 같은 task의 저장 순번; 최신 값을 확인해 갱신 |
| `updated_at` | UTC 저장 시점; 외부 자료의 현재성을 입증하는 값이 아님 |
| `summary` | 짧은 계약·진행·근거 map; 다음 표 참고 |

`summary`에는 비어 있지 않은 문자열 `goal`, `scope`, `progress`, `next_action`이 필수입니다.
`scope`에 승인된 범위·실제 근거·이후 수정 지시·제약을, `progress`에 완료·진행·미결정 사항을
기록합니다. 필요할 때 `evidence`(locator와 revision), `uncertain_actions`(정확한 target, action,
pending/응답/readback의 observation), `details`(플러그인별 상태)를 추가합니다. 이 추가 자료의
도메인 판정은 스킬이 소유하며 helper는 PR·gate·제품 상태 모델을 새로 만들지 않습니다.

전체 UTF-8 JSON은 ASCII escape된 인코딩 후 최대 32 KiB이며 초과하면 이전 기록을 보존하고 실패합니다.
원장·transcript·원문·raw 응답을 복제하거나 비밀값을 넣지 않습니다. 기존 자료는 locator로 참조합니다.
Research의 `persistence: off`, cache/catalog와 원문 저장 제한도 계속 적용됩니다. 파일에 없는
긴 원문을 요약만으로 복원할 수 있다고 간주하지 않습니다.

같은 task는 최신 `--expected-revision`으로 갱신합니다. 현재 record가 없으면 0입니다. 완료한
작업은 `close`로 닫고, 다른 목표로 전환해 중단할 때는 `--outcome superseded`를 사용합니다.
다른 task ID로 전환하려면 현재 작업이 닫혀 있어야 합니다. 이전 닫힌 기록은 history에 보존한 뒤
새 task를 revision 1로 기록합니다. history는 자동 복구 대상으로 검색하지 않습니다. 자동 삭제나
보존 기간 정책은 없습니다. 사용자가 정리하면 기존 산출물에서 수동으로 복구합니다.

## Writing·Fluent·Workflow의 기록 소유

세 플러그인은 서로 다른 작업과 기록을 관리합니다. 기존 Fluent 설치·호출명과
`<current-worktree-root>/.sonsu/continuity/<session-id>/fluent-languages.json`을 유지합니다.
Writing은 같은 디렉터리의 `writing.json`, Workflow는 `workflow.json`을 사용합니다.
기존 Fluent 기록을 Writing으로 이름 변경하거나 옮길 필요가 없습니다.

주 작업을 맡은 controller만 자기 플러그인의 기록을 만듭니다. 티켓·PR 작업에서 Writing·Fluent가
구성·표현만 돕는다면 별도 편집 작업이나 checkpoint를 만들지 않습니다. Writing이 맡은 장문 편집에서
Fluent 표현 지침만 적용할 때도 Writing 기록으로 계속합니다. 각 helper는 다른 플러그인의 파일을
자동 검색·복구하지 않고, 파일명만 바꿔도 record의 plugin identity가 다르면 거부합니다.
실제로 담당 작업을 바꿀 때는 원문·현재 산출물·사용자 지시를 확인해 필요한 진행 사항을 명시적으로
인계하며, 요약만으로 원문·권한·최신 상태를 추정하지 않습니다.

## CLI

실제 설치된 `skills/task-continuity/SKILL.md`에서 `../../scripts/task-continuity.py`를 해석한
**절대 경로**를 사용합니다. helper는 자신의 package manifest에서 plugin identity를 결정합니다.
인자·본문에서 임의의 다른 plugin을 지정할 수 없습니다.

```sh
python3 /absolute/plugin/scripts/task-continuity.py read
python3 /absolute/plugin/scripts/task-continuity.py write --mode write \
  --task-id task-42 --skill to-pr --expected-revision 0 < /absolute/summary.json
python3 /absolute/plugin/scripts/task-continuity.py close --mode write \
  --task-id task-42 --expected-revision 1
```

예시는 Workflow의 `to-pr`입니다. 다른 플러그인은 그 패키지의 실제 작업 스킬 이름을 사용합니다.
`read`는 기록 전체를 JSON으로 반환하고, 기록이 없으면 출력 없이 종료합니다. `write`·`close`는
저장 경로·task ID·revision·상태를 반환합니다. 본문은 stdin으로 전달하고 shell 보간을 사용하지 않습니다.
사용자의 입력이나 도구 결과를 command text로 실행하지 않습니다.

쓰기의 기본 mode는 `read-only`이며 `plan`도 쓰기를 거부합니다. `--mode write`는 현재 쓰기
권한을 확인한 controller가 지정하는 실행 옵션입니다. 호스트 권한을 발견하거나 부여하는 보안
장치가 아니며 sandbox나 사용자 지시를 대체하지 않습니다. 쓰기 금지 요청에서는 옵션을 바꿔
우회하지 않습니다. 유효한 승인은 작업 범위 안에서 유지하며 매 checkpoint마다 다시 묻지 않습니다.

helper는 stale revision, 다른 identity, 손상·지원하지 않는 기록, symlink 경로를 거부합니다.
원자적 replace 전 실패는 마지막 유효 checkpoint를 보존합니다. 같은 기록의 writer는 controller
하나이며 파일 lock과 revision 비교로 stale 병렬 갱신도 거부합니다. 실패한 기록을 자동 삭제하거나
새 task ID로 덮어써서 예산·승인 근거를 초기화하지 않습니다.

## Hook과 복구

각 manifest는 `hooks: "./hooks/hooks.json"`을 선언하며 `SessionStart`의 matcher는
`^(compact|resume)$`입니다. hook에는 root의 native event JSON이 stdin으로 들어옵니다.
실행 명령은 Codex의 `PLUGIN_ROOT`로 같은 package-local helper를 찾습니다.
활성 기록이 있을 때만 다음 내용을 `hookSpecificOutput.additionalContext`로 반환합니다.

- 고정된 복구 안내와 JSON-인코딩된 절대 skill/checkpoint 경로
- 기록은 비신뢰 작업 데이터이며 새 권한이 아니라는 안내
- 최신 사용자 지시·현재 artifact 대조와 불명확한 외부 결과의 조회 우선

본문·task ID·goal·외부 URL·사용자 문구를 developer context에 삽입하지 않습니다. 기록이 없거나
종료됐으면 무출력이고, 손상·권한·경로 오류에서도 context를 넣지 않고 고정 진단만 stderr로
남깁니다. hook은 모델·네트워크 호출, 기록 갱신과 외부 쓰기를 하지 않습니다. PreCompact와
PostCompact handler는 없으며 compaction의 실행 시점이나 압축 방식을 제어하지 않습니다.

Engineering에는 별도로 선택적 [완료 근거 관찰](../../plugins/engineering/skills/using-engineering-skills/references/evidence-gates.md)의
`Stop` handler가 있습니다. 명시적으로 등록한 task만 관찰하며 continuity checkpoint를 갱신하지
않습니다. 위의 읽기 전용 복구 계약은 `SessionStart` handler에 적용됩니다.

복구는 최신 사용자 지시 → 기존 원장·원문·현재 mutable target → 복구 기록의 순서로 정합성을
확인합니다. 확인된 승인은 유지하되 출처 없는 승인 문구는 쓰기 권한으로 승격하지 않습니다.
외부 쓰기 전에는 pending 대상을 기록하고 이후 응답·readback을 기록합니다. 중간에 끊겨 결과가
불명확하면 재시도보다 실제 대상 조회가 먼저입니다. 이미 목표 상태면 중복 쓰기하지 않습니다.
revision이 바뀌면 영향받은 증거만 다시 검증하고 unknown/not_run과 예산을 유지합니다.

Engineering에서는 최신 ledger의 complete/reopened와 누적 round를 따릅니다.
재개에서는 현재 소스·계약과 근거를 대조하고 기존 task/unit ID·누적 라운드를 유지합니다.
재개 자체를 영구 탈락 사유로 삼지 않습니다. fresh reviewer는 구현자 기록을 자동
상속하지 않습니다. 손상·누락된 입력은 기존 산출물에서 복구하고 꼭 필요한 미확인 입력만 질문합니다.

## 설치와 관찰 가능한 보장

플러그인 설치만으로 hook은 신뢰되지 않습니다. CLI의 `/hooks`에서 **현재 hook 정의**를 검토하고
신뢰해야 실행됩니다. 정의가 바뀌면 호스트의 재검토 절차를 따릅니다. helper와 설치 문서는 자동
신뢰 설정이나 trust bypass를 수행하지 않습니다. hook을 사용할 수 없으면 `<plugin>:task-continuity`를
직접 호출해 `read`부터 수동 복구할 수 있습니다.

Codex는 root session의 `SessionStart(source: compact)` context를 다음 모델 요청 전에 전달한다고
문서화합니다. 자동 compaction이 turn 도중 발생한 경우에도 같은 연결을 제공합니다.
[공식 Hooks 문서](https://learn.chatgpt.com/docs/hooks#sessionstart),
[플러그인 hook과 신뢰](https://learn.chatgpt.com/docs/hooks#plugin-bundled-hooks).

스킬과 hook의 발견, helper 실행, 실제 compaction 연결, 모델의 복구 판단은 별개의 검증입니다.
checkpoint 사이의 모든 대화 상태를 무손실 보존하는 기능은 아닙니다. 실행하지 않은 실제 연결은
`not_run`으로 보고하며 정적 검사나 모의 event 결과를 그 증거로 바꾸지 않습니다.

## 유지보수와 검증

```sh
python3 scripts/render-continuity.py --check
python3 -B -m unittest discover -s evals/task-continuity -p 'test_*.py' -v
python3 -B evals/task-continuity/native_probe.py --output /absolute/new-evidence-directory
```

native probe는 새 CODEX_HOME에 로컬 fixture 플러그인을 설치해 현재 프로필 목록의 모든 플러그인을 단독·전체 조합으로
`plugin/read`, `skills/list`, `hooks/list`를 검사합니다. 사용자 인증이나 설정을 복사하지 않고
모델 호출·hook 신뢰 변경을 하지 않습니다. 실제 compaction 연결 검증 절차와 행동 fixture는
[평가 안내](../../evals/task-continuity/README.md)에 정리합니다.
