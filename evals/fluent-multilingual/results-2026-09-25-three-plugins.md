# Fluent 3개 플러그인 분리 후 평가

패키지별 결과: [한국어](../fluent-korean/results-2026-09-25-three-plugins.md),
[영어](../fluent-english/results-2026-09-25-three-plugins.md),
[일본어](../fluent-japanese/results-2026-09-25-three-plugins.md).

## 입력과 방법

2026-09-25 현재 `fluent-korean`, `fluent-english`, `fluent-japanese`의 스킬 본문을 각각
`codex exec --ephemeral --ignore-user-config --disable plugins -s read-only`의 새 문맥에 직접
제공했다. 모델은 `gpt-6-sol`, reasoning effort는 `xhigh`였다. 평가 기대값은 모델에 제공하지
않았다. 한국어 28건, 영어 10건, 일본어 10건의 기존 본문 사례와 공통 집중 사례 9건을 실행했다.
영어·일본어의 출력 언어 선택 전용 사례 각 2건은 이 직접 주입 방식으로 평가하지 않았다.

당시 모델 실행에 사용한 스킬 SHA-256 (이번 ID·적용 범위 변경 전):

| 스킬 | SHA-256 |
| --- | --- |
| `fluent-korean` | `d7abb0fe1fd1fdc1e6f2351411cec452d238b10e35d564c27311e7a655ba80d8` |
| `fluent-english` | `2b0f1c6e714966149af35e675644520c429d43fb20e7e0f5990870192510a9fd` |
| `fluent-japanese` | `f823e8e6060e59bb33515c145a1b02c56483250db802f16d66486945d7ab4329` |
| 당시 집중 사례 `cases.json` | `7d6cf3c0d79520b50126d5433aaeb796f20b4fb8b67ad459369acef78bb623c3` |

## 관찰

- 기존 본문 사례 48건과 집중 사례 9건은 모두 정상 종료했다. 현재 후보의 출력에서 기존 사례의 보호 문자열 141개, 필수 제목 20개, 순서 marker 46개, literal 횟수 22개, 금지 문자열 5개, 유지 사례 11개와 코드 블록 5개를 대조했고 위반은 0건이었다. 집중 사례의 보호 문자열도 9건 모두 통과했다.
- 작성자가 출력과 입력을 대조해 사실·행위자·조건·불확실성, 편집 범위, 진단의 무수정 여부를 확인했다. 현재 후보에서 명확한 의미 위반은 발견하지 못했다. 이는 블라인드 또는 원어민 품질 평가가 아니다.
- 초기 한국어 `A01-generation-brief`와 `F01-unknown-actor`는 날짜·시간 표기를 바꿨다. 한국어 스킬에 수치·날짜·시간의 표기 보존을 명시한 뒤 두 사례를 재실행해 정확한 표기를 확인했다.
- 초기 영어 `soft-audit-and-false-positives`는 사용자가 그대로 두라고 지정한 대조 문장의 주어를 바꿨다. 영어 스킬에 산문 전체의 정확한 보존 조건을 추가한 뒤 재실행해 원문을 유지했다.
- 집중 사례 `en-voice-with-protected-terms`의 첫 출력은 근거 없는 찬사를 다른 찬사로 바꿨다. 확인된 변경만 기술하도록 영어 스킬을 수정한 뒤 `We optimized \`cacheKey\`. We have not deployed it.`으로 재실행했다.
- 영어 `project-terms-and-runbook-integrity`는 로그 안의 `release train`을 정확히 보존했지만, 기존 평가 입력은 별도 용어 표기를 추가로 요구했다. 그 추가 요구를 제거했다. 일본어 `runbook-integrity`의 기존 marker 순서는 두 명령을 단일 코드 블록에 모아 제시한 정상 출력과 충돌했다. 조건의 순서만 검사하도록 기대값을 수정했다. 두 사례의 기존 모델 출력은 바꾸지 않았다.

## 설치와 남은 범위

당시 격리된 Codex app-server에서 세 플러그인의 단독·동시 설치와 공개 스킬 발견을
확인했다. ID 변경 뒤에도 `plugin/read`, `plugin/install`, `skills/list`를 다시 실행해
`fluent-korean:fluent-korean`, `fluent-english:fluent-english`, `fluent-japanese:fluent-japanese`가
각각 단독 설치와 동시 설치에서 발견됨을 확인했다. 세 Fluent 패키지에는 hook이 없다.
모델의 native 자동 스킬 선택과 이번 적용 범위 정리 후 본문·갱신 사례의 모델 출력 평가는 `not_run`이다. Writing·Workflow와의 모델 출력 조합,
기존판 대비 동일 조건 비교, 반복 실행 안정성, 한국어·영어·일본어 원어민 선호도 `not_run`이다.

ID 변경 직후 버전은 형식 검증, 상대 경로·생성기 검사, 격리 설치와 한국어 shim·일본어 lint의 실행까지 확인했다. 이번 한국어 적용 범위 정리는 별도로 정적 검증한다.

원본 모델 trace와 출력은 현재 작업 호스트의 `/tmp/fluent-eval-e423/` 및
`/tmp/fluent-legacy-cases-e423/`에, 격리 로더 증거는
`/tmp/fluent-three-plugins-native-e423-current/`에 있다. 이 경로는 저장소 배포물에 포함되지 않는다.
