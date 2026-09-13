# 관리형 근거 게이트 v2

`plugins/engineering/scripts/evidence-gates.py`는 등록한 단계/작업의 현재 근거를 검사한다.
Python 표준 라이브러리·Git·POSIX를 사용하며 모델 실행·의미 판정은 하지 않는다. native
세션 도구는 그대로 사용한다. `Stop` hook은 현재 누락을 알리는 읽기 전용 observer다.

현재 설치 경로에서 helper의 절대 경로를 확인한다. 대상 저장소 root에서 명령을 실행한다.
`--help`가 현재 소비 계약이며 예제 ID·경로는 실제 작업에 맞춘다.

등록은 Git의 `info/exclude`에 `/.engineering/gates/` 규칙이 없을 때만 추가한다. 이미 있으면
읽기만 한다. `.git` 쓰기를 제한하는 sandbox는 실행 환경 준비 단계에서 해당 규칙을 설정한다.
규칙이 없고 추가 권한도 없으면 등록을 차단하며, 제외 설정 실패를 게이트 통과로 처리하지 않는다.
별도 workspace를 잠글 때에도 해당 Git 저장소의 제외 규칙을 먼저 확인·설정한다.

## 등록

```json
{
  "schema_version": 2,
  "contracts": ["contract.md"],
  "units": [
    {
      "id": "design",
      "stage": "design",
      "needs": [],
      "artifact": {"kind": "documents", "paths": ["design.md"]},
      "checks": [{"id": "links", "argv": ["python3", "check_links.py", "design.md"]}],
      "review": "checks"
    },
    {
      "id": "implement",
      "stage": "implementation",
      "needs": ["design"],
      "artifact": {"kind": "workspace", "path": "/absolute/isolated/worktree"},
      "checks": [{"id": "tests", "argv": ["python3", "-m", "unittest", "discover"]}],
      "review": "independent"
    }
  ]
}
```

`init --task-id <stable-id> --session-id <native-session>`의 stdin에 전달한다. 새 작업은 v2를
명시한다. `stage`는 design/plan/implementation/integration, 정책은 checks/independent/red-team이다.
`checks` 정책에는 검사가 하나 이상 필요하다. `independent`·`red-team`에서 적용할 명령이
없으면 `checks:[]`와 `checks_reason`을 기록할 수 있으며 필수 리뷰는 그대로 수행한다.
누락 ID·cycle은 거부한다. 계약은 controller root 상대 파일이다. 문서 산출물은 고정 파일
패키지로, 구현/통합은 실제 Git workspace 전체로 식별한다. workspace는 tracked + untracked nonignored 소스 전체와 존재하는 root manifest/lockfile을
포함한다. ignored probe 파일이 필요하면 artifact.inputs에 명시한다. node_modules/cache/build를
실행 환경 이미지로 보존하는 것은 아니므로 필요한 환경 검사는 별도로 선언한다. source symlink와
submodule은 현재 지원하지 않는다. 직접 구현은 controller root를 쓸 수 있다. 같은 DAG의 source
unit은 workspace를 분리하고 한 checkout의 순차 소스 변경은 하나의 unit으로 묶는다.

역할 기본값은 패키지의 `references/model-profiles.json`에서 읽는다. 사용자 명시 override가
있으면 unit의 `review_profiles`에 `source`와 해당 general_review/focused_review/red_team의
`{model,effort,count}`를 기록한다. source는 실제 지시 근거이며 설정을 임의로 완화하는 수단이 아니다.

설정을 보완할 때에는 같은 unit ID를 유지한 `revise` stdin에 전체 설정과
`revision:{reason:"변경 이유",source:"기존 승인·현재 지시 근거"}`를 넣는다. 기존 check ID·소비 예산,
계약·의존·산출물 범위를 줄이거나 review 정책을 낮출 수 없다. 잘못된 argv/oracle 수정은 이유와
근거를 기록하고 다시 검사한다. 명령의 의미적 동등성과 실제 지시 권한은 root가 확인한다.
프로필 변경은 기존 역할 override를 명시적으로 대체하고 같은 revision.source에 연결한다.
이는 새 승인 대화를 요구하는 절차가 아니며, 위험 수용은 별도 accepted_risk로 기록한다.

## 실행

1. `ready --task-id <id>`로 진입 가능한 unit과 부족한 근거를 확인한다.
2. `enter --task-id <id> --unit <unit> --request-id <id>`로 선행 근거를 확인하고 작성 소유를 기록한다.
3. 구현한 뒤 `run --task-id <id> --unit <unit> --check <check>`로 선언한 argv를 실행한다.
   셸 문자열을 해석하지 않는다. 실행 전후 snapshot이 다르면 현재 통과 근거로 사용하지 않는다.
4. 필수 리뷰를 아래 절차로 준비·수집·판정한다.
5. `complete-unit --task-id <id> --unit <unit> --request-id <id>`로 현재 조건을 다시 검사한다.
6. 모든 unit의 현재 조건이 충족되면 `close --task-id <id>`로 종료한다.

같은 request ID·같은 payload는 원 receipt를 돌려주고 다른 payload는 거부한다. 원 receipt의
성공은 현재 유효성을 뜻하지 않는다. 계약·정책·산출물·선행 receipt가 달라지면 `status`의
유효 상태가 만료된다. 이전 근거·요청은 이력으로 남고 선행 변경의 소비자도 다시 검증해야 한다.

관리되는 writer는 같은 workspace에서 하나만 실행한다. 리뷰 준비 중에는 writer를 멈춘다.
완료·포기는 writer 잠금 아래 owner 해제와 receipt를 먼저 저장하고 lease를 삭제한다.
저장 전에 중단되면 기존 소유권을 유지한다. 저장 뒤 lease 삭제 전에 중단되면 같은 완료 요청을
재시도하거나 `abandon --unit`으로 남은 lease를 정리한다. 새 소유자의 lease는 삭제하지 않는다.

