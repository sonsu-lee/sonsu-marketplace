# 스킬 평가

> 영문 정본: [SKILL.md](SKILL.md) (`970036b` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

두 가지 [Agent Skills 평가 루프][evaluating]를 omp와 Codex에 대해 실행한다.
먼저 출력 품질을 보고, 활성화가 문제일 때는 [description 트리거][descriptions]를
본다. Claude Code 결과는 대신 Anthropic의 `skill-creator` 플러그인
(`/plugin install skill-creator@claude-plugins-official`)으로 얻는다.

스크립트는 이 스킬의 `scripts/`와 `eval-viewer/` 디렉터리에 있다. 이 파일을 로드한
디렉터리 아래의 절대 경로로 호출한다(omp에서는 `realpath skill://evaluating-skills`).
파일 형식과 작업 공간 레이아웃은 [references/formats.md](references/formats.md)에,
클라이언트별 실행 방법은 [references/clients.md](references/clients.md)에 있다.

## 실행 전에

- **클라이언트, 모델, 노력 수준:** 사용자나 프로젝트가 지정한 것을 쓴다. 지정이
  없으면 지금 실행 중인 클라이언트, 모델, 노력 수준을 쓰되, 그 클라이언트가 omp나
  Codex일 때만 해당한다. 결과는 그 조합에서만 유효하다.
- **Home:** `--home`을 전달한다. 평가 대상 스킬이 설치되지 않은, 테스트 로그인이 된
  전용 클라이언트 home이어야 한다(스킬이 설치된 home은 스크립트가 거부한다).
  사용자 본인의 home은 절대 전달하지 않는다. 만드는 방법은
  `references/clients.md`에 있다.
- **실행:** 모델을 호출하는 스크립트는 수 분 이상 실행되고, 네트워크 접근과
  `~/.cache` 및 임시 디렉터리에 대한 쓰기가 필요하다. 사용 중인 클라이언트의
  샌드박스 밖에서 백그라운드 작업으로 시작한다.
- **비용:** 각 평가는 구성과 반복마다 한 번씩 실행된다. 대규모 실행 전에 사용자와
  범위를 합의한다.

## 출력 품질 평가

1. **케이스.** 스킬의 `evals/evals.json`에 `expected_output`이 있는 현실적인
   프롬프트 두세 개로 시작한다. 입력 파일은 `evals/files/` 아래에 두고 경계 케이스
   하나를 포함한다. 이전 케이스는 유지하고, 수정된 동작이나 결과에서 드러난 빈틈에
   대한 케이스를 추가한다. 케이스를 사용자에게 보여 준다.
2. **기준선.** 새 스킬은 스킬이 없는 경우(`--baseline without`)와 비교한다. 수정이면
   이전 버전을 `<workspace>/skill-snapshot`에 두고 `--baseline old`를 쓴다.
3. **실행.** `scripts/run_evals.py --skill-path <skill> --client <omp|codex>
   --model <model> --effort <effort> --home <home> --iteration <N>
   --baseline <without|old>`는 모든 평가를 스킬이 있는 경우와 기준선으로 한 번씩
   실행한다. 평가마다 새로운 `<N>`을 쓴다. 종료 상태 2는 일부 실행이 측정되지
   않았다는 뜻이므로 `--resume`으로 다시 실행한다. 한 번의 실행에서 단언 하나에
   기댄 차이를 주장하기 전에는 새 `<N>`으로 `--runs 3`을 붙여 평가를 반복한다.
4. **단언.** 실행이 진행되는 동안 객관적으로 확인할 수 있는 단언을 `evals.json`에
   쓰고 사용자에게 설명한다. 채점기는 트랜스크립트와 실행이 저장한 파일만 보므로
   그것들에 대해 단언한다.
5. **채점.** `scripts/grade.py <iteration-dir>`가
   [agents/grader.md](agents/grader.md)로 측정된 각 실행을 채점한다. 단언을
   바꾼 뒤에는 다시 실행한다.
6. **벤치마크.** `scripts/aggregate_benchmark.py <iteration-dir> --skill-name
   <name>`이 `benchmark.json`과 `benchmark.md`를 쓴다. 벤치마크에
   [agents/analyzer.md](agents/analyzer.md)를 적용하고 그 `notes` 배열에 본인의
   메모를 추가한다.
7. **리뷰.** `eval-viewer/generate_review.py <iteration-dir> --skill-name <name>
   --benchmark <iteration-dir>/benchmark.json`을 백그라운드에서 시작하고, 사용자에게
   각 출력을 검토해 달라고 요청한다. 피드백은 `<iteration-dir>/feedback.json`에
   저장된다.
8. **개선.** 실패한 단언, 피드백, 트랜스크립트로 스킬을 수정하되 개별 프롬프트를
   땜질하지 말고 일반화한다. 사용자가 만족할 때까지 다음 반복으로 3단계부터
   되풀이한다.

## description 조정

1. **쿼리.** `evals/eval_queries.json`에 현실적인 쿼리를 약 20개 둔다. 절반은
   스킬이 트리거되어야 하는 쿼리이고, 나머지 절반은 어휘는 공유하지만 다른 것이
   필요한 근접 오답이다. 사용자와 함께 검토한다.
2. **수정안 비교.** `scripts/run_trigger_eval.py --skill-path <skill> --client
   <client> --model <model> --effort <effort> --home <home>`를 현재 상태로 한 번,
   `--description "<previous description>"`을 붙여 이전 description으로 한 번
   실행한다. 통과하는 쿼리가
   줄지 않을 때만 수정안을 채택한다.
3. **탐색.** 클라이언트가 description을 제안하게 하려면 같은 인자로
   `scripts/run_loop.py`를 실행한다. 쿼리의 40%를 따로 떼어 두고 나머지로 수정하며,
   따로 둔 쿼리의 점수를 기준으로 `best_description`을 보고한다.
4. **다른 클라이언트.** 프로젝트나 사용자가 다른 클라이언트를 요구하면, 변경을
   채택하기 전에 각 클라이언트에서 2단계를 반복한다.

## 보고

클라이언트, 모델, 노력 수준, 반복 번호를 보고한다. 스킬이 있을 때와 기준선의
통과율과 그 차이, 시간과 토큰, 트리거 통과 수, 측정되지 않았거나 채점되지 않은
실행도 함께 보고한다. 몇 번의 실행은 방향을 보여 줄 뿐 신뢰할 수 있는 비율이
아니다. 실행이 한 번이면 표준편차 0은 분산을 측정하지 않았다는 뜻이다.

[evaluating]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
