# Pattern 관계 타입

관계는 이름 유사성이 아니라 scope와 intent를 설명합니다.

| 타입 | 의미 |
| --- | --- |
| `alias-of` | 같은 scope와 intent의 다른 이름 |
| `same-name-different-scope` | 이름은 같지만 적용 수준이나 guarantee가 다름 |
| `specializes` | target의 더 좁은 context를 다룸 |
| `generalizes` | target 여러 변형의 공통 구조를 다룸 |
| `implements` | target의 상위 원칙·구조를 구체적으로 실현 |
| `commonly-composed-with` | 독립 패턴이지만 한 guarantee를 위해 자주 함께 사용 |
| `alternative-to` | 같은 문제에서 forces에 따라 하나를 선택 |
| `conflicts-with` | 함께 적용하면 guarantee나 ownership이 충돌 |
| `supersedes` | 현재 catalog 정책에서 target을 대체 |

관계만으로 supporting pattern을 자동 선택하지 않습니다. `commonly-composed-with`도 현재 forces와
검증 가능한 guarantee가 있을 때만 조합합니다. 같은 이름을 하나의 전역 패턴으로 합치지 않고
family-prefixed ID와 `same-name-different-scope`로 구분합니다. 서로 다른 family에서 정규화한 이름이
같으면 모든 pair 중 적어도 한 방향에 이 관계를 명시해야 하며 validator가 누락을 거부합니다.
