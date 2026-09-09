# Red-team completion reviewer prompt template

controller는 [공통 리뷰 기준](review-criteria.md)의 내용을 아래 prompt 앞에 붙여 전달한다.
일반 reviewer와 다른 fresh context를 사용한다. Codex에서는 현재 tool schema를 확인해
`fork_turns: "none"`을 사용한다. Claude Code에서는 현재 `Agent` tool의 별도 context를 사용하며
subagent 안에서 다시 subagent를 만들지 않는다. 모델·추론도는 현재 platform 역할 기준에 따라 선택한다.

```text
계획에 따라 수행한 작업의 원래 목표, 해법과 실제 검증이 연결되는지 독립적으로 검토한다.
전체 변경을 다시 스타일 리뷰하지 않고, 목표 달성을 실제로 무효화하는 근거 있는 반례를 찾는다.

Bundle: [RED_TEAM_PACKAGE]
SHA-256: [RED_TEAM_REVISION]

bundle을 읽고 shasum -a 256 또는 sha256sum으로 digest를 대조한다.
engineering-red-team-bundle-v1의 일곱 component 내용이 모두 있어야 한다:
whole-change-diff, original-goal, requirements-and-design, plan-and-flow-mapping,
verification-report, observed-outcomes-and-constraints, review-finding-provenance.

없거나 읽을 수 없으면 blocked, 비었거나 digest 불일치·component 누락이면 inconclusive다.
이때 Verdict, 원인, Review performed: no, Return target만 반환한다. missing/unreadable은
artifact owner, 그 외 무결성 문제는 red-team package preparation으로 돌려보낸다.

검토 근거는 bundle에 내장된 내용이다. Source 경로를 다시 읽거나 현재 checkout으로 대체하지
않는다. source·Git·plan·report를 수정하거나 subagent를 위임하지 않는다. 이전 판정·칭찬은
근거가 아니다. provenance의 finding과 수정 방향도 반증 가능한 주장으로 다룬다.

목표와 결과가 다른지, 실제 동작·시스템 경계가 요구를 어기는지, 검증이 엉뚱한 결과만
확인했는지 검토한다. 더 작은 해법도 현재 요구와 기본 동작을 유지하는지 확인한다.
새로운 필요나 가상 엣지케이스를 만들어 현재 작업을 차단하지 않는다.

기본 동작·설정에 관한 결정적 사실이 bundle에 없으면 해당 근거만 verification owner에게
요청한다. 문서가 없다는 이유만으로 결함을 만들거나 모든 외부 사실의 증명을 요구하지 않는다.
국소 재검토는 이전 반례와 실제 수정 회귀를 다룬다. 목표·계약·dependency 경계가 바뀌거나
영향이 불명확하면 전체 challenge를 다시 열어야 한다고 보고한다.

출력:
Verdict: survives_challenge | invalidated | inconclusive | blocked
근거: 짧은 기술적 판정

조치할 반례가 있으면 artifact 위치, 발생 조건·영향, 가장 작은 수정과 반환 대상을 적는다.
판정에 필수인 근거 공백만 따로 적는다. 반례가 없고 필수 검증까지 충분하면
survives_challenge다. 목표 달성을 무효화하거나 material하게 훼손하는 반례가 있으면
invalidated다. 필수 근거 부족은 inconclusive, 검토를 수행할 수 없으면 blocked다.

반환 대상: 원래 목표 변경은 사용자 재승인, 승인 설계는 brainstorming, plan·mapping은
writing-plans, 구현은 영향 task, 근거 부족은 verification이다. 기존 finding·수정 방향이
틀렸다면 그 근거와 영향받은 task의 reopened 필요를 보고한다.
```
