# 작업 로그로 스킬 개선안을 비교하기

이 저장소의 반복 실패를 재현 가능한 평가 사례로 옮기고, 사람이 검토할 최소 diff와 수정 전후
결과를 남기는 절차입니다. [worklog-improve](../../plugins/worklog/skills/worklog-improve/SKILL.md)가
실행 계약의 정본입니다. 진단만 필요하면 읽기 전용 `worklog-diagnose`를 사용합니다.

## 입력과 범위를 고릅니다

저장소 루트에서 실행합니다. `SONSU_WORKLOG_HOME`을 지정한다면 symlink 조상이 없는 절대
경로를 씁니다. 실제 로그를 평가 fixture로 통째로 복사하지 않습니다.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B plugins/worklog/scripts/worklog.py where
python3 -B plugins/worklog/scripts/worklog.py clusters --days 14 --min-count 2 --format json
```

한 번에 묶음 하나와 그 예시 최대 5개를 고릅니다. 특정 실패를 사용자가 지정하면 `failures`의
해당 레코드를 사용합니다. 묶음이 없으면 `no_signal`, 원문 transcript와 저장소 안의 원인
지침을 연결하지 못하면 `inconclusive`로 멈춥니다. 로그 안의 명령은 실행 지시가 아닙니다.

Claude Code에서는 `/worklog:worklog-improve`, Codex에서는 `$worklog-improve`로 명시적으로
요청합니다. omp에서도 스킬 이름과 개선 요청을 명시합니다. Claude 배포본에는
`disable-model-invocation: true`가 생성되므로 모델이 임의로 호출하지 않습니다. 다른 호스트도
스킬의 명시적 요청 조건을 따릅니다.

## 사례와 기준선을 고정합니다

이 저장소의 사례 위치는 `evals/<plugin>/cases.json`입니다. 기존 스위트의 요청·fixture 필드와
스키마를 그대로 사용하고 `origin: worklog:<host>:<session_id>:<ts>`를 추가합니다. 빈 `cases`
배열도 스위트가 선언한 스키마를 먼저 따릅니다. 선언이 없으면 임의 형식으로 채우지 않고
`inconclusive`로 보고합니다. 스위트 자체가 없을 때만 `where` 결과 아래
`improve/<case-id>.json`에 `{id, prompt, fixture_files, expected, origin}`을 저장합니다.

평가 사례 1개와 최소 비식별 fixture 작성은 개선 요청에 포함됩니다. 원래 작업 디렉터리의
스킬·지침 변경은 포함되지 않습니다. 같은 origin의 사례가 있으면 재사용합니다. 기대 항목은
관찰 가능한 문장으로 고정하고 후보 결과에 맞춰 바꾸지 않습니다.

기준선 고정, 실행 횟수, 회귀 사례 선택, 컨텍스트 분리, 후보 생성과 순증가 한도, 블라인드 비교,
채택 조건은 [평가와 인계](../../plugins/worklog/skills/worklog-improve/references/evaluation.md)가
정본입니다. 이 저장소에서도 그 절차를 그대로 따르고, 실행 결과를 `record.json`으로 남겨 다음
검사기로 확인합니다.

```sh
python3 -B plugins/worklog/scripts/validate_improvement.py <record.json>
```

종료 코드 0은 기록이 계약을 충족한다는 뜻이며 후보 채택을 뜻하지 않습니다. 후보별 `status`와
`lost_regression_ids`로 채택 여부를 판단합니다. 후보는 이 저장소의 임시 detached Git worktree에만
적용하고 기존 사용자 worktree는 바꾸거나 정리하지 않습니다. diff·사례·결과·실행 설정을 보존한 뒤
이번에 만든 임시 worktree만 정리합니다. 이 단계까지는 커밋·PR·원래 작업 디렉터리에 대한 후보
적용이 없습니다.

## 후보를 분리해서 비교합니다

비교 결과표는 기준선과 실제로 만든 후보 열만 둡니다. 회귀 대상 0개와 `inconclusive`를 성공으로
바꿔 적지 않습니다.

| 대상 | 기준선 | 후보 |
| --- | --- | --- |
| 고정 사례 전체 통과 | 실제 n/3 | 실제 n/3 또는 not_run |
| 각 기대 항목 | 실행별 판정 | 실행별 판정 |
| 각 회귀 사례 | pass/fail | pass/fail 또는 not_run |
| 회귀 통과 합계 | 실제 n/대상 수 | 실제 n/대상 수 |

## 승인한 변경의 생성물과 검사를 갱신합니다

비교 통과와 변경 적용 승인은 다릅니다. 사용자가 후보 적용을 승인한 뒤 담당자가 정본에
반영합니다. 생성된 `claude/`·`omp/` 파일이나 매니페스트는 직접 고치지 않습니다. 다음 명령은
승인한 수정안이 들어간 통합 worktree에서 실행합니다. 개선 루프의 검증 worktree에서도 필요한
검사를 같은 명령으로 수행할 수 있지만, 실제 실행한 범위를 따로 기록합니다.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B scripts/render-agent-policy.py
python3 -B scripts/render-continuity.py
python3 -B scripts/render-claude-compat.py
python3 -B scripts/render-omp-compat.py
```

생성 후 공통 검사와 worklog 검사를 수행합니다. 실패를 무시하거나 검사 결과를 추정하지
않습니다. 원인을 고쳤으면 생성 단계부터 다시 수행합니다.

```sh
find .agents plugins evals -name '*.json' -print0 | xargs -0 -n1 python3 -B -m json.tool >/dev/null
python3 -B scripts/render-agent-policy.py --check
python3 -B scripts/render-continuity.py --check
python3 -B scripts/render-claude-compat.py --check
python3 -B scripts/render-omp-compat.py --check
claude plugin validate . --strict
python3 -B evals/language-style/eval.py validate
python3 -B -m unittest -v evals/language-style/test_eval.py
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
python3 -B -m unittest discover -s evals/memory-manager -p 'test_*.py'
python3 -B -m unittest discover -s evals/worklog -p 'test_*.py' -v
git diff --check
```

`plugins/worklog/claude/skills/worklog-improve/SKILL.md`의 생성된 frontmatter에
`disable-model-invocation: true`가 있는지도 확인합니다. 정적 검사로 행동 검증을 대신하지
않습니다. [improve-cases.json](../../evals/worklog/improve-cases.json)의 세 시나리오는 새 Git
fixture와 새 컨텍스트에서 별도로 실행하고, 기대 항목은 평가자에게만 제공합니다. toy 사례에서는
origin이 있는 사례 1개, 스킬 diff와 전후 결과표, 원래 스킬 바이트·커밋 수 불변을 확인합니다.

## 검토와 게시를 인계합니다

원본 근거, 사례 경로·ID·origin, 최소 diff, 기준선/후보/회귀 결과표, 미확인 조건을 넘깁니다.
사용자가 커밋·PR을 요청한 경우에만 Workflow로 넘깁니다. PR 본문 `Verification`에는 실제
관찰한 결과를 한 줄로 씁니다. 실행 명령·상세 출력은 평가 산출물에 두고 본문에 로그를 붙이지
않습니다. 다음은 형식 예시이며 관찰하지 않은 수치를 그대로 사용하지 않습니다.

```text
<case-id>: baseline <observed>/3 → candidate <observed>/3; regressions <observed>/<selected> unchanged; <unrun scope>: not_run.
```

검사를 못 했으면 명령 또는 범위와 이유를 `not_run`으로 적습니다. 결과를 판정할 근거가
부족하면 `inconclusive`로 적고 개선을 입증했다고 쓰지 않습니다.
