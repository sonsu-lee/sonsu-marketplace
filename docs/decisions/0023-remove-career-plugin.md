# ADR 0023: Career 플러그인 제거

- 날짜: 2026-10-09
- 상태: 채택
- 관련 결정: [ADR 0020](0020-add-career-plugin.md)

## 맥락

이 마켓플레이스는 개발 작업에 쓰는 도구를 제공한다. Career의 경력 원본 정리, 지원 서류 작성과
면접 준비는 이 범위와 맞지 않으므로 별도 플러그인으로 분리한다.

## 결정

- Career 플러그인과 전용 평가 자료를 저장소에서 제거한다. 카탈로그, 현재 상태 문서, 라우팅 사례와
  리팩터링 인벤토리에서도 관련 항목을 제거한다.
- Career는 추후 별도 저장소의 플러그인으로 만든다. 이 마켓플레이스에는 배포하지 않는다.
- omp 기본 구성은 Workflow, Fluent Korean, Fluent English, Fluent Japanese, Design 5개로 둔다.
  Worklog와 Design Patterns는 opt-in으로 유지한다.

## 결과

Codex·Claude Code 카탈로그는 플러그인 13개를 제공한다. omp 카탈로그는 기본 5개와 opt-in 2개를
제공한다. Career의 기존 구현과 결정 경위는 Git 기록과 ADR 0020에서 확인한다.
