# 원격 복구 결과와 재시도

로컬 수정, commit, push, 리뷰 답글, review thread 해결은 서로 다른 결과다. 실제 요청과 기존
승인 범위에서 수행하며 미승인 단계 때문에 가능한 수정·검증을 미완성으로 남기지 않는다.
검토 가능한 diff·답글 초안을 먼저 준비하고 필요한 권한만 마지막에 확인한다.

## Push

쓰기 직전 PR head와 push 대상 저장소·remote ref, 로컬 branch의 ancestry를 확인한다.
다른 사람이 head를 갱신했으면 새 상태를 통합·검증한 뒤 진행한다. fork PR을 base 저장소로
push하거나 강제 push하지 않는다. 결과가 불명확하면 같은 push를 반복하기 전에 정확한 원격
ref와 PR head를 읽는다. 원하는 commit이 반영됐으면 성공으로, 반영 안 됐고 입력이 그대로면
재시도 가능으로, 조회 불가면 `unknown`으로 남긴다.

## 답글과 대화 해결

전송이 승인된 답글만 원래 inline review thread에 게시한다. 현재 API 도움말·schema를 확인하고
thread ID와 소속 PR을 재검증한다. GitHub GraphQL의 `addPullRequestReviewThreadReply`와
`resolveReviewThread` 같은 지원 operation을 사용할 수 있다. 다중 행 본문은 JSON serializer나
body file로 전달하고 shell 문자열 보간으로 만들지 않는다.

- 수정한 의견: 수정이 PR 원격 head에 반영되고 관련 검증이 연결됐을 때만 해결할 수 있다.
  필수 원격 CI가 pending·실패·미확인이면 검증 완료로 보고하거나 해당 의존 대화를 해결하지 않는다.
- 기각한 의견: 설명 답글이 같은 대화에 실제 게시된 것을 확인한 뒤 해결한다.
- 불확실·차단·미처리 의견: 해결하지 않는다. 이미 같은 문제가 원격에서 해결됐다면 현재 근거로 no-op을 확인한다.

답글 응답이 timeout이면 전송 전 기록한 본문·작성자·대상과 전송 후 댓글을 페이지별로 대조해
중복 여부를 확인한다. 부재가 확인되지 않으면 재전송하지 않는다. 대화 해결 응답이 불명확하면
`isResolved`를 다시 읽는다. API 성공 응답만으로 readback 완료를 주장하지 않는다.

최종 PR head·check·대화 상태를 한 번 다시 조회해 실제 반영을 보고한다. CI가 진행 중이면
그 상태로 전달하고 지속 감시를 자동 시작하지 않는다. local validation, remote CI, reply,
resolution 각각 `applied / unapplied / unknown / no-op` 또는 실제 검사 상태와 근거를 남긴다.
