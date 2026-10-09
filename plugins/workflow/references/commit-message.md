# 커밋 메시지 기준

`commit`과 `review-commit`이 함께 쓰는 커밋 메시지 규칙이다. 메시지를 만들거나 제안된 메시지를 검토할 때 적용한다.

## 언어를 정한다

다음 순서로 처음 근거가 있는 단계의 언어를 쓴다.

1. 사용자 지정
2. 저장소가 명시한 규칙: `CONTRIBUTING*`, `commitlint.config.*`·`.commitlintrc*`, `AGENTS.md`·`CLAUDE.md`, `.github/` 안내
3. 영어

과거 커밋의 언어는 근거로 쓰지 않는다. 대화 언어도 근거가 아니다.

## 제목

- 저장소 규칙이 없으면 `<type>(<scope>): <summary>` 형식을 쓴다. `type`은 `feat|fix|docs|refactor|test|chore|perf|build|ci` 중 하나이고 `scope`는 선택이다.
- 영어 summary는 명령형으로 쓴다. 콜론 뒤 첫 글자는 소문자로 쓰고, 끝에 마침표를 붙이지 않으며, 헤더 전체는 72자 이하로 한다.
- 결정된 언어가 한국어면 명사형으로 끝내고(`… 추가`), 일본어면 체언으로 끝낸다.
- "update files"처럼 행위만 쓰지 않고 무엇이 달라지는지 쓴다.

## 본문

제목과 diff만으로 이유가 분명하면 본문을 생략한다. 다음 중 하나라도 해당하면 본문을 쓴다.

- 자명하지 않은 결정
- 버그의 원인
- 버린 대안
- 호환성·마이그레이션 영향

순서는 지금 코드의 문제(현재형) → 이 방식을 택한 이유 → 버린 대안 → 부작용이다. 72자에서 줄을 바꾼다.

파일 목록, diff를 문장으로 옮긴 설명, 테스트 개수, 작업 경위는 쓰지 않는다.

## footer

- `BREAKING CHANGE:`는 실제로 호환성이 깨질 때만 쓴다.
- 티켓 ID나 URL은 사용자 요청 또는 저장소 관례가 있을 때만 subject나 footer에 포함한다. commit message를 tracker 연결의 기본 채널로 사용하거나 티켓 ID를 만들지 않는다.

## AI 사용 표기

- `Assisted-by:`, AI용 `Co-authored-by`, 생성 도구 서명은 자동으로 넣지 않는다. 실제로 AI를 사용했다는 사실만으로 표기를 추가하지 않으며 `<AI tool name>` 같은 자리표시자도 출력하지 않는다.
- 사용자가 AI 표기를 제외하라고 요청하면 그 의사를 따른다. 저장소가 표기를 필수로 요구하면 충돌을 메시지 밖에서 알리되 임의로 trailer를 붙이거나 정책을 충족했다고 보고하지 않는다.
- 사용자가 표기를 명시적으로 요청한 경우에만 확인된 도구명과 요청 형식으로 작성한다. 필요한 값이 없으면 값을 만들거나 자리표시자를 넣지 않고 메시지 밖에서 필요한 정보를 알린다.
- `Signed-off-by`는 사용자를 대신해 붙이지 않는다.
- 실행 환경 설정이 trailer를 자동으로 덧붙이면 그 설정 위치를 결과 보고에서 알린다.

## squash 병합 저장소

`git log --first-parent -20 origin/<default>`로 본 제목 대부분이 `(#<number>)`로 끝나면 squash 병합 저장소로 본다. 이런 저장소에서는 PR 제목이 기본 커밋 제목이 되므로 PR 제목에도 위 제목 규칙을 적용한다.

## 예시

다음은 이 저장소의 기준을 설명하려고 만든 로컬 예시다.

좋은 예:

```text
fix(hooks): keep timeout cleanup within host budget

The capture hook spends its whole budget on the main step, so the
cleanup step is cut off when the host kills the process at the limit.

Reserve a fixed slice of the budget for cleanup before starting the
main step. Raising the hook timeout was not an option because the
host caps it for this event.
```

나쁜 예:

```text
update hook files
```

무엇이 달라지는지 알 수 없고, 형식과 이유가 모두 빠졌다.
