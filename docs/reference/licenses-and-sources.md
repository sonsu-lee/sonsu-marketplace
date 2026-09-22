# 플러그인별 라이선스와 출처

저장소 전체에 공통 root-level license는 없습니다. 각 package의 포함물과 검토 자료를 구분합니다.

- **Code Review**: 가져온 review 자료의 [MIT](../../plugins/code-review/LICENSE)와
  [Apache-2.0](../../plugins/code-review/LICENSE-APACHE-2.0) 조건을 따릅니다.
  [NOTICE](../../plugins/code-review/NOTICE), [UPSTREAM](../../plugins/code-review/UPSTREAM.md),
  [THIRD_PARTY_NOTICES](../../plugins/code-review/THIRD_PARTY_NOTICES.md)에 exact 포함 범위와 원문 고지를
  보존합니다. Code Forge 기준 commit은 `1779c8ac9638c755d341b16e708f7e44aaf15b75`입니다.
- **Code Intelligence**: marketplace는 mcpls binary를 재배포하지 않습니다. runtime dependency는
  `mcpls 0.6.0`, upstream commit `6b06d1af30292b71d2e4af05928cfb3bcd9856b1`, MIT OR Apache-2.0입니다.
  설치·업데이트는 사용자가 별도로 수행합니다. 세부 경계는
  [UPSTREAM](../../plugins/code-intelligence/UPSTREAM.md)과
  [THIRD_PARTY_NOTICES](../../plugins/code-intelligence/THIRD_PARTY_NOTICES.md)에 있습니다.
- **Developer Writing**: package license와 provenance는
  [LICENSE](../../plugins/developer-writing/LICENSE), [UPSTREAM](../../plugins/developer-writing/UPSTREAM.md),
  [THIRD_PARTY_NOTICES](../../plugins/developer-writing/THIRD_PARTY_NOTICES.md)에 있습니다. kdy1의 공개
  scripts commit `92a8fbe9a57bce5064ed7dba3a8f87f331930dc6`은 consulted-only이며 해당 repository code를
  package에 포함하지 않습니다.
- **Workflow**, **Prompting**, **Product**: 현재 별도 package license를 선언하지 않습니다. 외부에서
  실제 포함한 내용과 검토-only 자료는 각 package `UPSTREAM.md`가 있는 경우 그 파일에 기록합니다.
- **Interface Design**, **Operations UI**, **Figma Workflow**: 외부 UI code나 asset을 복사하지 않은
  독자 작성 절차입니다. 검토한 자료와 비복사 경계는 각 package의 `UPSTREAM.md`에 기록합니다.
- **Design Patterns**: 원천 catalog의 이름과 출처를 index하고 selection/review 계약과 설명은 독자
  작성했습니다. 포함 범위와 원천별 조건은
  [UPSTREAM](../../plugins/design-patterns/UPSTREAM.md)에 기록합니다.

ADR의 historical/consulted-only 근거는 package redistributable content가 아닙니다. 아이디어를 검토한
사실을 license grant나 파일 포함으로 바꾸지 않습니다. 외부 runtime, provider connector, language
server의 설치와 이용 조건은 각 공급자가 소유합니다.
