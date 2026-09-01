# Git 안전 규칙

commit 또는 push처럼 Git 상태를 변경할 때 읽는다.

## 변경 범위를 보존한다

- 작업 전후의 `HEAD`, index, worktree와 untracked 파일을 확인한다.
- 사용자가 요청한 경로와 hunk만 stage한다.
- 기존 staged 변경을 자동으로 해제하거나 다른 commit에 포함하지 않는다.
- 관계없는 수정, 생성 파일과 삭제를 복구하거나 정리하지 않는다.
- merge, rebase, cherry-pick 또는 revert가 진행 중이면 새로운 일반 workflow를 시작하지 않는다.

## Push 대상을 고정한다

- 정확한 remote URL, 인증 주체, current branch와 local head SHA를 확인한다.
- 사용자가 지정한 remote와 ref를 우선하고, 없으면 검증된 upstream과 repository 관례를 사용한다.
- 새 upstream이 필요하면 정확한 source와 destination ref를 보여 주고 일반 push만 수행한다.
- remote ref가 예상과 다르거나 non-fast-forward라면 자동으로 pull, rebase, merge 또는 force push하지 않는다.
- push 결과가 불명확하면 local SHA와 remote ref를 다시 조회한 뒤 재시도 여부를 판단한다.

## 실행 위임과 비밀을 보호한다

Git은 hook, signing program, filter, diff driver, credential helper, SSH command와 remote helper를 실행할 수 있다. 관련 명령이 실패하거나 더 넓은 host 권한이 필요하면 실행 파일과 대상 host가 예상한 범위인지 확인한다.

전체 환경변수나 Git 설정을 덤프하지 않는다. token, header, private key, passphrase, credential helper 결과와 credential 파일 내용을 출력하지 않는다. repository가 제어하거나 내용을 확인할 수 없는 hook·helper에 더 넓은 권한을 부여하지 않는다.

hook을 끄거나 `--no-verify`로 우회하지 않는다. signing, branch protection과 required checks를 완화하지 않는다. force push, reset, restore, clean과 자동 stash를 사용하지 않으며 인증 실패를 해결하기 위해 자동 로그인, 계정 전환 또는 credential 저장을 수행하지 않는다.
