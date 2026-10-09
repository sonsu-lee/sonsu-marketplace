---
name: push
description: 검증된 현재 Git commit을 사용자가 요청한 정확한 remote ref로 일반 push할 때 사용한다. branch·commit 생성, force push, PR 생성과 merge는 담당하지 않는다.
---

# Git push

현재 repository의 검증된 commit을 승인된 대상으로 보내고 실제 원격 ref를 다시 읽는다. branch·commit의 준비 여부는 현재 Git 상태에서 확인한다.

## 절차

1. [전달 권한](../../references/delivery-authority.md)으로 전송 범위를 확인한다. [Git 안전 규칙의 대상 고정](../../references/git-safety.md#push-대상을-고정한다)을 적용해 source SHA와 destination remote/ref를 확정한다.
2. 예상 source·destination이 일치하면 일반 push를 수행한다. non-fast-forward나 예상과 다른 ref는 필요한 별도 Git 작업으로 보고한다.
3. 같은 remote ref를 다시 읽어 local SHA와 비교한다. 응답이 불명확하면 [공통 재조회 규칙](../../references/git-safety.md#공통-확인과-결과)을 따르고, 미반영이 확인된 경우에만 재시도를 판단한다. 여러 단계의 외부 쓰기는 [연속성 기록](../../references/continuity.md)에 남긴다.

## 결과

source SHA, 실제 반영된 remote/ref·SHA, 미확인 상태와 필요한 별도 작업을 구분해 보고한다.

## 예시

입력: “현재 커밋을 `backup`의 `refs/heads/fix/cache-ttl`로 push해 줘.”

결과: 확인한 source SHA를 해당 destination에 일반 push하고 같은 ref를 재조회한다. SHA가 일치하면 반영 완료로, 조회가 실패하면 push 응답과 원격 반영 미확인을 구분해 보고한다.

## 경계

- branch·commit 생성, force push, PR 생성과 merge는 별도 작업으로 남긴다. non-fast-forward를 자동 pull·rebase로 해결하지 않는다.
- 로그인·계정 변경·credential 저장과 hook·branch protection 우회는 자동 수행하지 않는다.

## 참고 자료

- [Git 안전 규칙](../../references/git-safety.md)
- [전달 권한](../../references/delivery-authority.md)
- [작업 연속성](../../references/continuity.md)
