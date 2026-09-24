---
name: push
description: 검증된 현재 Git commit을 사용자가 요청한 정확한 remote ref로 일반 push할 때 사용한다. branch·commit 생성, force push, PR 생성과 merge는 담당하지 않는다.
---

# Git push

현재 repository와 명시된 전송 범위를 확인하고 [전달 권한](../../references/delivery-authority.md)과
[Git 안전 규칙](../../references/git-safety.md)을 적용한다. 이 스킬은 단독으로 동작한다.
다른 스킬이 branch나 commit을 먼저 만들었다고 가정하지 않는다. 여러 단계의 외부 쓰기는
필요할 때 [연속성 기록](../../references/continuity.md)을 사용한다.

1. current branch와 local HEAD SHA, remote URL·인증 주체·upstream, 대상 ref와 현재 remote ref를 확인한다.
2. 사용자 지정 remote·ref를 우선한다. 지정이 없으면 실제로 확인한 upstream과 저장소 규칙을 사용한다.
3. 예상한 source와 destination이 일치할 때 일반 push만 수행한다. non-fast-forward는 자동 pull·rebase·force push로 해결하지 않는다.
4. 응답이 불명확하면 remote ref를 조회해 이미 반영됐는지 확인하고, 미반영이 확인된 경우에만 재시도를 판단한다.
5. 실제 반영된 remote/ref와 SHA, 미확인 상태를 구분해 보고한다.

로그인·계정 변경·credential 저장이나 hook·branch protection 우회는 자동으로 수행하지 않는다.
