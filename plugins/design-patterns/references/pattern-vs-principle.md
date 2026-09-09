# Pattern, principle과 직접 해법

## 구분

| 종류 | 판단 기준 | 예 |
| --- | --- | --- |
| Pattern | 반복되는 context에서 forces를 균형 잡고 명시적 비용으로 guarantee를 제공 | Strategy, Saga, Unit of Work |
| Principle | 여러 설계에서 방향을 제시하지만 완성된 구조를 정하지 않음 | dependency inversion, information hiding |
| Idiom | 특정 언어의 기본 표현으로 해결 | Python context manager, Rust enum matching |
| Framework feature | 플랫폼이 lifecycle과 보장을 이미 소유 | ORM unit of work, broker dead-letter policy |
| Direct solution | 현재 한 사례를 가장 작은 코드로 해결 | 함수, 분기, 작은 module |

패턴은 정답 목록이 아닙니다. 같은 표면 구조도 scope와 intent가 다르면 다른 패턴이고, 다른 코드
형태도 같은 guarantee를 제공하면 같은 패턴의 language realization일 수 있습니다.

## Baseline 우선

먼저 직접 해법을 적고 다음 질문을 확인합니다.

- baseline이 실제로 어디서 깨지는가?
- 그 실패는 현재 요구인가, 미래 추측인가?
- 패턴이 추가하는 guarantee가 무엇인가?
- 표준 기능이 이미 같은 guarantee를 더 안정적으로 제공하는가?
- 패턴 이름 없이 구현해도 의도가 충분히 드러나는가?

답이 없으면 패턴을 추가하지 않습니다. 단순히 객체가 많다, `switch`가 있다, 비동기 통신을 쓴다는
사실만으로 pattern trigger가 되지 않습니다.
