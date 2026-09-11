# 완료 근거 관찰 도구

계획 기반 작업의 완료 근거를 로컬 파일에 연결하는 선택적 pilot이다. 조정자가 이 도구로
작업을 등록하면 `verification → final-review → red-team` 순서에서 누락되거나 오래된 근거를
검사한다. Fast Path와 계획 없는 작업은 기존 절차를 따른다. 판단·권한·리뷰의 정본은
[품질 게이트 계약](quality-gates.md)이며, 이 도구는 그 일부를 관찰한다.

일반 코드·diff 리뷰 요청은 등록 대상이라는 뜻이 아니다. 직접 리뷰·미등록 작업에 등록이나
별도 증적 작성을 요구하지 않으며, fresh reviewer는 조정자를 대신해 등록하지 않는다.
리뷰 내용의 판단은 [공통 리뷰 기준](../../requesting-code-review/review-criteria.md)을 따른다.

Python 3.9+, Git, POSIX(macOS/Linux)에서 동작한다. 모델·네트워크·별도 서버·다른 플러그인은
필요하지 않다. 검사 명령은 등록한 `argv`로 직접 실행하며 shell 문자열을 해석하지 않는다.

## 등록과 상태

현재 설치본의 `scripts/evidence-gates.py` **절대 경로**를 `GATES`로 둔다. 아래 명령의 cwd는
작업 Git worktree다. `TASK_ID`는 현재 원장의 고정 ID이며 재개·수정 때문에 새로 만들지 않는다.
계획과 계약의 위치를 `inputs`에, 실행할 모든 필수 검사를 `checks`에 등록한다. 설정은 JSON
파일이나 stdin으로 전달하며 원문을 shell 명령 문자열에 보간하지 않는다.

```json
{
  "inputs": [".engineering/plans/current-work.md"],
  "checks": [
    {"id": "unit", "argv": ["python3", "-B", "-m", "unittest", "discover", "-s", "tests"]},
    {"id": "diff", "argv": ["git", "diff", "--check"]}
  ]
}
```

`inputs`에는 실제 존재하는 파일을 지정한다. 끊어진 symlink와 디렉터리를 가리키는 symlink도
거부한다. 파일·검사 선택은 계획에서 결정하며 빈 목록은
허용하지 않는다. 자동으로 검사를 추측하거나 `echo passed` 같은 명령의 적합성을 판단하지 않는다.
적용하지 않는 검사는 이유를 계획에 남기고 등록 대상에서 제외한다.

```sh
python3 "$GATES" init --task-id "$TASK_ID" < /absolute/gate-config.json
python3 "$GATES" status --task-id "$TASK_ID"
python3 "$GATES" run --task-id "$TASK_ID" --check unit
python3 "$GATES" run --task-id "$TASK_ID" --check diff
```

session ID는 `init --session-id`, `CODEX_THREAD_ID`, `CLAUDE_CODE_SESSION_ID` 순으로 선택한다.
두 호스트 변수가 함께 남은 경우 실제 호스트의 정확한 ID를 지정한다. 같은 task를 다른
session에서 `init`해도 기존 receipt와 소비 예산을 유지한다. 현재 session의 다른 활성 task를
덮어쓰지 않는다. 주 조정자만 등록하며 subagent·fresh reviewer는 등록하지 않는다.

저장 위치는 `<worktree>/.engineering/gates/tasks/<task-id>/`다. 세션별 pointer는 인접한
`sessions/`에 둔다. 최초 등록은 Git `info/exclude`에 `/.engineering/gates/`를 추가하며
기존 내용을 보존한다. 실행 기록에는 로컬 검사 출력과 고정 리뷰 자료가 포함된다.

`status`는 읽기 전용이고 항상 JSON을 반환한다. `check`는 같은 JSON을 반환하면서 모든
필수 gate의 현재 근거가 충족되면 exit 0, 아니면 exit 1이다. 입력·경로·상태 오류는 exit 2다.
검사 명령의 `run`도 현재 해당 검사의 통과는 exit 0, 실패·미완료는 exit 1로 반환한다.

