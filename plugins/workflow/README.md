# Workflow

티켓·PR artifact와 provider 상태를 다루는 `1.0.0` capability pack이다. 일반 branch, worktree,
commit과 push 작업은 host 기본 Git 동작이 담당한다.

## Skills

- `inspect-prs`: 열린 PR 또는 지정 PR의 CI·review·merge 상태를 읽기 전용으로 조회
- `repair-pr`: 요청 범위에서 conflict → review finding → CI 순서로 한 번 복구
- `to-ticket`: ticket 초안·게시와 기존 제목·본문 수정
- `ticket-lifecycle`: 기존 ticket 상태·담당자·relation 변경
- `to-pr`: 새 PR 초안·게시와 ticket·시각 자료 연결

각 skill은 실제 provider target과 현재 permission을 확인한다. mutation 직전에 최신 state를 다시
읽고, mutation 뒤 canonical resource를 readback해 `applied | unapplied | unknown | no-op`을
구분한다. timeout이나 불명확한 응답을 같은 create/update 재전송으로 덮지 않는다.

`repair-pr`는 요청한 범위만 conflict, review finding, CI 순서로 처리한다. 승인된 commit은 root
cause별로 나누고 push가 승인되면 모든 수정과 local verification 뒤 마지막에 한 번만 수행한다.
polling loop, 자동 merge와 unrelated cleanup은 시작하지 않는다.

Ticket 문구는 `to-ticket/references/ticket-writing.md`와 `ticket-quality-bar.md`, PR 문구는
`to-pr/references/pr-writing.md`와 `pr-quality-bar.md`가 정본이다. 일반 문장 교정 plugin이나
다른 marketplace package를 요구하지 않는다.

```sh
codex plugin add workflow@sonsu-marketplace
```
