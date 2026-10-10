---
name: commit
description: 요청한 변경만 staging해 새 commit을 만들거나 Conventional Commit 메시지를 준비할 때 사용한다. push, amend, rewrite와 PR 생성은 담당하지 않는다.
---

# 커밋 준비와 생성

실제 diff에서 독립적으로 설명하고 되돌릴 수 있는 변경을 골라 메시지 또는 새 commit으로 전달한다. 메시지 제안은 읽기 전용으로 완료한다.

## 절차

1. [전달 권한](../../references/delivery-authority.md)과 [Git 안전 규칙](../../references/git-safety.md)으로 요청 범위를 확인한다. HEAD, index, worktree와 전체 diff를 읽는다.
2. 요청한 변경과 필요한 테스트·문서를 한 목적의 단위로 묶는다. 관계없는 수정·생성 파일·삭제, 비밀·대용량 파일·의도하지 않은 binary를 구분한다. 같은 파일의 다른 목적 변경은 hunk 단위로 분리하고 안전한 분리가 어려우면 충돌 범위를 알린 뒤 commit 전에 멈춘다.
3. [커밋 메시지 기준](../../references/commit-message.md)에 맞춰 언어·제목·본문·footer·AI 사용 표기를 정한다. 확인된 구현 효과·실행한 검증·확인된 티켓 상태만 기록한다.
4. 생성 승인이 있으면 HEAD·index·worktree·대상 diff를 재확인하고 승인된 경로 또는 hunk만 stage한다. staged diff·포함 경로·최종 메시지를 확인한 뒤 repository의 hook과 signing 정책을 유지해 새 commit을 만든다.
5. 새 commit의 SHA·부모·tree·메시지·포함 경로를 다시 읽고 남은 worktree·index 변경을 구분한다. 실패 응답이 불명확하면 HEAD 이동 여부를 먼저 확인한다. 여러 단계 작업은 [연속성 기록](../../references/continuity.md)에 남긴다.

## 결과

메시지 제안 또는 생성된 SHA와 포함 범위, 실제 검사 결과, 남은 변경을 보고한다. hook·signing 실패는 원인과 현재 HEAD를 함께 보고한다.

## 예시

입력: “재시도 간격 오타만 커밋해 줘. 같은 파일의 로그 문구 수정은 남겨 둬.”

결과: 승인된 간격 수정 hunk와 관련 테스트만 stage하고 `fix: correct retry interval`로 커밋한다. 확인한 SHA·포함 경로와 남겨 둔 로그 문구 변경을 따로 보고한다.

## 경계

- 기존 staged 변경을 자동으로 unstage하거나 관계없는 변경을 포함하지 않는다.
- hook·signing 실패를 우회하지 않는다. 기존 commit의 amend·rewrite는 수행하지 않는다.
- push·PR 생성은 각각 별도 승인과 담당 절차로 처리한다.

## 참고 자료

- [커밋 메시지 기준](../../references/commit-message.md)
- [Git 안전 규칙](../../references/git-safety.md)
- [전달 권한](../../references/delivery-authority.md)
- [작업 연속성](../../references/continuity.md)
