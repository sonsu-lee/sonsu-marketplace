# 티켓 선택 규칙

## 양식 출처를 먼저 확인한다

1. 사용자가 지정한 양식 또는 제공한 template
2. 대상 repository·팀·project의 적용 가능한 양식과 작성 지침
3. 이 플러그인의 종류별 기본형

repository의 issue template·form·기여 지침과 tracker의 팀·project template을 확인한다. repository에 파일이 없다는 이유만으로 Linear 팀 양식도 없다고 판단하지 않는다. 여러 양식이면 명시된 선택 규칙과 주된 결과로 고른다. 선택 근거가 부족하면 후보와 이유를 초안에 표시한다.

중립 초안 또는 적용할 양식이 없다고 확인한 대상은 기본형을 사용한다. 접근 불가로 확인하지 못했다면 `unverified`로 표시하고 기본형을 임시 draft로 사용할 수 있다. 게시 전 적용 양식·필수 field를 확인하거나, 미확인 한계를 밝힌 뒤 기본형 사용에 대한 사용자의 명시적 선택을 따른다. 그 선택으로 interface의 필수 field를 생략하지 않는다.

기존 티켓의 부분 수정에서는 현재 heading·순서·필수 항목을 유지한다. 새 template 전체로 재작성하는 것은 사용자가 요청했을 때만 한다. 유효한 양식이 있으면 아래 종류·구조는 필요한 의미를 판단하는 기준이며 대응하는 기존 section에 작성한다. 기본형을 뒤에 이어 붙이지 않는다.

## 종류는 주된 결과로 고른다

아래 표에서 해당하는 파일 하나만 읽는다. 표의 이름은 플러그인 template key이며 tracker type·label을 새로 만드는 지시가 아니다.

| 주된 목적 | Template | 구분 기준 |
| --- | --- | --- |
| 잘못된 동작 보고·복구 | [bug](../assets/templates/bug.md) | 관찰된 기대·실제 동작의 차이 |
| 기능 제안·채택 검토 | [feature-request](../assets/templates/feature-request.md) | 구현 여부·범위가 미정인 요청 |
| 합의된 기능 제공 | [feature](../assets/templates/feature.md) | 사용자·시스템 결과의 구현 |
| 질문·불확실성 해소 | [investigation](../assets/templates/investigation.md) | 판단에 필요한 근거·결론 |
| 리팩터링·dependency·설정·문서 정비 | [maintenance](../assets/templates/maintenance.md) | 내부 개선과 기존 속성 보존 |
| QA·접근성·성능 등 독립 검증 | [validation](../assets/templates/validation.md) | 정해진 대상·기준에 대한 판정 |
| 진행 중 장애 대응 | [incident](../assets/templates/incident.md) | 서비스 복구·영향 억제 |
| 반복 장애의 원인·재발 방지 | [problem](../assets/templates/problem.md) | incident를 넘는 원인·관리 결정 |
| 사고 회고 기록 | [postmortem](../assets/templates/postmortem.md) | 타임라인·요인·학습·후속 조치 기록 |
| 배포·단계적 공개·feature flag 전환 | [rollout](../assets/templates/rollout.md) | 환경·대상군에 실제 제공 |
| 데이터·schema·환경 전환 | [migration](../assets/templates/migration.md) | 이전 상태에서 목표 상태로 안전하게 이동 |
| 권한·지원·계정·환경 요청 | [service-request](../assets/templates/service-request.md) | 정해진 서비스 절차의 이행 |
| 취약점 접수·보안 개선 | [security](../assets/templates/security.md) | 제한된 정보 취급과 보안 결과 |

여러 종류가 겹치면 주된 완료 주장을 고른다. 현재 장애 복구는 incident, 재발 방지 조사는 problem, 회고 문서는 postmortem이다. 단순 dependency 갱신은 maintenance, 데이터 변환·cutover가 결과이면 migration이다. validation은 독립 판정 자체가 결과일 때만 분리한다. 작은 기능의 일반 테스트·배포는 기능 티켓 안에 둘 수 있다.

기존 tracker·업무 도메인 용어를 보존한다. adapter에서 중립 `kind`가 필요하면 bug는 `defect`, 승인된 기능 제공은 `delivery`, 질문 해소는 `investigation`, 내부 유지 작업은 `maintenance`로 참고할 수 있다. 나머지를 억지로 이 네 값에 맞추지 않고 실제 관례를 확인한다. `kind`는 native metadata를 확정하는 근거가 아니다.

## 구조는 종류와 별도로 고른다

- `single`: 독립 완료 가능한 한 결과. 추가 구조 파일을 읽지 않는다.
- `parent`: 여러 독립 결과의 전체 목표를 추적할 때 [부모 구조](../assets/structures/parent.md)를 읽는다.
- `child`: 상위 결과 중 일부를 맡을 때 [자식 구조](../assets/structures/child.md)를 읽는다.

부모도 feature·migration 등의 성격을 가질 수 있다. Epic·project·parent·subtask의 실제 hierarchy 매핑은 대상 tracker에서 확인한다. 부모라고 자동으로 project를 만들거나 자식 수를 늘리지 않는다.

## 준비 상태와 다음 단계를 판단한다

| 준비 상태 | 최소 근거 | 작성 결과 |
| --- | --- | --- |
| `intake` | 관찰된 문제·검토할 요청·답할 질문과 맥락 | 확인된 사실, 영향·원하는 결과, 미해결 질문 |
| `execution-ready` | 실행할 결과·범위·중요한 제약·판정 기준이 합의됨 | 맡아서 완료할 수 있는 계약 |
| `needs-information` | 문제·요청·질문을 특정할 근거가 부족함 | 보존 가능한 내용과 가장 중요한 누락 질문 |

이 값은 tracker의 Triage·Ready·In Progress 같은 status가 아니다. `intake`를 게시해도 착수나 채택을 뜻하지 않는다. incident 대응은 원인 미상이어도 복구 대상·목표·대응 경계가 확인되면 준비될 수 있다. 준비 상태를 판정하려고 구현 방법을 미리 요구하지 않는다.

같은 목적이 구체화되면 기존 티켓을 `revise`한다. 기능 제안이 채택되면 같은 티켓에 합의 범위를 보강할 수 있으며 새 기능 티켓을 반드시 만들지 않는다. 별도 결과·책임·완료 판정이 필요하면 분리하고 실제 관계를 명시한다. 시간 순서만으로 blocking을 만들지 않고 후속 작업이 앞선 결과 없이는 진행할 수 없을 때만 dependency를 쓴다.
