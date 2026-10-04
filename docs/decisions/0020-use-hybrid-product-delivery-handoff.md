# ADR 0020: 요구사항·설계·티켓·계획 하이브리드 인계

- 날짜: 2026-10-05
- 상태: 채택
- 관련 결정: [ADR 0008](0008-add-product-plugin.md) (보완, 대체 아님)

## 배경

Product는 승인된 제품 합의를 PRD로 바꾸는 데서 끝났고, PRD가 설계 문서·티켓·구현 계획으로
넘어갈 때 무엇을 넘기는지 정한 계약이 없었다. Engineering 계획의 흐름 표에는 요구사항 ID를
연결할 자리가 없어서 PRD의 수용 기준이 티켓과 계획에서 끊겼다. 작은 변경에도 PRD를 만들지,
큰 변경에서 어떤 설계 문서를 남길지 판단 기준도 없었다.

승인 요건은 `to-prd`의 문서 안전 계약과 `product-discovery`의 준비 상태 판정에 따로 적혀
있었고, `conditional`이라는 같은 단어가 제품 합의 상태와 PRD 변환 가능성 두 축에 함께 쓰였다.
판단 근거의 종류도 표기하지 않아 추론이 확인된 사실처럼 결정 근거로 쓰일 수 있었다.

## 결정

고정 단계 대신 작업 크기에 따라 필요한 산출물만 고르는 하이브리드 인계를 채택한다.

- [인계 계약](../../plugins/product/references/delivery-handoff.md)이 작업 크기를 S/M/L로
  판정한다. S는 PRD 없이 티켓이나 구현으로, M은 PRD-lite와 구현 계획으로, L은 전체 PRD →
  필요한 외부 설계 → 티켓 분해 → 구현 계획으로 간다.
- PRD가 있을 때만 REQ ID를 티켓의 `참고`와 Engineering 계획의 흐름 표 `요구사항` 열에
  보존한다. PRD가 없는 작업에는 ID를 만들지 않는다.
- PRD 템플릿에 품질 기대(NFR), 우선순위(P1/P2), 위험(RISK) 행을 둔다. 근거 없는 수치는 OPEN
  항목으로 남긴다.
- 외부 계약(API·데이터·통합)이 바뀌는 기능만 Engineering `brainstorming`의
  [기능 설계 문서 템플릿](../../plugins/engineering/skills/brainstorming/design-doc-template.md)으로
  영속 설계 문서를 남긴다. 내부 구현만 바뀌면 계획에 둔다.
- `plan`, `brainstorming`, `to-prd`는 선택과 판단의 근거에 종류(`[사용자 결정]`,
  `[저장소: 경로:줄]`, `[공식문서: URL]`, `[실험: …]`, `[논문/실무자: URL]`)를 붙이고, 근거
  없는 판단은 `[추론]`으로 표시해 결정 근거로 쓰지 않는다.
- 승인 요건과 상태 어휘는 [승인 기준](../../plugins/product/references/approval.md) 한 곳에 둔다.
- PRD 변환 가능성의 중간 값을 `conditional`에서 `partial`로 바꾼다. 제품 합의 상태와
  frontmatter `workflow_status`의 `conditional`은 그대로 둔다.

## 대안

- **순차형(요구사항정의 → 기본설계 → 상세설계)을 필수 단계로 두는 방식**: 기각한다. ADR 0008의
  "고정 pipeline 아님"과 충돌하고, 작은 변경에도 문서를 강제한다. 명세 주도 개발 도구가 작은
  작업에 과잉 명세를 만든다는 비판도 있다
  ([Fowler, Exploring Gen AI: SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)).
- **현행 유지**: 변경이 없지만 PRD와 티켓·계획 사이의 추적이 끊긴 채 남는다.
- **모든 기능에 설계 문서**: 일관되지만 내부 구현 변경에도 영속 문서가 쌓여 관리 비용이 효용보다 크다.

## 결과

- 크기 판정은 판단을 돕는 기준이며 자동 검사로 강제하지 않는다. 경계 사례는 사람이 정한다.
- REQ 추적은 PRD가 있는 작업에서만 확인할 수 있다.
- 각 플러그인은 다른 플러그인의 설치를 전제로 하지 않는다. 담당 스킬이 없으면 다음 산출물을
  대화로 안내한다.
- 행동 평가는 [product-delivery-handoff](../../evals/product-delivery-handoff/README.md)에 두며
  현재 `not_run`이다.
- 참고한 실무 자료: [Kiro Specs](https://kiro.dev/docs/specs/),
  [Spec Kit](https://github.com/github/spec-kit),
  [IPA 비기능 요구 등급](https://www.ipa.go.jp/archive/digital/iot-en-ci/jyouryuu/hikinou/ent03-b.html)

## 다시 볼 때

- 크기 판정이 실제 요청에서 자주 엇갈리거나 S로 판정한 작업에서 요구사항 누락이 반복될 때
- 티켓·계획에서 REQ ID 보존이 평가에서 꾸준히 실패할 때
- Product 밖의 담당(디자인·티켓 작성)이 별도 인계 형식을 요구할 때