## 리비전과 실제 실행 근거

snapshot은 다음을 함께 해시한다.

- Git tracked 파일의 현재 내용·실행 비트·삭제와 nonignored untracked 파일
- Git index의 논리적 entries·`assume-unchanged`/`skip-worktree` 플래그와 HEAD. 파일이 같아도 비교 기준이 바뀌면 무효화한다.
- 실제 staged diff. `git add -N`의 intent-to-add를 정상 stage로 전환하는 변경도 포함한다.
- `inputs`에 명시한 계획·계약 파일. Git에서 무시한 파일도 포함한다.
- 등록한 검사 정의, 현재 검사 도구와 `quality-gates.md` 정책

runtime 상태 디렉터리는 snapshot에서 제외한다. 소스의 symlink는 링크 자체를 식별하며 외부
대상 내용을 추적하지 않는다. submodule·디렉터리 입력은 지원하지 않는다. 외부 환경·의존성,
선택하지 않은 ignored 파일, 검토 내용의 진위를 이 digest로 입증하지 않는다. 입력이 크면
전체 포함 파일을 읽는 비용이 들며, 매 도구 호출이 아닌 명시적 검사와 `Stop`에서만 계산한다.

`run`은 실행 전에 attempt를 저장하고 실제 종료 코드·출력을 receipt에 연결한다. 성공 종료라도
실행 전후 snapshot이 다르면 `inconclusive`다. 프로세스 시작 실패는 `blocked`, 시간 초과는
`inconclusive`이며 `execution: incomplete`를 별도로 보존한다. 기본 제한 시간은 300초,
`--timeout`으로 0초 초과 3,600초 이하를 지정할 수 있다. 시간 초과 시 해당 process group을 종료한다.
사용자가 승인한 검증 명령만 등록·실행한다. 등록이나 통과는 새 실행 권한이 아니다.
`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` 등 상위 실행에서 상속된 저장소 대상 변수는
snapshot 조회와 검사 실행에서 제거한다. 현재 worktree를 기준으로 실행하며 그 밖의 환경은 상속한다.
완료 결과를 저장할 때 다른 writer가 잠금을 사용 중이면 해제될 때까지 기다린다.
실행 전 예약과 훅 관찰은 잠금 경합 시 실행하지 않고 다음 호출로 넘긴다.
명령 종료 후 입력·로그를 조회할 수 없어도 종료 코드와 확보한 근거를 기록하고 판정은
`inconclusive`로 남긴다. 조회 오류는 exit 2로 보고하며, 입력을 복구한 뒤 같은 task에서 이어 간다.

## 리뷰 근거 연결

일반 리뷰 전에 기존 `requesting-code-review/scripts/review-package`로 전체 변경을 고정한다.
준비 명령은 현재 검증이 통과했을 때만 리뷰 attempt를 예약하고 입력 package를 복사한다.

```sh
python3 "$GATES" prepare-review --task-id "$TASK_ID" --gate final-review \
  --package /absolute/whole-change-package.md
```

반환된 `attempt`, `artifact_digest`, 고정 `package`와 `package_digest`를 리뷰 요청에 포함한다.
새 문맥의 리뷰어는 그 package를 읽는다. 검토 결과를 파일로 보존한 뒤 실제 리뷰어 ID와 함께
예약한 attempt에 연결한다.

```sh
python3 "$GATES" record-review --task-id "$TASK_ID" --gate final-review \
  --attempt 1 --verdict passed --reviewer-id reviewer-session-id \
  --report /absolute/general-review.md
```

일반 리뷰 verdict는 `passed | failed | inconclusive | blocked`다. red-team은 기존
`requesting-code-review/scripts/red-team-package`로 원래 목표·계획·전체 변경·검증·관찰·지적 이력을
고정한 뒤 같은 prepare/record 명령의 `--gate red-team`을 사용한다. verdict는
`survives_challenge | invalidated | inconclusive | blocked`다.

