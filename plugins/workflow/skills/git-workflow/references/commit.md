# Commit 규칙

commit 메시지를 준비하거나 staged 변경에서 새 commit을 만들 때 읽는다.

## 원자성을 확인한다

하나의 commit에는 독립적으로 설명하고 되돌릴 수 있는 한 가지 목적만 담는다. 전체 diff를 읽고 다음을 구분한다.

- 요청한 변경
- 해당 변경에 필요한 테스트와 문서
- 관계없는 수정, 생성 파일과 삭제
- 비밀, 생성물, 대용량 파일과 의도하지 않은 binary

관계없는 변경이 같은 파일에 섞여 있으면 경로 전체를 stage하지 않고 요청된 hunk만 다룬다. 안전하게 분리할 수 없으면 commit 전에 충돌하는 범위를 알리고 멈춘다. 기존 staged 변경을 자동으로 unstage하지 않는다.

## Conventional Commit을 작성한다

repository 규칙이 없으면 다음 형식을 사용한다.

```text
<type>(<optional-scope>): <imperative summary>
```

`type`과 `scope`는 실제 diff와 repository 관례에서 고른다. summary는 변경의 결과를 간결하게 설명한다. 구현하지 않은 효과, 실행하지 않은 테스트와 확인하지 않은 티켓 상태를 메시지에 넣지 않는다. breaking change 표시는 실제 호환성 변화가 있고 repository 형식에 맞는 경우에만 사용한다.

티켓 ID나 URL은 사용자 요청 또는 repository 관례가 있을 때만 subject나 footer에 포함한다. commit message를 tracker 연결의 기본 채널로 사용하거나 티켓 ID를 만들지 않는다.

## 생성하고 확인한다

1. `HEAD`, index, worktree와 대상 diff를 다시 확인한다.
2. 승인된 경로 또는 hunk만 stage한다.
3. staged diff, 포함 경로와 최종 메시지를 확인한다.
4. repository의 hook과 signing 정책을 유지한 채 새 commit을 만든다.
5. 새 commit의 SHA, 부모, tree, 메시지와 포함 경로를 다시 읽는다.
6. worktree와 index에 남은 변경을 commit 범위와 구분한다.

hook 또는 signing이 실패하면 우회하지 않는다. 실패 결과가 불명확하면 `HEAD`가 이미 이동했는지 확인하기 전에는 commit을 다시 실행하지 않는다. 기존 commit의 amend나 rewrite는 수행하지 않는다.