`abandon --unit`은 사용 가능한 관리 상태를 해제하는 명시적 복구 동작이다. 중단된 pending
검사는 invocation lease와 등록된 process group이 모두 종료된 경우에만 기존 attempt·부분 로그를
보존하고 incomplete/inconclusive로 복구한다. 살아 있는 실행은 해제하지 않는다. 관리되는 검사와
자식은 해당 group에 남거나 전달된 lease를 유지해야 한다. 둘 다 버리는 의도적인 daemon은
이 실행 계약의 대상이 아니며 별도 서비스 검증을 사용한다. 외부 편집이나
중간에 바뀌었다가 되돌린 파일까지 완전히 차단·감지하는 파일시스템 보안 장치는 아니다.
직접 자식이 종료돼도 lease 보유자나 등록된 group의 종료를 확인하지 못하면 검사 결과를
`pending`·`incomplete`로 남기고 `run`은 비정상 종료한다. unit 완료와 소유권 해제를 막으며,
실행이 모두 끝난 뒤 `abandon`으로 `inconclusive` 복구한다. 실행 중인 unit의 집계 상태도
`pending`으로 표시한다.

## 리뷰 라운드

`prepare-review --unit <unit> --gate final-review --package <brief.md>`가 현재 고정 입력과
요청 reviewer 구성을 만든다. 별개 새 문맥의 리뷰어 각각에 동일 패키지·기준을 전달한다.
입력 brief는 읽을 수 있는 고정 설명 파일이다. CLI는 전체 snapshot tar와 brief를 별도로 보존하고
`files`에 경로를 반환한다. CLI가 reviewer를 생성하거나 모델 관측값을 만들어내지는 않는다.

`record-review --unit <unit> --gate final-review --attempt <N> --reviewer-id <id> --report <path>`의
stdin은 다음 원결과다. `run_id`는 실제 별개 실행을 식별한다.

```json
{
  "run_id": "native-run-identity",
  "execution": "complete",
  "verdict": "failed",
  "findings": [{"id": "f1", "title": "문제", "location": "src.ts:12", "evidence": "도달 경로/재현", "impact": "계약 위반"}],
  "observed": {"model": "unknown", "effort": "unknown"}
}
```

원결과를 보존한 뒤 root가 `adjudicate --unit <unit> --gate final-review --attempt <N>`의 stdin에
모든 지적의 결정을 넣는다. `finding`은 reviewer-id:finding-id이고 decision은 valid/dismissed/duplicate다.
각각 reason/evidence를 쓰며 duplicate는 duplicate_of를, valid는 blocking true/false를 명시한다.
유효한 비차단 개선을 필수 수정으로 승격하지 않는다. 실제 유효 필수 지적이 남으면
통과하지 않는다. schema 통과가 판정 근거의 진실성을 증명하지는 않는다.

5명의 일반 리뷰는 1라운드다. 누락·미완료·서로 다른 실행으로 확인할 수 없는 복사 결과는
통과가 아니다. 국소 수정의 prepare 입력은 `{scope:"focused",prior_round:N,impact_assessment:"..."}`로
이전 전체 근거·제한된 영향·새 근거를 연결한다. 완료·판정된 failed 전체 라운드도 변하지 않은
범위의 근거로 사용할 수 있지만 이전 failed 결과는 보존한다. focused adjudicate의 resolutions에
선택한 전체 라운드부터 이후 판정된 라운드까지 남은 valid+blocking 지적의
finding/reason/evidence를 넣어 현재 산출물의 해결을 확인한다. 패키지는 중간 라운드의 원보고서와
unresolved_prior_findings도 보존한다. 오래된 prior_round 선택으로 후속 지적을 건너뛸 수 없으며
누락된 해결 근거는 통과를 막는다. 계약/의존 변화는 집중 재사용으로 덮지 않는다.
전체 재개방과 집중 검토를 합해 같은 gate 최대 5라운드이며 호출 수는 따로 집계한다.

고위험은 일반 리뷰 뒤 `--gate red-team`으로 별도 Astra high 실행을 등록한다. 내용은 목표·
계약·계획·전체 변경·검사·관찰/제약·반례 이력까지 고정해야 한다. 일반 리뷰 결과를 red-team
실행으로 대신 등록하지 않는다. red-team 원결과는 challenge_verdict를 별도 기록한다.
root의 검증 뒤 challenge 판정도 원결과와 구분해 보존한다.

## 상태와 이관

`passed`, `failed`, `blocked`, `inconclusive`, `not_run`을 구분한다. 사람이 현재 artifact의
위험을 명시 수용했다면 complete 입력에 `{outcome:"accepted_risk",acceptance:{human,source,artifact,reason}}`를
기록한다. 수용은 별도 결과이며 조정자나 budget 소진이 대신할 수 없다. downstream에도
그 수용 이력이 남으며 일반 passed로 숨기지 않는다. aggregate accepted-risk 종료는
`close --outcome accepted_risk`로 명시한다.
이 종료 방식은 모든 unit이 현재 완료되고 그중 `accepted_risk`인 unit이 있을 때만 허용한다.

v1은 역사적 observer 기록으로 보존한다. 기존 v1 통과를 v2 unit 근거로 자동 이관하지 않는다.
새 정책을 적용하려면 새 v2 등록과 현재 근거를 만든다. 도구는 사용자의 실제 승인이나 임의
외부 쓰기의 권한을 부여하지 않는다.