리뷰 입력 준비와 결과 기록 사이에 snapshot 또는 선행 receipt가 바뀌면 등록을 거부한다.
현재 digest를 오래된 보고서에 붙여 통과시키지 않는다. 일반 리뷰와 red-team은 다른 reviewer ID를
사용하고, 등록된 controller ID는 reviewer로 받지 않는다. 이 검사는 **ID·예약·근거 연결의
일관성**만 확인한다. 실제 독립 context, report의 진위, package의 의미적 완전성은 조정자가
도구 실행 근거로 확인한다. 제출자가 ID나 내용을 조작하는 것을 막는 보안 장치는 아니다.

입력 package와 report는 task 디렉터리에 고정해 원래 파일 수정·삭제의 영향을 받지 않게 한다.
고정 사본이나 검사 출력이 바뀌면 관련 receipt는 `inconclusive`로 평가한다. 같은 소스에서
검사만 다시 실행해도 새 receipt에 의존하는 후속 리뷰는 재확인한다.

## 수정·중단·완료

각 check와 두 review gate에는 최초 실행을 포함한 최대 5회의 누적 시도가 있다. 새 session,
설정 수정, close 후 재개로 초기화하지 않는다. 제한은 자동 복구나 실행 권한을 만들지 않는다.
기존 계획에 더 낮은 상한이 있으면 조정자가 그 상한을 우선한다.

등록한 검사 명령이나 입력 경로를 잘못 정했다면 `revise`로 같은 task/check ID의 구성을 수정한다.
과거 구성·receipt·소비 예산을 보존하고 새 구성의 snapshot으로 근거를 다시 평가한다.

```sh
python3 "$GATES" revise --task-id "$TASK_ID" < /absolute/corrected-gate-config.json
```

이 pilot은 check ID 추가·제거와 기존 근거의 부분 재사용을 자동 처리하지 않는다. 검사 집합의
변경, 정확한 리비전에 대한 사람의 `accepted_risk`, 국소 수정 후 근거 재사용은 기존 원장에
근거를 남겨 품질 계약으로 판단하고 pilot에서는 미충족 관찰로 구분한다. 도구를 통과시키기
위해 task ID를 바꾸거나 근거를 지우지 않는다.

검사나 리뷰가 중단돼 예약만 남았다면 실제 실행이 끝났는지 먼저 확인한다. `abandon`은 해당
예약을 `inconclusive`로 닫으며 시도를 돌려주지 않는다. 이후 도착한 옛 결과는 받지 않는다.

```sh
python3 "$GATES" abandon --task-id "$TASK_ID" --gate check:unit --attempt 1
python3 "$GATES" abandon --task-id "$TASK_ID" --gate final-review --attempt 1
python3 "$GATES" check --task-id "$TASK_ID"
python3 "$GATES" close --task-id "$TASK_ID"
```

`close`는 현재 모든 gate가 통과한 경우만 완료로 닫는다. 작업을 중단하고 다른 작업으로
넘어가는 경우 `close --outcome superseded`를 사용한다. 근거와 시도는 보존된다.
재개는 같은 task/config의 `init`이며, 최신 사용자 지시와 실제 상태를 먼저 대조한다.

## Stop 관찰

Engineering의 `Stop` 훅은 등록한 root session의 활성 task만 조회하고 최신 결과를
`observation.json`에 저장한다. 이전 관찰과 달라진 미충족 상태에는 고정된 `systemMessage`를
반환한다. `decision: block`, continuation, 검사 실행, 모델 호출은 하지 않는다. 질문·중간
보고로 turn을 끝내도 미완료가 관찰될 수 있으므로 알림 자체를 절차 위반으로 해석하지 않는다.

미등록·다른 session·subagent·닫힌 task·plan mode에는 아무것도 쓰거나 출력하지 않는다.
Git 저장소 밖의 일반 작업 디렉터리도 조용히 건너뛴다.
손상된 상태는 자동 복구·삭제하지 않고 고정 진단만 남긴다. 훅을 실행할 수 없으면 CLI `status`로
확인한다. 플러그인 설치·발견과 사용자의 hook trust, 실제 hook 실행, 모델의 지침 준수는 별개다.
현재 관찰 pilot은 도구 호출 누락 자체를 막거나 100% 절차 준수를 보장하지 않는다.

