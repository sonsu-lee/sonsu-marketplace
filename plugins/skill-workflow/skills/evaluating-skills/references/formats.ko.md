# 평가 파일

> 영문 정본: [formats.md](formats.md) (`fe462ed` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

스크립트는 스킬의 `evals/` 디렉터리를 읽고 Anthropic의 skill-creator와 같은 작업
공간 레이아웃으로 결과를 쓴다.

## `evals/evals.json`

```json
{
  "skill_name": "csv-cleanup",
  "evals": [
    {
      "id": 1,
      "prompt": "Clean data.csv: trim spaces and drop duplicate rows.",
      "expected_output": "A cleaned CSV without duplicates or padding.",
      "files": ["evals/files/data.csv"],
      "assertions": ["Writes a CSV with no duplicate rows"]
    }
  ]
}
```

- `skill_name`은 `SKILL.md`의 `name`과 같다.
- 각 평가에는 고유한 정수 `id`, `prompt`, `expected_output`이 있다. `files`와
  `assertions`는 선택이며, 그 밖의 키는 받아들이지 않는다. 키는 `expectations`가
  아니라 `assertions`다.
- `files`는 `evals/files/` 아래의 경로를 나열한다. 파일은 기본 이름으로 실행의 작업
  디렉터리에 복사된다. 끝에 `/`를 붙여 쓴 디렉터리는 그 내용이 복사된다.
- 평가는 이 입력만 사용한다. 다른 경로, 네트워크 서비스, 자격 증명은 쓰지 않는다.
- `evals/` 아래에는 `SKILL.md`라는 이름의 파일을 두면 안 된다. Codex가 이를 스킬로
  등록하기 때문이다.

## `evals/eval_queries.json`

```json
[
  {"query": "clean the duplicates in exports/q3.csv", "should_trigger": true},
  {"query": "convert this CSV to Parquet", "should_trigger": false}
]
```

각 `query`는 한 번만 나타난다. 학습/테스트 분할은 텍스트로 결과를 대응시킨다.

## 작업 공간

`--workspace`를 주지 않으면 결과는
`${XDG_CACHE_HOME:-~/.cache}/skill-evals/<skill>-workspace`에 쓰인다. 커밋하지
않는다.

```text
<workspace>/
  skill-snapshot/               previous version for --baseline old
  <client>/iteration-N/
    iteration.json              client, model, effort, home, baseline, runs
    benchmark.json, benchmark.md
    feedback.json               saved by the review viewer
    eval-<id>/
      eval_metadata.json        prompt, expected output, files, assertions
      <config>/run-<r>/         config: with_skill, without_skill, old_skill
        transcript.md           prompt, brief, tool calls, final message
        events.jsonl            raw client events
        outputs/                files the run saved, final_message.md,
                                metrics.json
        timing.json             tokens, duration, observed model; "error"
                                is null when the run was measured
        grading.json            expectations[] with text, passed, evidence;
                                summary
```

- `timing.json`에 `"error": null`이 있으면 측정된 실행이다. 요청과 다른 모델이나
  노력 수준으로 실행한 경우는 오류로 기록한다.
- `benchmark.json`은 각 구성의 평균 통과율, 시간, 토큰과, with_skill에서 기준선을
  뺀 `delta`를 보고한다. `metadata.coverage`는 평가와 구성별로 채점된 실행과 기대한
  실행을 알려 주며, 모자라는 것은 `benchmark.md`에 나열된다.

## 트리거 결과

`run_trigger_eval.py`는 쿼리마다 한 항목씩 `results`를 출력한다. 항목은 `triggers`,
`runs`(측정된 실행), `trigger_rate`, `pass`, `unmeasured`(측정된 실행 없음)를
가진다. 트리거되어야 하는 쿼리는 비율이 0.5 이상일 때 통과하고, 근접 오답은 그
미만일 때 통과한다. `run_loop.py`는 반복마다 `history`와 `best_description`을
추가한다.

## 종료 상태

모든 스크립트는 성공하면 0, 잘못된 입력이면 1로 종료한다. `run_evals.py`,
`run_trigger_eval.py`, `run_loop.py`는 일부 실행이 측정되지 않았을 때 2로
종료하고, `grade.py`는 일부 실행이 채점되지 않았을 때 2로 종료한다.
