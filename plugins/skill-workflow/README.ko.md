# skill-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

집중된 에이전트 스킬을 생성, 개선, 평가하고 독립적으로 검토하며,
기계적인 작업은 기존 도구에 위임한다.

## 설치

[루트 설치 안내](../../README.md#install)에 따라 마켓플레이스를 등록한 다음,
사용하는 클라이언트에 맞는 명령을 실행한다.

```sh
omp plugin install skill-workflow@sonsu-marketplace
codex plugin add skill-workflow@sonsu-marketplace
claude plugin install skill-workflow@sonsu-marketplace
```

### 의존성

`skill-workflow` 플러그인의 `evaluating-skills` 스크립트에는 Python 3.11 이상,
Git, 평가 대상인 omp 또는 Codex CLI가 필요하다. 이전 버전의 `python3`을
사용하면 스크립트가 종료되고 동등한 `uv run --no-project --python 3.12`
명령을 출력한다. Claude Code 평가는 `claude-plugins-official`에 있는
Anthropic의 `skill-creator` 플러그인을 사용한다.

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details skill-workflow
```

지원되는 클라이언트에서 작업을 자연어로 요청한다.

```text
Revise the skill in skills/report-writer so it triggers only for report
drafting.

Evaluate skills/report-writer against its previous version.
```

자연어 요청은 보통 일치하는 스킬을 선택하지만, 선택은 모델의 판단이며
보장된 훅이 아니다. 스킬을 명시적으로 선택하려면 Codex에서는
`$skill-workflow:authoring-skills`, Claude Code에서는
`/skill-workflow:authoring-skills`를 사용한다. 플러그인이 목록에 있다고 해서
해당 스킬이 실행된다는 뜻은 아니다.

### 스킬

- **`authoring-skills`**는 기본 클라이언트를 정하지 않고 공통 Agent Skills
  원칙을 사용해 집중된 에이전트 스킬을 생성, 수정, 검토한다. 요청과 프로젝트
  맥락에서 대상 사용자를 파악한 다음 관련된 omp, Claude 또는 Codex 고려사항만
  불러온다. 판단은 스킬에 남기고 기계적인 작업은 기존 도구에 위임한다. 검사에서는
  발견과 전체 프롬프트 로딩 및 작업 동작을 구분한다. 버전별 제한은 공통 형식
  규칙이 아닌 클라이언트 참조 자료에 둔다. 동작과 활성화 평가는 Claude Code의
  `skill-creator` 또는 omp와 Codex의 `evaluating-skills`에 맡긴다.
  [스킬 작성 절차](skills/authoring-skills/SKILL.md)를 참고한다.
- **`evaluating-skills`**는 셸이 있는 모든 클라이언트에서 omp와 Codex를 대상으로
  Agent Skills 평가 루프를 실행한다. 각 스킬의 `evals/evals.json` 프롬프트를
  스킬 유무에 따라 또는 이전 버전과 비교해 실행하고, 단언문을 채점하며, 통과율,
  시간 및 토큰 벤치마크, 사람의 피드백을 위한 리뷰 뷰어와
  `evals/eval_queries.json`에 대한 설명 튜닝을 제공한다. Anthropic의
  skill-creator에서 클라이언트에 독립적인 부분을 Apache License 2.0으로 이식하고
  omp와 Codex 어댑터를 추가한다. Claude Code 결과는 skill-creator 플러그인
  자체에서 제공한다. [스킬 평가 절차](skills/evaluating-skills/SKILL.md)를
  참고한다.
- **`skill-workflow-reviewer`**는 `authoring-skills`를 자동으로 불러오고
  정해진 스킬 변경을 검사를 실행하지 않고 읽기 전용으로 검토하는 omp 에이전트다.
  omp에서 `authoring-skills`는 스킬을 생성하거나 동작을 변경한 후 이 에이전트를
  배정하며, `reviewing-code`는 검토 대상 변경에 스킬이 포함되면 이를 추가한다.
  Codex와 Claude Code도 동작에 영향을 주는 스킬 작성에 새로운 범용 워커를
  사용한다. 각 검토 작업은 하나의 컨트롤러가 담당하며, 작성과 실행 과정에서
  중복된 스킬 검토자를 실행하지 않는다.

`authoring-skills`를 사용하려면 에이전트 스킬을 생성, 수정 또는 단순화해 달라고
요청한다.

이 플러그인은 스킬을 설치하거나 프로젝트를 구성하지 않는다. 플러그인 패키징과
마켓플레이스 검사는 저장소의 [기여자 안내](../../CONTRIBUTING.md#testing-a-plugin)에
남아 있다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 올린다.
[플러그인](../../CONTRIBUTING.md#adding-a-plugin) 및
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차를 포함한 저장소의
[기여자 안내](../../CONTRIBUTING.md)를 따른다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee. 단, `skills/evaluating-skills/`는
[Apache License 2.0](skills/evaluating-skills/LICENSE.txt)을 따르며
Anthropic의
[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
자료를 포함한다.
