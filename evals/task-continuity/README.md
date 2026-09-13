# 작업 연속성 평가

이 평가는 저장·복구 helper, 실제 Codex 로더와 모델의 재개 판단을 분리합니다.
형식 정본은 [작업 연속성 계약](../../docs/reference/task-continuity.md)입니다.

## Runtime 회귀 검사

```sh
python3 -B -m unittest discover -s evals/task-continuity -p 'test_*.py' -v
python3 scripts/render-continuity.py --check
```

`test_runtime.py`는 실제 CLI·파일시스템·Git fixture를 사용합니다. session/worktree 격리,
read-only·plan 및 session 부재 시 무쓰기, stale 갱신 거부, 종료·history 보존, 손상·symlink
경계, 원자적 replace 실패, 8개 plugin의 동시 저장·hook, 본문 비주입을 검사합니다.
현재 목록에는 Fluent Languages와 Writing이 각각 포함됩니다. 실제 helper로 두 기록을 만들고,
Writing이 Fluent 기록을 대신 읽거나 이름만 바꾼 다른 plugin identity를 허용하지 않는지 검사합니다.
OS replace 실패를 주입하는 검사 외에는 도구 결과를 mock하지 않습니다. 임시 Git commit은
테스트 fixture 안에서만 만들며 현재 repository의 commit·index는 변경하지 않습니다.

## 행동 시나리오

보관된 `cases.json`과 아래 2026-09-07 관찰은 당시 Fluent Languages를 포함한 구성을 대상으로
합니다. Writing의 새 평가에는 현재 스킬·참조와 기대값을 별도 고정하고 결과도 분리합니다.
과거 Fluent의 스킬 선택·로딩·decision 결과를 Writing의 검증으로 재표기하지 않습니다.

`cases.json`의 `input`만 모델에 제공하고, `expected`와 판정을 암시하는 설명은 evaluator가
보관합니다. 후보에는 해당 플러그인의 전체 task-continuity 스킬을 읽게 하고 다음 행동·순서·쓰기
조건을 반환하게 합니다. baseline은 새 지침 없이 같은 관찰을 제공합니다. 실제 외부 쓰기는 없습니다.

판정은 JSON keyword 일치가 아니라 제안한 행동을 읽어 수행합니다. E는 Task2/reopened와 3/5를
유지하면서 기존 Fast Path를 반드시 disqualify해야 합니다. W와 F는 실제 대상의 조회가 재생성보다
먼저여야 합니다. P와 T는 출처 없는 승인 메모를 권한으로 쓰지 않아야 합니다. R·Q·B는 근거의
현재성·revision·not_run을 구분해야 합니다. D는 누락 원문을 추정하지 않아야 하며 L과 RO는
불필요하거나 금지된 checkpoint 쓰기를 제안하지 않아야 합니다.

이는 모의 관찰에 대한 **모델 decision probe**이며 native 자동 skill selection, 실제 외부
mutation, 실제 컴팩션 이후의 전체 실행을 입증하지 않습니다. 단일 sample의 결과를 일반 성공률로
표현하지 않습니다. baseline에서 이미 맞았던 동작은 새 지침의 개선 효과라고 주장하지 않습니다.

## 실제 Codex 로더

```sh
python3 -B evals/task-continuity/native_probe.py --output /absolute/new-evidence-directory
```

새 evidence 디렉터리만 허용합니다. 각 구성은 별도 CODEX_HOME과 workspace를 사용합니다.
8개 플러그인의 단독 설치와 전체 설치에서 `plugin/read`·`plugin/install`·`skills/list`·`hooks/list`를 실제로
호출하고 namespace를 포함한 스킬 이름, hook event·matcher와 최초 untrusted 상태를 검사합니다.
사용자의 인증·설정을 복사하거나 신뢰 상태를 바꾸지 않습니다. native event와 결과는 해당 evidence
디렉터리에 남깁니다. 기존 user-level standalone skill이 로더에 보일 수 있어 검사는 fixture
플러그인의 정확한 namespace만 대상으로 합니다.

## 실제 컴팩션 연결 인수 절차

이 단계는 사용자 인증과 해당 hook 정의의 신뢰가 준비된 **별도 테스트 작업**에서 실행합니다.
사용자가 `/hooks`로 현재 정의를 신뢰한 뒤 진행하며 trust bypass나 managed-hook 위장으로 대체하지 않습니다.

1. 테스트 작업의 정확한 session ID와 workspace에서 활성 checkpoint를 만듭니다. 실제 외부
   쓰기를 하지 않는 합성 task·artifact를 사용하고 checkpoint 본문에 고유한 테스트 표식을 넣습니다.
2. 수동 `/compact` 또는 실제 `thread/compact/start`를 실행하고 compaction 완료 event를 관찰합니다.
   `{}` 응답은 요청 수락일 뿐 완료 증거가 아닙니다.
3. 다음 모델 요청 전에 `SessionStart(source: compact)`의 hook 실행과 경로 안내가 전달됐는지,
   checkpoint 본문이 developer context에 복제되지 않았는지 native trace로 확인합니다.
4. 모델이 기록·현재 artifact를 읽고 미완료 구간부터 이어가는 실제 read/행동을 확인합니다.
5. 자동 compaction도 별도 관찰합니다. 단순 SessionStart event 주입으로 대신하지 않으며 실제
   auto trigger와 같은 turn의 즉시 continuation을 확인합니다. 유한한 호출·시간 예산 안에 실제
   auto trigger를 관찰하지 못하면 `not_run` 또는 `inconclusive`로 기록하고 무한히 context를 채우지 않습니다.
6. 완료 기록과 기록 없는 session, 같은 session의 resume에서도 각각 무주입/활성 복구를 확인합니다.

각 결과에 runtime 버전, package revision, source와 event, 관찰 자료 위치, `pass`·`fail`·
`not_run`·`inconclusive`를 구분합니다. native hook 실행이 미검증이면 자동 복구의 전체 인수는
완료되지 않은 상태이며 helper·로더 검사 통과로 대체하지 않습니다.

## 이전 구현에서의 관찰 (2026-09-07)

2026-09-07, Codex CLI 0.152.1에서 8개 단독·전체 조합의 스킬과 hook 발견을 확인했습니다.
첫 probe의 상대 CODEX_HOME 경로와 namespace 없는 이름 비교는 evaluator 오류였으며 수정 후
새 evidence 디렉터리에서 다시 실행했습니다. 원 실패 결과도 보존했습니다.

11개 candidate decision probe는 각 예상 행동을 보였으며, baseline 8개 중 E에는 이전 Fast Path를
재평가할 여지가 있었습니다. 후보는 disqualification을 명시했습니다. 나머지 baseline의 올바른
판단은 새 지침의 효과로 귀속하지 않습니다. 단일 sample이며 실제 외부 작업은 실행하지 않았습니다.

실제 수동·자동 compaction 후 hook 실행과 다음 모델 요청 전달은 `not_run`입니다. 격리된 검증
환경은 사용자 인증과 trusted hook을 갖지 않았으며, 사용자 설정을 바꾸거나 우회하지 않았습니다.
