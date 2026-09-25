# 독립 리뷰 실행

이 참고 자료는 공개 `review` 스킬과 집중 관점 리뷰가 사용하는 고정 입력, 독립 실행과
결과 수집 절차다. 의미적 판단은
[공통 리뷰 기준](review-criteria.md)을 따른다. 위임된 리뷰어는 지정 입력을
직접 검토하고 추가 리뷰어를 만들지 않는다. root만 할당한다.

명시적인 GitHub PR 심층·다중 리뷰는 `review-pr`가 맡는다. 일반 코드 리뷰와 개발
절차에서 선언한 독립 리뷰에는 아래 계약을 적용한다.

독립 실행을 준비할 때 [실행과 문맥 계약](agent-execution.md)을
읽고 생성 응답·대기·완료 근거를 연결한다.

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
관리되는 writer를 멈추고 패키지 digest를 확인한다. 개발 gate의 workspace snapshot은 단순
diff 패키지와 별개로 주변 소스·설정·의존성의 최신성을 다룬다.

[code-reviewer.md](review/code-reviewer.md)에 고정 내용·계약·사실인 명령 결과·제약과 공통 기준을
채운다. 이전 대화, 구현자의 자기 정당화, 다른 최초 리뷰어의 지적을 넘기지 않는다. 실행
설정은 Codex의 [모델 프로필](model-profiles.md) 또는
Claude Code의 [모델 프로필](claude-model-profiles.md)과 현재 native 스키마를 따른다.
Claude Code에서는 해당 역할의 `engineering:<role>` subagent를 선택해 프로필의 model과
frontmatter effort를 적용한다. `inherit`는 effort 설정을 생략한다.
요청/관측 설정, 별개 run ID·완료 이벤트와 원결과를 보존한다. 같은 보고서 복사본은 독립 실행이 아니다.

리뷰 전용 요청에는 전체 개발 DAG 등록·소스 수정·commit을 요구하지 않는다. 임시 쓰기가
허용되면 고정 자료를 만들고 모든 쓰기가 금지됐다면 inline 고정 입력을 사용한다. 독립 실행
기능 자체가 없으면 `blocked`/`not_run`을 보고하고 보조 정적 관찰과 구분한다. 자체 리뷰로
필수 독립 리뷰를 대신하지 않는다.

## 집중 리뷰 진입

한 관점만 요청한 경우 root는 그 범위·관련 계약·공통 기준을 고정하고 `focused_review` 프로필의
새 문맥 1개에 위임한다. 사용자 지정은 우선하며 현재 root 모델은 바꾸지 않는다.
위임문에는 사용자가 지정한 대상과 관점을 그대로 유지한다. 관점 스킬의 일반 항목으로 요청을
넓히지 않는다. 주변 파일은 지정 대상의 판단 근거로만 읽고, 무관한 영역의 결함을 현재 리뷰의
finding이나 차단 조건에 포함하지 않는다. 위임된 검토자는 직접 검토하고 재위임하지 않는다.
root는 아래 수집·판정·보고 순서를 마친다. 일반 5인 리뷰나 개발 DAG를 추가하지 않는다.

## 수집·판정·재검토

root의 순서는 **위임 → 모든 원결과 수집 → 지적 검증 → 최종 보고**다. 생성 성공이나
`pending_init`은 결과 수집이 아니다. 생성된 ID로 native wait/resume를 이어가며 같은 ID의
완료 상태와 비어 있지 않은 원결과가 모두 도착할 때까지 수집 단계에 머문다. 자체 분석에서
지적이 없어도 이 단계를 생략하지 않는다. 결과를 받을 수 없으면 미완료 상태와 이유를 보고하며,
자체 판단을 독립 리뷰의 최종 판정으로 대신하지 않는다.

모든 원결과를 받은 뒤 root가 원인별 중복을 합치고 각 지적의 요청 범위·계약·도달 경로·
재현/정적 근거를 검증한다. 그 후 검증한 지적과 한계를 최종 보고한다. 원결과와 조정자의
판정은 구분한다. 다수결·발견 수·문장 길이로 통과시키지 않고, 유효한 지적은 1명만 발견해도
처리한다. 별도 Sol 전수 리뷰는 기본 단계가 아니며 명명된 미해결 판단만 Sol high 또는 복잡한
경계의 현재 호스트 `complex_adjudication` 프로필 모델에 보낸다.

[품질 게이트](quality-gates.md)에 따라 5개 리뷰를 한
라운드로 센다. 국소 수정은 이전 전체 근거·차이·영향 범위·새 검사와 집중 검토자 1개를 연결한다.
계약·설계·의존 경계 변경이나 영향 불명확성은 전체 5개를 다시 연다. 리뷰 요청만으로 수정을
승인받은 것은 아니므로 리뷰 전용 작업은 검증한 지적과 한계를 전달하고 끝낸다.

## 고위험 red-team

`red-team` 정책은 일반 리뷰 뒤 별도 새 문맥의 현재 호스트 `red_team` 프로필 모델이 검토한다. 직전에 전체 변경,
원래 목표, 요구사항/설계, 계획/대응 관계, 검사 결과, 관찰/제약, 지적/수정 이력을 고정한다.

```bash
"$REVIEW_SCRIPTS/red-team-package"   "$WHOLE_CHANGE_PACKAGE" "$ORIGINAL_GOAL_FILE" "$REQUIREMENTS_FILE"   "$PLAN_AND_MAPPING_FILE" "$VERIFICATION_REPORT" "$OUTCOMES_FILE"   "$PROVENANCE_FILE" "$RED_TEAM_BUNDLE"
```

[red-team-reviewer.md](review/red-team-reviewer.md)와 묶음·digest를 전달한다. 묶음 밖 가변 자료로
필수 근거 공백을 채우지 않는다. `survives_challenge`만 통과이며 `invalidated`는 반증된 단계,
`inconclusive`는 검증 공백, `blocked`는 실행 환경에 반환한다. 사람의 명시적 `accepted_risk`는
별도 결과다. 수정 후에는 현재 전체 묶음을 다시 고정하고 변경 영향에 맞게 재검토한다.
