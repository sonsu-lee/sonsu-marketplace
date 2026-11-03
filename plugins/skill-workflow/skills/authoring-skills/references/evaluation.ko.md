# 평가 선택

> 영문 정본: [evaluation.md](evaluation.md) (`57da0f4` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

형식, 발견, 전체 로딩, 출력 품질, 활성화는 서로 다른 주장이다. 하나의 근거가 다른
것을 증명하지 않는다. 변경이 영향을 주는 동작에 맞는 검사를 고른다.

## 변경에 맞는 검사

- **메타데이터나 패키징:** 공식 형식 검증기와 클라이언트의 발견 검사를 실행한 뒤,
  설치된 스킬을 호출해 주입된 내용이 경고 없이 전부 로딩되는지 확인한다.
- **작업 지침:** `evals/evals.json`으로 스킬 유무 또는 이전 버전과 비교하는 출력
  품질 루프. 답만이 아니라 transcript를 읽는다.
- **도구나 설정:** 실제 도구를 유효·무효 입력으로 실행한다. 모델 의견이 아니라
  결정론적 검사를 쓴다.
- **description이나 범위:** 이전·새 description으로 `evals/eval_queries.json`
  트리거 eval을 실행하고 실제 로딩을 관찰한다.
- **형식만 수정:** 동작 벤치마크를 만들지 않는다.

로더에 맞추려고 내용을 참고 문서로 옮기면, 옮긴 내용이 필요한 eval을 추가하고
참고 문서를 읽었는지 assertion으로 확인한다.

## 실행기 선택

프로젝트에 기존 설정이 있으면 그것을 먼저 쓴다. 없으면:

- **Claude Code:** Anthropic의 [skill-creator 플러그인][creator].
- **omp와 Codex:** `evaluating-skills` 스킬.
- **다른 클라이언트:** [출력][outputs]과 [description][descriptions] 가이드를
  클라이언트 자체 도구로 따른다.

## 결과 반영

실패, 피드백, trace를 함께 보고 고친다. 안전장치를 쌓기보다 효과 없는 요구사항을
지운다. 영향받는 케이스를 다시 실행하고, 간단한 확인은 반복 측정과 구분해 보고한다.

## 주의할 점

- 발견 검사는 메타데이터만 읽어 본문 잘림을 놓칠 수 있다.
- 모델이 스킬을 쓰겠다고 말하는 것은 활성화의 근거가 아니다.
- `evals/` 아래에 `SKILL.md`라는 파일을 두지 않는다. 일부 클라이언트가 등록한다.
- 수동 확인은 설치된 패키지 밖의 격리된 workspace에서 하고, 티켓·PR·메시지 같은
  테스트 산출물을 실제 프로젝트에 게시하지 않는다.
- 결과는 실행한 클라이언트, 모델, effort에서만 유효하다. 여러 클라이언트가 쓰는
  description은 어느 클라이언트에서도 통과하던 트리거 쿼리를 잃으면 안 된다.
- 평가는 스킬의 일상 경로 밖에 둔다. 스킬 사용자는 작성용 벤치마크를 실행하지 않는다.

[outputs]: https://agentskills.io/skill-creation/evaluating-skills
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[creator]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
