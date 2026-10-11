# 리뷰 실행

`review-code`의 PR 외 리뷰와 집중 관점 리뷰가 쓰는 고정 입력·독립 실행·결과 수집 절차다.
PR 대상은 [PR 리뷰 실행과 게시](pr-review-execution.md)를 따른다. 의미 판단은
[공통 리뷰 기준](review-criteria.md)을 따른다. 위임된 리뷰어는 지정 입력을 직접 검토하고 추가
리뷰어를 만들지 않는다. root만 할당한다.

## 입력과 실행

일반 리뷰·최초 전체 변경 리뷰의 기본은 **현재 호스트 프로필의 새 문맥 5개**다. 동일 고정 산출물과
동일 기준을 제공하며 강제로 다른 관점을 나누지 않는다. 사용자 명시 설정·인원은 우선한다.
특정 관점 리뷰와 국소 수정 재검토는 같은 호스트 프로필의 새 문맥 1개가 기본이다.

작은 코드는 전체 내용과 계약을 고정 inline 입력으로 전달한다. 큰 변경은 현재 설치 위치에서
플러그인 루트의 `scripts/review-package` 경로를 확인하고 대상 Git 저장소에서 다음 중 하나를 실행한다.

```bash
"$REVIEW_SCRIPTS/review-package" range "$BASE_SHA" "$HEAD_SHA"
"$REVIEW_SCRIPTS/review-package" working-tree
```

미커밋 패키지는 staged·tracked·untracked 변경을 포함한다. 기준은 작업 시작점/확인한 merge
base이며 여러 커밋을 임의로 HEAD~1로 줄이지 않는다. 파일·검증 보고를 snapshot하는 동안
관리되는 writer를 멈추고 패키지 digest를 확인한다.

[code-reviewer.md](review/code-reviewer.md)에 고정 내용·계약·사실인 명령 결과·제약과 공통 기준을
채운다. 이전 대화, 구현자의 자기 정당화, 다른 최초 리뷰어의 지적을 넘기지 않는다. 실행
설정은 Codex의 [모델 프로필](model-profiles.md), Claude Code의 [모델 프로필](claude-model-profiles.md) 또는
omp의 [모델 프로필](omp-model-profiles.md)과 현재 native 스키마를 따른다.
Claude Code에서는 해당 역할의 `review:<role>` subagent를 선택해 프로필의 model과
frontmatter effort를 적용한다. `inherit`는 effort 설정을 생략한다.
요청/관측 설정, 별개 run ID·완료 이벤트와 원결과를 보존한다. 같은 보고서 복사본은 독립 실행이 아니다.

임시 쓰기가 허용되면 고정 자료를 만들고 모든 쓰기가 금지됐다면 inline 고정 입력을 사용한다.
독립 실행 기능 자체가 없으면 `blocked`/`not_run`을 보고하고 보조 정적 관찰과 구분한다.

## omp 실행

omp 패키지에는 역할 agent가 없다. omp에서는 `task` 도구의 순정 `reviewer` agent에 같은 고정 입력을
주고, 인원은 프로필의 기본값을 따른다. `general_review`·`focused_review`·`adjudication` 같은 역할
이름은 사용자가 그 agent를 직접 등록했을 때만 쓴다. 실제 모델은 관측값으로 기록한다.

순정 `reviewer`에는 이 플러그인의 omp 규칙 `sonsu-review-standard`가 자동으로 붙는다. root는
`findings[]`를 `<body의 라벨> <file_path>:<line_start> — <title>. <body의 나머지>` 형식으로 옮기고,
`summary.explanation` 첫 줄의 판정을 그대로 쓴다. 판정 줄이 없거나 라벨이 없는 `P2`·`P3` 지적이
있으면, root가 다음 대응(`P0`·`P1` → 라벨 없음, `P2` → `Optional:`, `P3` → `Nit:`)과 판정 규칙(필수
지적이 있으면 `Request changes`, 다른 지적만 있으면 `Approve with comments`, 지적이 없으면 `Approve`)으로
보정하고, 보정했다는 사실을 결과에 적는다.

## 집중 리뷰 진입

한 관점만 요청한 경우 root는 그 범위·관련 계약·공통 기준을 고정하고 `focused_review` 프로필의
새 문맥 1개에 위임한다. 사용자 지정은 우선하며 현재 root 모델은 바꾸지 않는다.
위임문에는 사용자가 지정한 대상과 관점을 그대로 유지한다. 관점 스킬의 일반 항목으로 요청을
넓히지 않는다. 주변 파일은 지정 대상의 판단 근거로만 읽고, 무관한 영역의 결함을 현재 리뷰의
finding이나 차단 조건에 포함하지 않는다. 위임된 검토자는 직접 검토하고 재위임하지 않는다.
root는 아래 수집·판정·보고 순서를 마친다. 일반 5인 리뷰를 추가하지 않는다.

## 수집·판정·재검토

root의 순서는 **위임 → 모든 원결과 수집 → 지적 검증 → 최종 보고**다. 생성 성공이나
`pending_init`은 결과 수집이 아니다. 생성된 ID로 native wait/resume를 이어가며 같은 ID의
완료 상태와 비어 있지 않은 원결과가 모두 도착할 때까지 수집 단계에 머문다. 자체 분석에서
지적이 없어도 이 단계를 생략하지 않는다. 결과를 받을 수 없으면 미완료 상태와 이유를 보고하며,
자체 판단을 독립 리뷰의 최종 판정으로 대신하지 않는다.

모든 원결과를 받은 뒤 root가 원인별 중복을 합치고 각 지적의 요청 범위·계약·도달 경로·
재현/정적 근거를 검증한다. 그 후 검증한 지적과 한계를 최종 보고한다. 원결과와 조정자의
판정은 구분한다. 다수결·발견 수·문장 길이로 통과시키지 않고, 유효한 지적은 1명만 발견해도
처리한다. 별도 상위 모델 전수 리뷰는 기본 단계가 아니며 명명된 미해결 판단만 현재 호스트의
`adjudication` 또는 복잡한 경계의 `complex_adjudication` 프로필 모델에 보낸다.

리뷰 요청만으로 수정을 승인받은 것은 아니므로 리뷰 전용 작업은 검증한 지적과 한계를 전달하고 끝낸다.
