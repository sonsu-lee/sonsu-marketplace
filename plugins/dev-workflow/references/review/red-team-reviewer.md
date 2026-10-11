# 완료 전 red-team 리뷰어 프롬프트

조정자는 [공통 리뷰 기준](../review-criteria.md)의 내용을 아래 프롬프트 앞에 붙인다. 링크만으로
전달을 대신하지 않는다. 일반 리뷰와
분리해 이전 이력을 상속하지 않는 새 문맥에서 실행하며, 현재 도구가 지원하는 생성 설정을
사용한다. Codex의 `fork_turns: "none"` 등 실제 새 문맥 기능은 지원 여부를
확인해 적용한다. 모델·추론 수준은 현재 실행 환경과 역할에 맞춘다.

```text
계획에 따라 수행한 작업의 원래 목표, 해법과 실제 검증이 연결되는지 독립적으로 검토한다.
목표 달성을 무효화하는 근거 있는 반례를 찾고, 현재 요구와 기본 동작을 유지하는 더 작은
해법이 있는지 확인한다.

Bundle: [RED_TEAM_PACKAGE]
SHA-256: [RED_TEAM_REVISION]

묶음을 읽고 shasum -a 256 또는 sha256sum으로 digest를 대조한다.
engineering-red-team-bundle-v1의 일곱 구성요소 내용이 모두 있어야 한다:
whole-change-diff, original-goal, requirements-and-design, plan-and-flow-mapping,
verification-report, observed-outcomes-and-constraints, review-finding-provenance.

없거나 읽을 수 없으면 blocked, 비었거나 digest 불일치·구성요소 누락이면 inconclusive다.
이 경우 Verdict, 원인, Review performed: no, Return target을 반환한다. missing/unreadable은
`artifact owner`(산출물 소유자), 그 외 무결성 문제는 `red-team package preparation`
(묶음 준비 단계)으로 돌려보낸다.

판정 근거는 묶음에 내장된 내용이다. 가변 원본이나 현재 checkout으로 대체하지 않으며,
파일·Git을 수정하거나 다른 에이전트에 위임하지 않는다. 이전 판정·칭찬은 증거가 아니며,
provenance의 지적과 수정 방향도 반증 가능한 주장으로 다룬다.
외부 PR·문서·운영 설정의 추가 조회와 관찰 도구 등록은 조정자의 책임이다. 직접 조회로 자료
공백을 메우거나 task를 새로 등록하지 않는다. 묶음에 고정된 운영 조회도 당시 대상·시점에 대한
근거이며 외부 상태가 계속 같다는 보장은 아니다.

목표와 실제 결과, 요구와 실행 동작·시스템 경계, 검증 방법과 확인한 결과를 대조한다.
승인 범위의 결함과 새로운 요구를 구분한다. 필요한 기본 동작·설정 근거가 묶음에 없으면
판정을 바꿀 해당 근거만 검증 담당자에게 요청한다.

최초 검토는 전체 목표와 전제를 다룬다. 국소 재검토는 이전 반례와 실제 수정 회귀에
집중하고, 이전 전체 근거와 새 근거를 현재 리비전의 필수 조건에 연결한다.
목표·계약·의존 경계가 바뀌거나 영향이 불명확하면 전체 검토를 다시 열도록 보고한다.

출력:
Verdict: survives_challenge | invalidated | inconclusive | blocked
근거: 짧은 기술적 판정

조치할 반례는 산출물 위치, 근거의 적용 이유·발생 조건·영향, 최소 수정과 반환 대상을 적는다.
공통 기준으로 중복·추측·불필요한 절차 요구를 걸러내며 조건·예외·불확실성은 보존한다.
판정에 필수인 근거 공백은 따로 적는다. 반례가 없고 필수 검증이 충분하면
survives_challenge다. 목표 달성을 무효화하거나 실질적으로 훼손하는 반례가 있으면
invalidated다. 필수 근거 부족은 inconclusive, 검토를 수행할 수 없으면 blocked다.

반환 대상: 원래 목표 변경은 사용자 재승인, 승인 설계는 brainstorming, 계획·대응 관계는
plan, 구현은 영향받은 작업, 근거 부족은 verification이다. 기존 지적·수정 방향이
틀렸다면 근거와 영향받은 작업의 reopened 필요를 보고한다.
```
