# decision-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

중요한 설계 결정을 선별하고 저장소의 관례를 우선해 간결한 ADR을 작성한다.

## 설치

[루트 설치 안내](../../README.md#install)에 따라 마켓플레이스를 등록한 뒤
사용하는 클라이언트의 명령을 실행한다.

```sh
omp plugin install decision-workflow@sonsu-marketplace
codex plugin add decision-workflow@sonsu-marketplace
claude plugin install decision-workflow@sonsu-marketplace
```

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details decision-workflow
```

지원하는 클라이언트에서 작업을 자연어로 요청한다.

```text
Does moving our job queue from Redis to Postgres warrant an ADR?

Draft an ADR for that decision and leave it proposed.
```

자연어 요청은 보통 일치하는 스킬을 선택하지만, 선택은 모델의 판단이며
보장된 훅이 아니다. 스킬을 명시적으로 선택하려면 Codex에서는
`$decision-workflow:writing-adrs`를, Claude Code에서는
`/decision-workflow:writing-adrs`를 사용한다. 플러그인이 목록에 표시된다고
해서 해당 스킬이 실행되는 것은 아니다.

### 스킬

- **`writing-adrs`**는 기록할 가치가 있는 결정을 선별하고 맥락, 결정과
  근거, 기각한 대안, 결과를 담은 짧은 ADR을 작성한다. 대상 프로젝트의 범위,
  템플릿, 생명주기를 우선 따르며, 이들이 없으면 방향을 정하거나 중대한
  영향을 미치는 설계 선택을 기준으로 삼는다.
  [ADR 작성 절차](skills/writing-adrs/SKILL.md)와
  [기본 템플릿](skills/writing-adrs/assets/adr.md)을 참고한다.

`writing-adrs`를 사용하려면 설계 선택에 ADR이 필요한지 묻거나 ADR의 작성,
검토 또는 대체를 요청한다. 모든 구현 변경에 대해 결정 기록을 만들지는
않는다.

원칙은 Martin Fowler의 ADR 지침을 따르며 기본 템플릿은 Evolu에서 가져와
수정했다. 초안은 의사결정자가 수락할 때까지 제안 상태로 유지되며, 수락된
결정을 변경하려면 연결된 대체 문서가 필요하다. 이 플러그인은 훅을
설치하거나 기존 저장소에 형식을 강요하거나 일상적인 작업을 ADR로 만들지
않는다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에
올린다. 저장소의 [기여자 안내](../../CONTRIBUTING.md)를 따르며,
[플러그인](../../CONTRIBUTING.md#adding-a-plugin) 및
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차도 준수한다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee
