# 스킬 평가

> 영문 정본: [SKILL.md](SKILL.md) (`f9653c8` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

omp나 Codex에서 두 가지 [Agent Skills 평가 루프][evaluating]를 실행한다. 먼저 출력
품질을, 활성화가 문제일 때는 [description 트리거][descriptions]를 평가한다. Claude
Code는 Anthropic의 `skill-creator` 플러그인을 쓴다
(`/plugin install skill-creator@claude-plugins-official`).

`scripts/`와 `eval-viewer/`의 스크립트는 이 스킬 디렉터리 아래 절대 경로로
호출한다(omp에서는 `realpath skill://evaluating-skills`). 파일 형식과 workspace
구조는 [references/formats.md](references/formats.md), 클라이언트 설정은
[references/clients.md](references/clients.md)에 있다.

## 실행 전에

- **클라이언트, 모델, effort:** 사용자나 프로젝트가 정한 것, 없으면 omp나 Codex에서
  실행 중인 자신의 것. 결과는 그 조합에서만 유효하다.
- **홈:** `--home`에 테스트 로그인이 있고 평가 대상 스킬이 설치되지 않은 전용
  클라이언트 홈을 넘긴다. 사용자의 홈은 절대 쓰지 않는다.
- **실행:** 모델 실행은 수 분이 걸리고 네트워크와 `~/.cache`·임시 디렉터리 쓰기가
  필요하다. 클라이언트 샌드박스 밖의 백그라운드 작업으로 실행한다.
- **비용:** eval은 구성과 반복마다 한 번씩 실행된다. 큰 실행 전에 범위를 합의한다.

## 출력 품질 평가

1. **케이스:** `evals/evals.json`에 `expected_output`이 있는 현실적인 프롬프트 두세
   개, 입력 파일은 `evals/files/`에 두고 경계 사례를 하나 넣는다. 이전 케이스는
   유지하고 바뀐 동작이나 빈틈을 위한 케이스를 더한다. 사용자에게 보여 준다.
2. **기준선:** 새 스킬은 `--baseline without`. 개정은 이전 버전을
   `<workspace>/skill-snapshot`에 두고 `--baseline old`.
3. **실행:** `scripts/run_evals.py --skill-path <skill> --client <omp|codex>
   --model <model> --effort <effort> --home <home> --iteration <N>
   --baseline <without|old>`. 차이를 주장하기 전에는 `--runs 3`을 더한다.
4. **assertion:** 실행 중에 객관적으로 확인 가능한 assertion을 `evals.json`에
   쓴다. 채점자는 transcript와 저장된 파일만 본다.
5. **채점:** `scripts/grade.py <iteration-dir>`가 [agents/grader.md](agents/grader.md)로
   채점한다. assertion을 바꾸면 다시 실행한다.
6. **벤치마크:** `scripts/aggregate_benchmark.py <iteration-dir> --skill-name <name>`이
   `benchmark.json`과 `benchmark.md`를 만든다. [agents/analyzer.md](agents/analyzer.md)를
   적용하고 `notes`에 메모를 더한다.
7. **리뷰:** `eval-viewer/generate_review.py <iteration-dir> --skill-name <name>
   --benchmark <iteration-dir>/benchmark.json`을 백그라운드로 띄우고 사용자에게
   각 출력을 검토해 달라고 한다. 피드백은 `<iteration-dir>/feedback.json`에 저장된다.
8. **개선:** 실패한 assertion, 피드백, transcript로 고치되 프롬프트 하나를 땜질하지
   말고 일반화한다. 3단계부터 반복한다.

## description 조정

1. **쿼리:** `evals/eval_queries.json`에 현실적인 쿼리 약 20개. 절반은 트리거되어야
   하고, 절반은 어휘를 공유하는 near-miss다. 사용자와 함께 검토한다.
2. **비교:** `scripts/run_trigger_eval.py --skill-path <skill> --client <client>
   --model <model> --effort <effort> --home <home>`를 그대로 한 번,
   `--description "<이전>"`으로 한 번 실행한다. 통과한 쿼리가 줄지 않을 때만 채택한다.
3. **탐색:** 같은 인자의 `scripts/run_loop.py`가 description을 제안하고, 쿼리 40%를
   떼어 두었다가 `best_description`을 보고한다.
4. **다른 클라이언트:** 프로젝트나 사용자가 요구하는 클라이언트마다 2단계를 반복한다.

## 보고

클라이언트, 모델, effort, iteration. 스킬과 기준선의 통과율과 차이, 시간과 토큰,
트리거 통과 수, 측정·채점되지 않은 실행.

## 주의할 점

- 평가마다 새 `--iteration`이 필요하다. 이미 있는 번호는 거부된다.
- 종료 코드 2는 측정되지 않은 실행이 있다는 뜻이다. `--resume`으로 다시 실행한다.
- eval ID는 영구적인 키다. ID를 다른 케이스에 다시 쓰지 않고, ID의 의미가 바뀌면
  새 workspace를 쓴다.
- 비교할 때마다 `skill-snapshot`을 의도한 기준 리비전에서 다시 만든다.
- 몇 번의 실행은 방향만 보여 줄 뿐 믿을 만한 비율이 아니다. 실행이 한 번이면
  표준편차 0은 분산을 재지 않았다는 뜻이다.

[evaluating]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
