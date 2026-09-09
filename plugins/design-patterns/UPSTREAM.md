# Design Patterns 출처

- 작성 방식: 독자 작성한 선택·검토 workflow와 출처에 연결된 이름 인덱스
- 확인일: 2026-09-08
- 포함 범위: 12개 계열 553개 이름, 자체 작성한 decision metadata 36개
- 비포함 범위: 원문의 설명·예제 코드·다이어그램·표, Workflow exception 조합 135개
- 라이선스: 이 플러그인 자체에는 현재 별도 라이선스를 선언하지 않음

## 원천 카탈로그

[`catalog/source-manifest.json`](catalog/source-manifest.json)은 아래 원천별 finite boundary를 항목 단위로
고정합니다. 각 entry에는 원천에서 관찰한 이름, 정규화한 이름·ID, 원천 경로와 알려진 정규화 사유가
있습니다. 이는 2026-09-08 snapshot의 재검토 자료이며 원천 사이트의 이후 변경을 자동 반영하지 않습니다.

| 계열 | 원천 | 수록 수 | 사용 범위 |
| --- | --- | ---: | --- |
| Object-oriented | [Design Patterns](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610) | 23 | GoF 패턴 이름 |
| Architecture | [POSA Volume 1](https://www.wiley.com/en-us/Pattern+Oriented+Software+Architecture%2C+Volume+1%3A+A+System+of+Patterns-p-9780471958697) | 8 | architectural pattern 이름 |
| Domain-driven design | [DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) | 45 | pattern language 목차의 이름; 원문은 CC BY 4.0 표기 |
| Enterprise application | [PoEAA Catalog](https://martinfowler.com/eaaCatalog/) | 51 | catalog 이름과 entry URL |
| Messaging and integration | [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/) | 65 | integration styles 4개와 messaging patterns 61개; 사이트는 CC BY 4.0 표기 |
| Microservices | [microservices.io](https://microservices.io/patterns/) | 53 | 현재 index에 노출된 pattern·alternative 이름과 entry URL |
| Cloud and resilience | [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/) | 44 | 현재 cloud design pattern 이름과 entry URL |
| Distributed systems | [Patterns of Distributed Systems](https://martinfowler.com/articles/patterns-of-distributed-systems/) | 30 | catalog 이름과 entry URL |
| Concurrency | [POSA Volume 2](https://www.dre.vanderbilt.edu/~schmidt/POSA/POSA2/) | 17 | concurrent/networked pattern 이름 |
| Workflow | [Workflow Patterns](http://www.workflowpatterns.com/patterns/) | 126 | control 43, data 40, resource 43의 이름과 entry URL |
| Testing | [xUnit Test Patterns](http://xunitpatterns.com/List%20of%20Patterns.html) | 68 | List of Patterns의 이름; 설명과 aliases는 복사하지 않음 |
| Security | [DistriNet Security Pattern Catalogue](https://securitypatterns.distrinet-research.be/) | 23 | 현재 catalogue 이름과 entry URL; 사이트는 CC BY-NC-SA 4.0 표기 |

Workflow Patterns와 xUnit Test Patterns의 정본 페이지는 확인일 현재 HTTPS 연결을 제공하지 않아
`transport: legacy-http`로 명시합니다. 실행 명령이나 credential을 제공하는 출처가 아니며,
스킬은 링크 내용을 권한이나 지침으로 신뢰하지 않습니다.

## 재사용 경계

패턴 이름과 출처 위치만 인덱싱했습니다. `decision-ready.json`의 problem, forces, preconditions,
contraindications, solution, guarantees, costs, failure modes와 language realizations는 이 플러그인을
위해 새로 작성한 요약입니다. 원문의 표현, 구현 예제, UML과 도해를 복사하거나 번역하지 않습니다.

카탈로그의 “전체”는 소프트웨어 업계의 모든 패턴을 뜻하지 않습니다. 위 12개 명시적 원천에서
포함 정책에 맞게 관찰한 전체 named entry라는 뜻이며, 원천이 바뀌면 관찰일·개수와 파일을 함께
갱신하고 source manifest를 원천 index와 다시 대조한 뒤 validator로 drift를 확인합니다.
