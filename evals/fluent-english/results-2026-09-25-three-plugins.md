# Fluent English 독립 플러그인 평가 — 2026-09-25

`fluent-english` `0.1.0-beta.1`의 당시 모델 평가 스킬 본문 SHA-256은
`2b0f1c6e714966149af35e675644520c429d43fb20e7e0f5990870192510a9fd`이다.
[공통 실행 조건](../fluent-multilingual/results-2026-09-25-three-plugins.md)에 따라 새 문맥에서
스킬 본문을 직접 제공했다.

- 기존 영어 본문 사례 10건과 새 작성·윤문·진단 집중 사례 3건: 정상 종료 13건. 출력 언어 선택 전용 사례 2건은 직접 주입으로 평가하지 않았다.
- 기존 사례의 보호 문자열 36개, 제목 4개, 순서 marker 10개, 금지 문자열 5개, 코드 블록 1개와 유지 사례를 대조했다. 현재 후보의 위반은 0건이다. 목록 안에서 3칸 들여쓴 `sh` 코드 블록은 명령·fence 내용을 정규화해 검사했다. 집중 사례의 보호 문자열도 통과했다.
- `soft-audit-and-false-positives`의 초기 출력은 그대로 두도록 지정한 문장을 바꿨고, `en-voice-with-protected-terms`의 초기 출력은 근거 없는 찬사를 남겼다. 보존·근거 규칙을 수정한 후 두 사례를 재실행해 해결을 확인했다.
- 출력과 입력의 사실·행위자·조건·불확실성·편집 범위를 작성자가 대조했고 명확한 의미 위반은 발견하지 못했다. 영어 원어민 선호 평가가 아니다.

이번 ID·적용 범위 변경 뒤 격리된 native 로더에서 `fluent-english:fluent-english`의 단독·동시 설치와 공개 스킬 발견은 `observed`다. 이 패키지에는 hook이 없다.
변경 후 본문의 모델 출력, native 자동 선택, Writing·Workflow 결합 출력과 원어민
품질 평가는 `not_run`이다. 원본 출력과 trace는 이 호스트의
`/tmp/fluent-legacy-cases-e423/english/` 및 `/tmp/fluent-eval-e423/en-*/`에 있다.
