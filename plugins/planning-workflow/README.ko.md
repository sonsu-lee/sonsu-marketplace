# planning-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

복잡한 작업을 계획하고 독립적인 리뷰와 최종 검증을 통해 승인된 실행을 조율한다.

## 목차

- [설치](#설치)
  - [의존성](#의존성)
- [사용법](#사용법)
  - [CLI](#cli)
  - [스킬](#스킬)
- [기여](#기여)
- [라이선스](#라이선스)

## 설치

[루트 설치 가이드](../../README.md#install)에 따라 마켓플레이스를 등록한 뒤
사용하는 클라이언트의 명령을 실행한다.

```sh
omp plugin install planning-workflow@sonsu-marketplace
codex plugin add planning-workflow@sonsu-marketplace
claude plugin install planning-workflow@sonsu-marketplace
```

### 의존성

`executing-work`는 코드 변경과 스킬 동작 변경에 대해 독립적인 리뷰를 요구한다.
코드 리뷰에는 [review-workflow](../review-workflow/README.md)의
`reviewing-code`를 불러오고, 코드 리뷰 컨트롤러가 없는 스킬 전용 변경에는
[skill-workflow](../skill-workflow/README.md)의 `authoring-skills`를 따른다.
작업에 해당 리뷰가 필요하면 이 플러그인들을 설치한다. 설치하지 않으면 누락된
리뷰는 통과가 아닌 한계로 보고된다.

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details planning-workflow
```

지원하는 클라이언트에서 자연스럽게 작업을 요청한다.

```text
Plan adding CSV export to the reports page. Do not change any files yet.

Implement the approved plan, then review and validate the final revision.
Do not commit or push.
```

자연어 요청은 보통 알맞은 스킬을 선택하지만, 선택은 모델의 판단이며 보장된
훅이 아니다. 스킬을 명시적으로 선택하려면 Codex에서는
`$planning-workflow:planning-work`를, Claude Code에서는
`/planning-workflow:planning-work`를 사용한다. 플러그인이 목록에 있다고 해서
해당 스킬이 실행된다는 증거는 아니다.

### 스킬

- **`planning-work`**는 기능, 여러 풀 리퀘스트에 걸친 변경, 제품 및 UI 기획처럼
  복잡한 작업을 구현 전에 승인받을 설계로 계획한다. 범위를 넓히지 않으면서
  요청된 산출물과 의도한 결과를 구분하고, 이용 가능한 맥락을 읽으며, 계획을
  바꿀 수 있는 미지의 사항만 질문한다. 중요한 가정이 불확실할 때는 이를 반박할
  수 있는 직접적인 근거, 구체적인 방법, 외부 검증을 찾는다. 요구사항이 설계에
  어떻게 반영되는지 추적하고, 발생 가능한 경계 사례를 고려하며, 검증과 전달을
  계획하고, 계획을 Draft 또는 Decided로 표시한다. 가능하면 독립적인 독자를
  활용하고, 그렇지 않으면 자체 리뷰임을 밝힌다. 이는 계획이 작동한다는 증거는
  아니며, 명시적인 승인을 기다린다. 조사와 실험은 더 이상 결정에 영향을 줄 수
  없을 때 중단하고, 계획만 요청받은 경우 읽기 전용으로 진행한다. 계획은 필수
  출력 형식을 따르며 최신 합의에서 다시 이어갈 수 있는 상태를 유지한다.
  [계획 절차](skills/planning-work/SKILL.md)를 참고한다.
- **`executing-work`**는 구현, 독립적인 리뷰, 범위를 정한 정리, 최종 수정본
  검증을 통해 승인된 작업을 조율한다. 유효한 계획을 재사용하고, 커밋, 푸시,
  게시, 병합, 배포 권한을 각각 구분하며, 유용한 경우에만 테스트나 정리를
  위임한다. 하나의 컨트롤러가 해당하는 경우 스킬 기준 리뷰를 포함해 리뷰 요청을
  담당한다. 여러 위치에 하나의 규칙을 반복 적용하는 변경에서는 재실행 가능한
  쿼리로 범위와 적용 범위를 확인하고, 일관된 적용에 필요한 최소한의 수단을
  사용하며, 새로 전체 조사하는 대신 점진적으로 갱신한다.
  [실행 절차](skills/executing-work/SKILL.md)를 참고한다.

계획과 실행에는 [Ponytail의 가장 작은 완전한 변경 원칙][ponytail]을 적용한다.
요청된 동작이나 안전장치를 빠뜨리지 않으면서 적합한 기능을 재사용한다. README와
가이드를 수정할 때 `executing-work`는 절차를 중복하기보다 해당 내용을 관리하는
문서를 우선한다. 이 지침은 스킬과 함께 제공되므로 사용자는 이 저장소의 README가
필요하지 않지만, 관련 스킬은 불러와야 한다.

작고 명확한 변경에는 계획이 필요하지 않다. 스킬은 에이전트의 행동을 안내하며,
훅을 설치하거나 권한을 부여하지 않는다. 전문적인 산출물에는 관련 티켓, ADR,
Git 스킬을 사용한다.

## 기여

풀 리퀘스트를 환영한다. 질문이나 문제는
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues)에 올린다.
[플러그인](../../CONTRIBUTING.md#adding-a-plugin) 및
[테스트](../../CONTRIBUTING.md#testing-a-plugin) 절차를 포함한 저장소의
[기여 가이드](../../CONTRIBUTING.md)를 따른다.

## 라이선스

[MIT](../../LICENSE) © sonsu-lee

[ponytail]: https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md
