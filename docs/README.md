# 문서 안내

이 디렉터리는 marketplace와 capability pack을 장기간 유지하는 지식을 보관합니다. 구현 순서만 있는
계획은 대화, 기존 issue/ticket 또는 사용자가 지정한 위치에 두며 단지 계획이라는 이유로 `docs/`에
추가하지 않습니다.

## 문서 배치 기준

| 질문 | 위치 |
| --- | --- |
| 현재 구조와 routing은 무엇인가? | [`architecture/`](architecture/) |
| 왜 이 선택을 했는가? | [`decisions/`](decisions/) |
| 제품 범위와 성공 조건은 무엇인가? | [`product/`](product/) |
| 목표를 어떻게 수행하는가? | [`guides/`](guides/) |
| 정확한 field와 계약은 무엇인가? | [`reference/`](reference/) |
| 반복 유지보수 절차는 무엇인가? | [`runbooks/`](runbooks/) |
| 조사 corpus와 분석 방법은 무엇인가? | [`research/`](research/) |

현재 계약을 설명하는 문서는 구현과 함께 갱신합니다. 작업 log와 일회성 검사 결과는 task report,
PR 또는 issue에 남깁니다. 새 문서는 독립된 읽기 목적이 있고 기존 정본에 맞는 위치가 없을 때만
만듭니다.

## 승인 경계

설계, 문서 작성, code edit, commit, push, PR/issue 게시와 deploy는 서로 다른 권한입니다. 한번 승인한
현재 범위는 반복해서 묻지 않지만, 한 단계의 승인을 다음 remote action으로 확대하지 않습니다.

## 이름과 수명

아키텍처·가이드·참조·runbook은 날짜 없는 안정된 주제 이름을 사용합니다. 결정 기록은
`NNNN-<decision>.md`이고 대체된 결정은 내용을 보존한 채 `Superseded`와 새 ADR 링크를 남깁니다.
실제 내용이 없는 folder나 placeholder 문서는 만들지 않습니다.

## 현재 문서

- [마켓플레이스 아키텍처](architecture/overview.md)
- [플러그인 생명주기와 observability](architecture/plugin-lifecycle.md)
- [스킬 라우팅과 exact ownership](architecture/skill-routing.md)
- [Interface Design과 디자인 책임](architecture/interface-design.md)
- [얇은 capability pack 결정](decisions/0015-use-thin-capability-packs.md)
- [마켓플레이스 요구사항](product/marketplace-requirements.md)
- [플러그인 개발·수정·추가](guides/adding-a-plugin.md)
- [플러그인 manifest](reference/plugin-manifest.md)
- [플러그인별 license와 source](reference/licenses-and-sources.md)
- [upstream plugin 업데이트](runbooks/updating-upstream-plugin.md)
- [Madia Designer 실무 관찰 방법](research/madia-design-practice-method.md)
- [Madia Designer 공개 영상 catalog](research/madia-design-practice-catalog.md)

ADR 0001–0014는 결정 당시의 구조를 보존합니다. `Superseded` ADR의 plugin path, model roster와 hook
설명은 현재 실행 계약이 아닙니다.
