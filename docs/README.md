# 문서 안내

이 디렉터리는 마켓플레이스와 플러그인을 장기간 유지하는 데 필요한 지식을 보관합니다.
구현 순서만 담은 작업 계획은 기본적으로 대화, 기존 이슈·티켓 또는 Git에서 제외된
`.superpowers/plans/`에 두며, 단지 계획이라는 이유로 `docs/`에 저장하지 않습니다.

## 문서 배치 기준

| 질문 | 위치 | 변경 방식 |
| --- | --- | --- |
| 시스템은 현재 어떻게 구성되어 있는가? | [`architecture/`](architecture/) | 현재 상태에 맞춰 갱신 |
| 왜 이 선택을 했고 어떤 대안을 포기했는가? | [`decisions/`](decisions/) | 기존 기록을 보존하고 새 결정으로 대체 |
| 무엇을 만들며 성공 조건은 무엇인가? | [`product/`](product/) | 제품 범위가 바뀔 때 갱신 |
| 특정 목표를 어떻게 달성하는가? | [`guides/`](guides/) | 절차가 바뀔 때 갱신 |
| 정확한 형식, 필드와 계약은 무엇인가? | [`reference/`](reference/) | 구현과 일치하도록 갱신 |
| 반복 작업을 어떻게 실행, 검증하고 복구하는가? | [`runbooks/`](runbooks/) | 실제 실행 가능성을 유지 |

새 문서를 만들기 전에 `README.md`, `CONTEXT.md`, `docs/**`, 기존 이슈와 티켓을
검색합니다. 관련 문서가 있으면 새 날짜 문서를 만들기보다 기존 문서를 갱신합니다.
두 위치가 모두 가능해 보이면 문서가 답해야 하는 주된 질문으로 분류합니다.

## 계획과 문서 처리

설계 또는 구현 계획을 시작할 때 문서 영향을 다음 중 하나로 분류합니다.

1. 문서 변경 없음
2. 기존 문서 갱신
3. 새 문서 생성
4. 기존 결정 대체

새 문서나 큰 문서 재구성이 필요하면 구현 전에 검토한 기존 문서, 제안 경로,
목적과 예상 변경 범위를 사용자에게 제시합니다. 구현 계획은 기본적으로 대화에
작성합니다. 파일이 필요한 실행 도구를 사용할 때에는 `.superpowers/plans/<topic>.md`를
사용합니다. 저장소가 이미 이슈·티켓 또는 다른 계획 위치를 사용하거나 사용자가 위치를
지정하면 그 규칙을 우선합니다.

## 승인 경계

- 설계 승인은 문서 파일 작성 승인이 아닙니다.
- 문서 작성 승인은 코드 구현 승인이 아닙니다.
- 문서나 구현 승인은 Git 커밋 승인이 아닙니다.
- 커밋은 현재 작업에서 사용자가 명시적으로 요청했거나 승인한 경우에만 수행합니다.
- 한 번 승인한 범위 안에서는 같은 권한을 반복해서 묻지 않습니다.
- push, PR 생성, merge와 배포는 커밋과 별개의 권한입니다.

## 이름과 수명

- 아키텍처, 제품, 가이드, 참조와 런북은 날짜가 없는 안정적인 주제 이름을 사용합니다.
- 날짜가 필요하면 문서 안의 `Date` 또는 `Last reviewed`에 기록합니다.
- 결정 기록은 `0001-<decision>.md` 형식의 순번을 사용합니다.
- 대체된 결정은 내용을 지우지 않고 `Superseded` 상태와 새 결정 링크를 남깁니다.
- 실제 내용이 없는 폴더와 자리표시자 문서는 만들지 않습니다.

## 현재 문서

- [마켓플레이스 아키텍처](architecture/overview.md)
- [플러그인 생명주기](architecture/plugin-lifecycle.md)
- [스킬 라우팅](architecture/skill-routing.md)
- [플러그인 독립성과 runtime 라우팅 결정](decisions/0003-keep-plugins-independent.md)
- [Research 독립성과 선택적 provider 결정](decisions/0004-keep-research-independent.md)
- [Engineering 이름 변경 결정](decisions/0005-rename-superpowers-to-engineering.md)
- [Prompting 독립 플러그인 결정](decisions/0006-keep-prompting-independent.md)
- [마켓플레이스 요구사항](product/marketplace-requirements.md)
- [플러그인 추가 가이드](guides/adding-a-plugin.md)
- [플러그인 매니페스트 참조](reference/plugin-manifest.md)
- [업스트림 플러그인 업데이트 런북](runbooks/updating-upstream-plugin.md)
