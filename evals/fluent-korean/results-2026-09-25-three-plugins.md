# Fluent Korean 독립 플러그인 평가 — 2026-09-25

`fluent-korean` `0.1.0-beta.1`의 당시 모델 평가 스킬 본문 SHA-256은
`d7abb0fe1fd1fdc1e6f2351411cec452d238b10e35d564c27311e7a655ba80d8`이다.
[공통 실행 조건](../fluent-multilingual/results-2026-09-25-three-plugins.md)에 따라 새 문맥에서
스킬 본문을 직접 제공했다.

- 기존 한국어 본문 사례 28건과 새 작성·진단·윤문 집중 사례 3건: 정상 종료 31건.
- 기존 사례의 보호 문자열 65개, 제목 10개, 순서 marker 22개, 지정 횟수 15개, 코드 블록 3개와 유지 사례를 대조했다. 현재 후보의 위반은 0건이다. 집중 사례의 보호 문자열도 통과했다.
- `A01-generation-brief`, `F01-unknown-actor`는 초기 출력에서 날짜·시간 표기를 바꿨다. 보존 규칙을 수정한 후 두 사례를 재실행해 정확한 표기를 확인했다.
- 출력과 입력의 사실·조건·불확실성·편집 범위를 작성자가 대조했고 명확한 의미 위반은 발견하지 못했다. 원어민 선호 평가가 아니다.

이번 ID·적용 범위 변경 뒤 격리된 native 로더에서 `fluent-korean:fluent-korean`의 단독·동시 설치와 공개 스킬 발견은 `observed`다. 이 패키지에는 hook이 없다.
변경 후 본문의 모델 출력, native 자동 선택, Writing·Workflow 결합 출력과 원어민
품질 평가는 `not_run`이다. 원본 출력과 trace는 이 호스트의
`/tmp/fluent-legacy-cases-e423/korean/` 및 `/tmp/fluent-eval-e423/ko-*/`에 있다.