## 도입 근거와 검증

`@ttsc/evidence`의 필수 참조와 fingerprint 만료, `@ttsc/graph`의 작은 관계 응답을 참고했다.
외부 코드를 복사하거나 compiler 패키지를 의존성으로 추가하지 않았다. 근거 연결 검사와
의미적 진위를 구분하는 범위는 [upstream README](https://github.com/samchon/ttsc/blob/14a22f077caf23f1bfb8a97b3d9db765912074ef/packages/evidence/README.md#L112-L129)에 명시돼 있다.
[Codex Hooks](https://learn.chatgpt.com/docs/hooks#stop)와
[Claude Code Hooks](https://code.claude.com/docs/en/hooks#stop)의 실제 이벤트를 사용한다.

```sh
python3 -B -m unittest discover -s plugins/engineering/tests -p 'test_evidence_gates.py' -v
python3 scripts/render-continuity.py --check
python3 -B evals/task-continuity/native_probe.py --only engineering --output /absolute/new-probe-directory
```

fixture의 실제 CLI·모의 event 실행, native loader 발견, 실제 host hook과 모델 workflow 준수를
각각 보고한다. 누락 검출, 오탐, snapshot 시간과 알림 빈도를 관찰한 뒤 차단 도입을 별도로 판단한다.
pilot을 중단하려면 task를 `superseded`로 닫는다. 설치본을 되돌릴 때에는 이전 Engineering
버전을 사용하며 기존 기록을 삭제하거나 다른 플러그인의 훅을 변경하지 않는다.

### PR 리뷰 후 보완한 실행 경계

- 기존 리뷰어 ID를 controller session으로 추가하는 `init`은 상태를 변경하지 않고 거부한다.
- 기본 리뷰 패키지 생성기는 `TMPDIR`의 물리 경로를 반환한다. 상태 디렉터리와 리뷰 입력의
  symlink 거부 정책은 유지한다.
- 검사 로그는 8 MiB까지 저장한다. 초과 시 process group을 종료하고 로그에 이유를 남기며
  `inconclusive` / `execution: incomplete`로 기록한다. 근거 파일 해시는 나누어 읽어 계산한다.
- `Stop` 관찰에는 6초 실행 예산을 적용한다(호스트 제한 10초). snapshot 도중 예산을 초과하면
  `ready: false`, `observation: inconclusive`, `reason: time_budget_exceeded`를 저장하고 알린다.
  task 확인 이전에 예산을 초과하면 상태를 쓰지 않고 확인 불가 알림만 반환한다.
  운영체제의 중단 불가능한 I/O나 호스트 자체 종료까지 보장하는 제한은 아니다.

### 패키지·종료 상태·정책 변경 처리

리뷰 package는 report의 1 MiB 제한을 적용하지 않고 64 KiB 단위로 복사·해시한다.
입력을 임시 파일로 고정한 뒤 task 디렉터리에 원자적으로 게시하므로 package 크기에 비례한
임시 디스크 공간은 필요하다. report 제한은 그대로 유지한다. `red-team-package`도 기본
임시 경로를 물리 경로로 정규화한다.

닫힌 task의 `close`와 `abandon`은 거부한다. 동일한 종료 상태를 다시 요청하더라도 먼저
같은 task/config로 `init`해야 한다. 리뷰 정책 digest에는 `quality-gates.md` 외에
`review-criteria.md`, `code-reviewer.md`, `red-team-reviewer.md`도 포함한다.
정책 파일 변경은 기존 근거를 오래된 상태로 판정하며, 파일 누락은 검사 오류로 보고한다.
이 관찰을 이유로 task ID를 바꾸거나 자동으로 전체 재실행하지 않는다. 유효 근거의 부분 재사용과
사람이 결정한 `accepted_risk`는 기존 품질 계약으로 판단하고, pilot의 미충족 관찰과 구분한다.
