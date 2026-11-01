# 리뷰 렌즈

> 영문 정본: [review-lenses.md](review-lenses.md) (`869d0cd` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

집중 질문을 고르거나 바뀐 동작을 분석할 때 읽는다. 이들은 서로 보완하는 렌즈일
뿐, 필수 작업 네 가지나 모든 작업자가 반복할 체크리스트가 아니다. 변경의 목적에서
시작해, 입력이나 생산자에서 변환과 상태 변경을 거쳐 소비자와 부수 효과까지,
관련된 호출자를 diff 밖까지 따라간다. 테스트는 의도한 동작을 보여 줄 뿐 실행의
증거가 아니다.

- **흐름:** 영향받는 종단 간 경로가 요구 사항을 충족하면서, 소비자가 여전히
  필요로 하는 데이터와 동작을 보존하는가? 바뀐 경로가 닿는 곳의 생산자/소비자
  계약, 호환성, 영속성, 권한 부여, 외부 데이터를 추적한다. 관련이 있으면
  식별자와 타임스탬프를 실제 소비자와 그 의미상 목적에 비추어 확인하고, 표준의
  요구 사항과 프로젝트의 선택을 구분한다. 집중 작업자가 이어야 할 진입점과
  관찰 가능한 결과를 밝힌다.
- **실패와 상태:** 도달 가능한 오류, 경계 입력, 순서, 경쟁 상태, 취소, 재시도가
  불변식을 깨뜨릴 수 있는가? 오류 전파, 리소스 소유권, 정리, 부분 상태, 잠금을
  살피며, 관련이 있으면 암묵적인 유일성 대기도 포함한다. 실제 호출자와 트랜잭션
  수명을 추적한다. 실제 실행 경로와 호출자가 없는 가설적인 조합을 구분한다.
- **아키텍처와 현재 비용:** 책임이 이 계층에 속하며 현재의 추상화를 재사용하는가?
  구체적인 결합, 중복된 정책, 현재의 변경 비용을 규명한다. 변경이 추가한
  추측성 코드, 곧 요청하지 않은 옵션, 한 번만 쓰는 추상화, 래퍼, 어떤 호출자나
  입력도 도달하지 않는 폴백 경로나 가드에 이의를 제기한다. diff만이 아니라
  호출자와 입력으로 도달 불가능함을 보이고, 취향이나 상상한 규모를 위한
  마이그레이션이 아니라 삭제나 인라인화를 제안한다. 신뢰 경계 검증, 데이터 손실
  방지, 보안 점검, 접근성 장치는 제거해도 되는 단순화가 아니며, 리뷰 대상
  변경을 증명하는 테스트도 마찬가지다.
- **구현:** 데이터 구조, 할당/복사/계산 비용, API, 타입, 가드, 주석, 테스트
  단언을 살핀다. 대체안을 제안하기 전에 지원되는 API 버전, 반환값, 생명주기,
  오류를 확인한다. 타입은 외부 데이터를 검증하지 않는다. 모든 진입 경로와
  변경에서 불변식이 유지될 때만 실제 경계에서 한 번 검증하고, 가변 상태나 우회
  호출자에는 가드를 유지한다. 주석은 문법이 아니라 의도나 제약을 설명한다. 목적이나
  순서가 분명하지 않을 때는 번호를 붙인 단계가 도움이 된다. 바뀐 공개 동작을
  문서와 비교한다. 정상 경로와 도달 가능한 중요한 경계나 경쟁 상태에 대해 가장
  작은 유용한 수준의 테스트를 요청하고, 각각이 잡아낼 법한 버그를 밝힌다. 동시성
  테스트는 결정적 조율, 리소스 격리, 타임아웃 예산, 실패 시 정리를 확인한다.
  커버리지 비율은 기준이 아니다. 배선만 되풀이하는 테스트, 목(mock)을 그대로
  돌려주는 테스트, 동작을 보존하는 리팩터링이 바꿀 구현 세부 사항을 단언하는
  테스트는 약하다. 바뀐 동작에 대해 잘못된 확신을 주거나 실제 유지보수 비용을
  더할 때만 보고하고, 변경을 증명하는 테스트를 지우라고 하지 말고 더 강한
  단언을 요청한다.

지적의 기준, 작업자의 경계, 검증, 보고는 공통 스킬이 정한다. 이 렌즈들은
리뷰어에게 런타임 실행 권한을 주지 않는다.

## 출처

- [Google review criteria][criteria]: 설계, 기능, 복잡성, 테스트, 주석, 주변
  컨텍스트.
- [Google review standard][standard]: 완벽을 요구하거나 증거 대신 개인의 취향을
  내세우지 않고 코드 건강을 개선한다.
- [Compound Engineering `ce-simplify-code`][simplify]와 그
  [test-value reviewer][test-value] (MIT): 안전 점검과 증명 테스트의
  보호 장치, 테스트 가치 질문을 베끼지 않고 각색했다.
- [Test Behavior, Not Implementation][behavior] (Google Testing Blog,
  2013): 테스트는 공개 동작을 검증해야 하며 구현이 바뀌어도 살아남아야 한다.
- [Code Coverage Best Practices][coverage] (Google Testing Blog, 2020):
  커버리지는 손실이 큰 지표다. 무엇이 테스트되지 않았는지와 테스트 품질을
  판단한다.

[criteria]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[standard]: https://google.github.io/eng-practices/review/reviewer/standard.html
[simplify]: https://github.com/EveryInc/compound-engineering-plugin/blob/786ac0194183fadc3d0e2525b2ba6d40353926d3/skills/ce-simplify-code/SKILL.md
[test-value]: https://github.com/EveryInc/compound-engineering-plugin/blob/786ac0194183fadc3d0e2525b2ba6d40353926d3/skills/ce-simplify-code/references/personas/test-value-reviewer.md
[behavior]: https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html
[coverage]: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
