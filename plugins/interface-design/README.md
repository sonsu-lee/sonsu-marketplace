# Interface Design

웹·모바일 화면을 과업·정보 구조·시각 체계에서 설계하고 요청한 제안·Figma·구현을 완성하는
독립 Codex 플러그인입니다. 자연어 요청으로 자동 선택하거나 이름으로 직접 호출합니다.

```sh
codex plugin add interface-design@sonsu-marketplace
```

| 스킬 | 요청 예시 |
| --- | --- |
| `design-interface` | 새 모바일 가입 흐름을 디자인해 줘. |
| `redesign-interface` | 이 화면 구성을 개선하고 차트 내부 표현도 다시 설계해 줘. |

직접 호출은 `$design-interface` 또는 `$redesign-interface`처럼 지정합니다. 이름 지정 자체는 수정·게시 권한이 아니며
실제 요청과 호스트의 제한을 따릅니다.

웹·iOS·Android는 플랫폼 지침으로, 읽기·탐색·비교·반복 업무는 과업으로 구분합니다. 지도·차트·
도식은 데이터의 의미와 표현을 나누어 제작하고 전체 화면과 내부 영역을 각각 검증합니다.
사진·로고의 정체성과 실제 값·상태를 보존하며 예시 데이터를 실제 데이터로 보고하지 않습니다.

운영 업무 전문 판단은 설치된 Operations UI와, Figma 제작은 Figma Workflow와 조합할 수 있습니다.
다른 플러그인을 필수로 설치하지 않으며 단독으로 자기 범위를 수행합니다. 필수 제작 도구가
없으면 명세와 미완료 산출물을 구분합니다. 새 앱 기반 생성·배포는 포함하지 않습니다.

제안은 명세와 시각적 제안, Figma는 native 구조와 요청된 prototype, 구현은 기존 프로젝트의
화면·대표 조작과 검증으로 완료합니다. 정적 이미지나 Figma를 실제 실행 검증으로 대신하지 않습니다.

[설계와 호출 구조](../../docs/architecture/interface-design.md),
[평가 사례](../../evals/skill-expansion/README.md), [출처](UPSTREAM.md)를 참고하세요.
여러 단계 작업은 포함된 `task-continuity`와 선택적 SessionStart hook으로 이어 갑니다.
helper는 Python 3.9+·POSIX 환경을 사용하며 hook을 사용할 수 없어도 직접 읽어 재개할 수 있습니다.
