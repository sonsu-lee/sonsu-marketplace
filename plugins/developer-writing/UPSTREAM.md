# Developer Writing provenance

`write-developer-blog`, `article-shapes.md`와 `technical-evidence.md`는 이 저장소에서 독자적으로
작성했다. 외부 문구, 코드, template과 예제를 배포물에 복사하지 않았다.

## Consulted only

- [`kdy1/kdy1-scripts@92a8fbe9a57bce5064ed7dba3a8f87f331930dc6`](https://github.com/kdy1/kdy1-scripts/tree/92a8fbe9a57bce5064ed7dba3a8f87f331930dc6):
  standalone `write-blog-post`의 좁고 명시적인 호출 구조와 사용자 자료/미확인 질문 분리를
  관찰했다. 확인한 snapshot에는 root license가 없어 원문 문구, 코드와 template을 포함하지 않았다.
- Julia Evans, “Blog about what you've struggled with”와 “Writing great examples”: 독자의 구체적인
  막힘과 실제 코드에서 무관한 부분을 덜어 내는 방법을 참고했다.
- Simon Willison, “AI writing policy”: AI가 저자의 1인칭 의견과 이유를 만들지 않는 경계를
  참고했다.
- SSGOI 공개 저장소와 release 기록, Josh Comeau의 blog implementation 글: 구현 조건·재현·검증과
  interactive example이 설명을 보강하는 공개 사례로만 관찰했다.

이 자료는 고정 제목 수, 단계 수, SEO 지표나 생산성 효과의 근거가 아니다. 네 가지 mode, 흐름
의사코드와 evidence 상태는 현재 package 계약이다.
