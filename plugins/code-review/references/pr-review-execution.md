# PR 리뷰 실행과 게시

`review-pr`이 직접 호출되었을 때만 적용하는 실행 계약이다. 일반 코드 리뷰, PR URL 단독 입력,
상태 조회, 로컬 결과 정리에는 reviewer 생성이나 provider 게시를 추가하지 않는다.

## 권한 경계

명시적인 `review-pr` 호출은 해당 PR에 통합 `COMMENT` review 하나를 게시하는 의도를 포함한다.
호스트 권한과 사용자의 더 좁은 제한은 항상 우선한다. 이 권한은 source 수정, commit, push, merge,
`APPROVE`, `REQUEST_CHANGES`나 다른 PR mutation으로 확장되지 않는다.

## 고정 checkout

정확한 repository, open state, base/head SHA와 merge base를 provider metadata와 fetched object로
교차 확인한다. 사용자의 dirty checkout 밖에서 reviewer별 `git worktree add --detach <path>
<head-sha>` 또는 host가 제공하는 동등한 clean detached checkout을 만든다. 각 HEAD와 초기 clean
상태를 확인하고 동일한 전체 diff와 review brief를 제공한다. worktree는 파일 격리이지 security
sandbox가 아니다.

reviewer는 자신의 checkout에서 읽기·검사만 수행하고 source 수정, 재위임, 게시를 하지 않는다.
정확히 세 reviewer가 현재 host/model/reasoning을 상속한다. 임의 model 대체, 인원 축소와
coordinator 대행은 금지한다.

## 실패와 한 번의 재시도

host가 구조화된 결과로 transient 실행 실패임을 식별한 logical reviewer만 동일 입력·동일 설정으로
한 번 재시도한다. 문자열 추측, 인증·권한·입력 오류, model 미지원, reviewer 결과 검증 실패는
transient로 승격하지 않는다. non-transient 실패 또는 재시도 소진은 현재 PR의 완료 review 게시를
중단한다. 성공한 reviewer와 completed-with-no-findings 결과를 반복하지 않는다.

## 통합 COMMENT의 idempotency

coordinator는 원인 기준으로 검증·중복 제거한 body와 inline comment를 만든다. 게시 전 PR state와
base/head SHA, 기존 review/comment 전체를 다시 읽는다. locked base/head 중 하나라도 현재 값과
다르면 게시하지 않는다. marker는 `<!-- sonsu-review-pr:<run-id>:<head-sha> -->`이며 author,
commit과 canonical payload를 함께 동일성 기준으로 사용한다.

[`../skills/review-pr/scripts/review_protocol.py`](../skills/review-pr/scripts/review_protocol.py)에
locked/current base SHA와 head SHA, reviewer status·attempt count, publish attempt와 readback
completeness·marker·author·commit·payload 일치 여부를 전달한다. `post_once`일 때만 최초 POST를
수행한다.

POST 응답이 불명확하면 review와 inline comment를 끝까지 readback한다. complete readback에서 marker,
author, commit과 payload가 모두 일치하면 기존 POST 성공으로 확정한다. 하나라도 다르거나 readback이
불완전하면 늦은 반영 가능성 때문에 재게시하지 않는다. provider의 create mutation에 안전한
idempotency key가 없는 한 GET 결과가 없다는 사실도 최초 POST 실패를 증명하지 않는다.

## 결과와 cleanup

locked/current base SHA와 head SHA, 세 reviewer 상태, retry, finding과 inconclusive, marker,
POST/readback 결과, review URL 또는 중단 action을 보고한다. reviewer 종료 뒤 plugin-owned clean
checkout만 제거한다. dirty 또는 종료 불명 checkout은 보존해 상태와 경로를 알린다.
