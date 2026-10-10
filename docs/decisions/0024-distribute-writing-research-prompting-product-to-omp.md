# ADR 0024: Writing·Research·Prompting·Product의 omp 선택 배포

- 날짜: 2026-10-09
- 상태: 채택
- 관련 결정: [ADR 0015](0015-independent-skills.md), [ADR 0022](0022-add-worklog-plugin.md), [ADR 0023](0023-remove-career-plugin.md)

## 맥락

omp의 검색·위임·질문·세션 기능은 작업 실행을 제공하지만 도메인별 산출물의 판단 기준을 모두 대신하지는 않는다.
리팩터링 인벤토리는 다음 이유로 네 플러그인의 `omp.proposal`을 `opt-in`으로 판정했다.

| 플러그인 | 인벤토리의 선택 배포 근거 |
| --- | --- |
| [Writing](../research/refactor-inventory/writing.json) | 일반 답변마다 필요하지는 않지만 문서 체계 정리와 개발자 글 작성에 고유 가치가 있다. 세션 관리는 호스트에 맡긴다. |
| [Research](../research/refactor-inventory/research.json) | 일반 검색·병렬 실행·세션 복구와 달리 주장별 증거 감사와 버전을 고정한 코드 사례 조사에 별도 가치가 있다. 공급자 라우팅과 연속성 hook을 호스트 계약에 맞춰 분리해야 한다. |
| [Prompting](../research/refactor-inventory/prompting.json) | 다른 모델·제품에 전달할 프롬프트 작성은 omp subagents 실행과 다른 과업이다. Codex·Claude 실행 프로필과 연속성 hook을 omp 실행 설정에서 분리해야 한다. |
| [Product](../research/refactor-inventory/product.json) | 제품 탐색과 실험 판정은 질문·검색·세션 기능만으로 대체되지 않는 전문 과업이다. 연속성 처리는 omp 세션 경로를 사용해야 한다. |

선택 배포의 효용은 인벤토리의 추론을 채택한 것이며 실제 설치·행동 평가의 성공을 뜻하지 않는다.
네 원본 패키지에는 Codex·Claude용 `SessionStart` hook과 `task-continuity.py`가 있으므로 원본을 그대로 omp에 연결하지 않는다.

## 결정

- `writing`, `research`, `prompting`, `product`를 `OMP_OPTIN_PLUGINS`와 `ISOLATED`에 추가한다.
  기본 5개는 유지하고 기존 opt-in Design Patterns·Worklog와 함께 필요한 사용자가 직접 설치한다.
- 네 패키지는 `plugins/<name>/omp`에 스킬·참고 자료·자산·도메인 스크립트·라이선스 사본을 생성한다.
  hook·연속성 실행기·역할 agent·runtime extension을 추가하지 않고 `shared/omp-runtime/continuity.md`로
  omp 순정 todo·session 안내를 주입한다. 도메인 스크립트의 내용과 실행 권한은 보존한다.
- Research는 현재 노출된 읽기 전용 도구와 capability 기반 fallback을 사용한다. 공급자 자동 설치나
  연결 권한을 추가하지 않는다. 직접 API adapter의 opt-in marker를 유지하도록 패키지 README를 생성한다.
  README의 공급자 설정은 원본을 유지하고 설치·연속성 안내만 omp 기준으로 바꾼다.
  Prompting의 Codex·Claude 프로필에는 작성 대상 프롬프트의 참고 자료라는 안내를 붙여 현재 omp의
  모델·effort·역할 선택과 분리한다.

## 대안

- **원본 패키지 직접 참조**: Design Patterns처럼 `./plugins/<name>`을 그대로 쓰면 사본이 없지만,
  원본의 `SessionStart` hook과 `task-continuity.py`가 omp에 함께 설치된다.
- **기본 묶음에 추가**: 설치 단계는 줄지만 일반 요청마다 네 도메인의 스킬이 라우팅 후보에 더해진다.
- **omp 배포 제외 유지**: 기본 구성은 단순하지만 omp 사용자는 카탈로그 밖 경로로 설치해야 하고
  업데이트를 받지 못한다.

## 결과

omp 카탈로그는 Codex 순서로 기본 5개와 opt-in 6개, 총 11개를 제공한다. Codex·Claude 카탈로그의
13개 플러그인과 원본 패키지는 유지한다. 설치만으로 기존 omp 설정이나 실행 정책을 바꾸지 않는다.

생성기는 패키지 사본과 소유권 목록을 관리한다. 계약 테스트는 카탈로그 순서·격리 경로·상대 링크,
연속성 교체, 실행기 제외, 도메인 스크립트 보존과 대상 모델 안내를 검사한다. 정적 패키지 검증과
사용자 환경의 실제 설치·호출 결과는 구분한다.

## 다시 볼 때

- 원본 패키지에서 hook·연속성 실행기가 빠져 omp에서 원본을 직접 참조할 수 있을 때
- 명시적 요청 없이도 네 도메인 스킬이 반복 사용되어 기본 묶음 승격이 필요할 때
- omp가 주장별 근거 감사, 대상 모델 프롬프트 작성, 제품 실험 판정 같은 도메인 기능을 기본으로 제공할 때
