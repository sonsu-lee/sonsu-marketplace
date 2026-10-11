# PR 리뷰 실행과 게시

`review-code`의 일반·심층·다중 PR 리뷰가 사용하는 실행 계약이다.
인원·모델·추론 강도는 현재 호스트 프로필의 `pr_review`와 사용자 지정에 따른다.
기본은 한 라운드에 새 검토자 1명이며 상위 모델 검토를 자동 추가하지 않는다. PR 외 일반 리뷰·
개발 DAG의 역할 인원과 라운드 상한은 이 경로의 기본값이 아니다. 현재 요청과 기존 문맥에서도 리뷰
의도가 확인되지 않는 PR URL 단독 입력에는 리뷰 실행·게시를 추가하지 않는다. 상태 조회·로컬
코드 리뷰·기존 결과 정리만 요청한 작업에도 게시를 추가하지 않는다.

## 검토자 설정

현재 호스트의 [Codex](model-profiles.md), [Claude Code](claude-model-profiles.md),
[omp](omp-model-profiles.md) 프로필을 읽는다. Codex는 `pr_review`의 Luna xhigh 1명,
Claude Code는 Opus 5.5 medium 1명이 기본이다. omp는 `settings_policy: inherit_native`에
따라 순정 `reviewer` 1명을 기존 설정으로 요청한다. 순정 reviewer와 직접 설치한 Review
agent를 구분하고 model·effort·memory·isolation·동시성이나 역할별 override를 자동 변경하지 않는다.

사용자가 지정한 인원·모델·effort는 해당 항목만 우선한다. 인원만 늘리면 같은 PR 기본 역할을
지정한 수만큼 호출하며 다른 모델을 섞거나 관점을 강제로 나누지 않는다. 심층 요청만으로 PR 외
기본 5인·5라운드나 상위 모델을 추가하지 않는다. 다른 플러그인이나 특정 CLI 설치를 필수로
요구하지 않고 필요한 격리를 지원하는 실행 경로를 선택한다. 미지원 설정·대체·격리 실패는
근거와 `blocked`/`not_run`으로 기록하며 조용히 대체하지 않는다.

판단 정체, 상충 근거, 복잡한 상태·권한·복구 경계나 판단 능력 부족이 확인되면 추가 근거를
확보하고 적합한 검토/판정 설정을 선택한다. Codex는 `senior_review`, `adjudication`,
`complex_adjudication`을 사용하며 다른 모델은 지원·접근권을 확인한 명시 override로 지정한다.
Claude는 Opus 5.5를 유지하고 필요하면 더 높은 effort의 별도 native 정의를 선택한다.
omp는 기존 설정을 우선하고 사용자가 명시한 실행만 정확한 provider/model/effort로 지정한다.
라운드 수나 용량 오류만으로 승격하지 않는다. 새 전체 리뷰에는 이전 결과를 숨기고 특정
finding 판정에는 그 finding과 근거를 제공한다.

## 요청 범위

사용자가 특정 PR의 리뷰를 요청하면 독립 검토와 결과의 해당 PR 게시까지 완료한다.
`로컬에서만`, `게시하지 마`, `초안만`, 모든 쓰기 금지 등 명시한 제한과 호스트 권한을 우선한다.
스킬 이름 지정만으로 게시 대상을 만들거나 제한을 해제하지 않는다. 단독 리뷰 요청은 소스 수정,
commit·push·merge 또는 `APPROVE`·`REQUEST_CHANGES` 제출 권한으로 확장하지 않는다.
이미 수정까지 승인된 작업에서는 조정자가 담당 구현 단계에서 지적을 수정하고 새 리뷰를 이어간다.
기본 게시 형식은 조정자의 통합 `COMMENT` 리뷰다.

이 기본값은 PR 리뷰에 결과 게시를 포함하도록 정한 사용자 계약을 구현한다. 공통 전달 권한의
승인은 그 요청에 포함되며 별도 메시지로 다시 확인하지 않는다. 공통 리뷰 기준의 읽기 전용
범위 중 소스 수정 금지는 유지하고, PR 리뷰의 준비용 fetch·워크트리와 결과 게시는 이 문서의
명시적 예외로 수행한다. 일반 로컬 리뷰에는 이 예외를 적용하지 않는다. Review가 리뷰
결과의 통합·게시·재조회를 끝까지 소유하며, Git의 PR 생성·제목/본문 작성과 구분한다.

## 읽기 전용 snapshot 도구

설치한 플러그인의 `scripts`를 `REVIEW_SCRIPTS`, 정확한 이력이 있는 로컬 checkout을 `REPO`로
지정한다. 이 도구는 `git`과 인증된 `gh`로 metadata만 조회한다. fetch·diff 패키징·워크트리
생성·원격 쓰기는 수행하지 않는다. 필요한 fetch는 승인된 준비 단계에서 별도로 수행하고,
수집한 `fixed_shas`와 fetched commit을 대조한다. shallow 저장소, 없는 commit, 공통 조상 없음,
여러 merge base는 근사하지 않고 실패로 반환한다. `review-package`는 수집된
`merge_base`부터 `head`까지 diff를 고정하는 별도 도구다.

```bash
python3 "$REVIEW_SCRIPTS/pr_review_snapshot.py" capture 87 --repository github.com/acme/catalog --repo "$REPO" --output "$BEFORE"
python3 "$REVIEW_SCRIPTS/pr_review_snapshot.py" compare --against "$BEFORE" --repo "$REPO" --output "$PRE_POST"
python3 "$REVIEW_SCRIPTS/pr_review_snapshot.py" compare --against "$PRE_POST" --repo "$REPO" --output "$POST"
```

`capture [PR]`은 번호 또는 HTTPS PR URL을 받는다. URL의 host·base repository를 우선하고
`--repository HOST/OWNER/REPO`와 충돌하면 실패한다. 번호만 주면 `gh repo view`로 저장소를
확인한다. PR도 생략하면 현재 브랜치의 열린 PR이 정확히 하나인 경우만 선택한다.
`compare --against FILE`은 성공한 저장 snapshot의 대상을 다시 조회하므로 PR 선택 인자가 없다.
두 명령의 `--repo PATH` 기본값은 현재 디렉터리이며 `--output FILE`은 기존 파일을 덮지 않고
새 파일로만 저장한다. stdout에도 같은 JSON을 출력한다. 모든 파일 쓰기 금지 시 `--output`을
생략하고 결과를 호출 입력에 보존한다. 저장 파일 비교가 불가능하면 동일 필드를 읽기 전용으로
대조하고 자동 비교를 실행했다고 보고하지 않는다.

| 필드 | 의미와 사용 |
| --- | --- |
| `schema_version`, `status` | 현재 schema는 `1`; `ok`, `changed`, `blocked`로 수집 상태를 구분 |
| `snapshot.host`, `repository`, `number`, `url`, `state` | GitHub host·base 저장소·PR 식별자와 `open`/`closed`/`merged` 상태 |
| `snapshot.base`, `head` | 각각 `{sha, ref, repository}`; fork의 head repository와 base repository를 구분하며 삭제된 head repository는 `null` |
| `snapshot.merge_base`, `fixed_shas` | 검증한 정확한 공통 조상과 고정 `{base, head, merge_base}` SHA; 로컬 working tree는 포함하지 않음. 닫힌 PR이거나 비교 대상과 base/head SHA가 다르면 로컬 이력을 확인하지 않으므로 `merge_base`는 `null`이고 `fixed_shas`에는 원격 base/head SHA만 있음 |
| `snapshot.existing_review_ids`, `existing_inline_comment_ids` | 모든 페이지에서 수집한 ID 목록; 본문·작성자·해결 상태를 판정하는 자료는 아님 |
| `snapshot.collection_stable`, `observed_after` | metadata를 수집 앞뒤로 읽어 같았는지와 마지막 관측; 원자적 조회나 이후 불변을 보증하지 않음 |
| `comparison` | `unchanged`, `changed_fields`, `before`/`after` state·fixed SHA, `new_review_ids`, `new_inline_comment_ids` |
| `error` | `blocked`일 때 확인하지 못한 원인 |

종료 코드 `0`은 수집 중 안정된 열린 PR이며 비교 모드에서는 저장 SHA/state도 같다.
`1`은 닫힌 PR, 저장 SHA/state의 차이 또는 수집 중 변경이다. `2`는 인자·저장 파일·도구·인증·
응답·Git 이력 오류다. argparse 인자 오류는 stderr로 출력하고 `2`로 종료한다.
`1`이면 기존 검토 결과와 현재 상태를 구분하고 쓰기를 멈춘다. `2`이면 원인을 해결하기 전까지
SHA 일치나 게시 가능 상태를 주장하지 않는다.

위 예시의 첫 compare는 게시 직전, 둘째는 게시 후에 실행한다. 쓰기 재시도 전에도 새로 비교한다.
`changed_fields`가 비어 있어도 `collection_stable=false`면 수집 중 변한 것이다.
ID 증가만으로 이번 게시를 식별할 수 없으므로 아래 게시 계약의 작성자·commit_id·본문·댓글
payload 대조와 원격 readback은 별도로 수행한다. 도구의 `ok`는 게시 권한·리뷰 완료·게시 성공이 아니다.

## 대상 고정과 워크트리

1. 정확한 GitHub host·repository·PR 번호·state·base/head SHA와 merge base를 확인한다.
   필요한 이력을 fetch하고 원격 metadata와 fetched SHA를 대조한다. 전체 PR diff는 merge base부터
   head까지이며 사용자의 dirty 변경을 포함하지 않는다. fork도 검증한 PR ref와 정확한 SHA로 고정한다.
2. 각 리뷰어마다 다른 경로에 `git worktree add --detach <path> <head-sha>`로 워크트리를 만든다.
   모든 워크트리의 HEAD와 초기 clean 상태를 확인하고 각 세션의 작업 디렉터리를 해당 경로로 지정한다.
   native 도구에 cwd 인자가 없으면 brief에 절대 경로를 지정하고 첫 작업에서 cwd·HEAD 확인을 요구한다.
   경로·HEAD·초기 clean 확인에 실패하면 올바른 workdir로 지정해 다시 확인한다. 해결할 수 없으면
   해당 리뷰어를 `blocked`/`not_run`으로 남기고 그 결과를 완료된 워크트리 리뷰로 합치지 않는다.
   원래 checkout에서 reset·checkout·stash로 사용자 변경을 옮기지 않는다.
3. root가 각 라운드마다 별도 새 세션으로 요청한 리뷰어를 생성한다. 같은 고정 입력·전체 diff·관련
   소스·현재 요구사항·프로젝트 지침·공통 기준을 전달하고 부모 대화, 구현 서사와 이전/다른 리뷰
   결과를 제외한다. Codex·Claude는 memory 주입·생성을 실행별로 끄고, omp는 기존 native
   제어 상태를 확인하며 자동으로 설정을 변경하지 않는다. 새 문맥·파일 공간·memory 차단은 각각 확인한다.
   세션 ID·워크트리 경로·base/head 또는 로컬 snapshot digest·요청/관측 설정·격리 근거를 연결한다.
   지원되는 실행 경로로도 요구한 memory 제어를 확인할 수 없으면 한계와 `blocked`/`not_run`을
   남기고 완전 격리 리뷰 완료로 표현하지 않는다. Git worktree는 보안 sandbox가 아니다.
4. 사용자가 여러 명을 지정했고 슬롯이 충분하면 병렬 실행한다. 슬롯·깊이 제한일 때 가능한 수로 나눠 실행하며
   전역 설정을 자동 변경하거나 다른 작업의 에이전트를 중단하지 않는다. leaf는 읽기 전용 검토와
   결과 반환만 맡고 추가 위임·소스 수정·원격 게시를 하지 않는다. 검사용 생성물은 자기 임시 공간에 둔다.
5. 워크트리를 만들 수 없으면 원인·실행 한계를 보고한다. 사용자가 허용한 snapshot/inline 대체만
   사용하고 그것을 워크트리 실행으로 기록하지 않는다. 모든 파일 쓰기 금지 시 워크트리도 만들지 않는다.

### 호스트별 새 세션과 memory 제어

- Codex: `fork_turns=none`은 부모 대화 차단이며 자동 memory 차단을 대신하지 않는다.
  native 실행별 memory 설정을 지원하면 주입·생성을 모두 끈다. CLI 경로에서는 resume/fork 없이
  새 `codex exec --ephemeral`에 `-c memories.use_memories=false`와
  `-c memories.generate_memories=false`를 적용한다. 모델과 `model_reasoning_effort`도 명시한다.
  현재 CLI가 지원하면 `--strict-config`로 알려지지 않은 키를 거부한다. memory를 주입·수집하는
  hook·외부 도구도 별도로 비활성화/제외하고 관련 기록을 남긴다.
- Claude Code: 매 라운드 새 non-fork subagent를 선택하고 persistent `memory` 필드를 사용하지
  않는다. main 대화·auto memory를 독립 brief에 넣지 않는다. CLI 대안은
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`과 새 `claude -p --no-session-persistence`이며,
  역할의 정확한 model과 frontmatter effort를 적용한다. `--bare` 또는 CLAUDE.md 전체 차단은
  필요한 프로젝트 지침까지 제외하므로 현재 계약을 잃는 대안으로 사용하지 않는다.
- omp: 순정 `reviewer`의 기존 model·effort·memory·isolation·동시성 설정을 유지한다.
  `task.agentModelOverrides`나 memory overlay를 기본 실행 조건으로 추가하지 않는다.
  매 라운드 새 task reviewer를 생성하고 부모 대화·이전 finding을 brief로 넘기지 않는다.
  별도 프로세스 경로는 resume 없이 새 `omp --no-session -p <brief>`이며, brief에서 순정
  `reviewer` 호출과 완료 결과 수집을 명시한다. `isolated`는 파일 공간 분리이며 memory off와
  다르다. 기존 설정에서 isolation을 사용할 수 없으면 자동 활성화하지 않고 외부에서 소유한
  임시 워크트리 경로를 지정한다. 그 공간의 정리는 외부 조정자가 담당한다. memory backend와
  추가 주입 상태를 확인하고, 요구한 격리를 충족할 수 없으면 한계를 남긴다. 사용자가 모델이나
  설정 변경을 명시한 경우에만 별도 실행에서 적용하고 실제 관측 설정을 대조한다.

각 호스트의 context provider·hook·외부 memory tool에 의한 추가 주입/생성도 확인한다.
프로젝트 규칙·현재 요구사항·소스·검사 결과는 남긴다. 정책 문구나 설정 요청만으로 관측된
격리를 주장하지 않으며 다른 작업의 memory·전역 설정을 자동으로 변경하지 않는다.

각 검토자에게 고정 base/head의 전체 diff와 caller·test·계약을 읽기 전용으로 검토하고 이전
작업 memory를 조회·생성하지 않도록 지시한다. 실제 발생 조건·영향·근거가 있는 지적만
priority·`path:line`·원인·최소 수정 방향으로 반환하고 확인 범위·실행한 검사·미확인도 보고하게 한다.
지적 없음은 정확성·보안의 증명이 아니다. 조정자는 이전 라운드 이력과 지적별 수정 상태를
별도로 보존하고 새 검토자에게 잠정 통과 결론을 넘기지 않는다.

## 지적 검증과 반복 종료

1. root가 해당 라운드의 모든 원결과를 수집해 계약·도달 경로·재현/정적 근거로 판정한다.
   원인별 중복을 합치고 지적별 `valid`/`dismissed`/`inconclusive`, 수정·검사 상태를 추적한다.
   생성 성공만으로 완료를 세지 않는다. 실행 실패·빈 결과와 검토 완료 후 지적 없음을 구분한다.
   다수결이나 지적 수 경쟁을 사용하지 않고 중요한 미판정 후보는 근거를 확보할 때까지 남긴다.
2. 리뷰만 요청받았으면 검증한 지적과 미해결·한계를 보고/게시한다. 이미 수정 권한이 있으면
   담당 구현 단계에서 실제 문제를 수정하고 필요한 검사를 수행한다. 검토자에게 수정을 맡기지
   않으며 commit·push 권한은 별도로 확인한다. root가 이전 finding의 해소를 별도로 확인한다.
3. 수정 후 전체 PR 또는 로컬 전체 변경 snapshot을 다시 고정하고 새 검토자를 생성한다.
   새 전체 리뷰어는 이전 finding과 수정 서사를 받지 않는다. 국소 수정 재확인은 그 finding의
   해소 근거이며 전체 PR 재리뷰를 대신하지 않는다. 다른 모델로 전환한 전체 리뷰에도 같은 규칙을 적용한다.
4. 판단 정체·상충 근거·필요한 능력 부족을 확인하면 추가 근거 또는 명시한 상위 설정으로
   검토/판정을 수행한다. 환경·입력·용량 오류부터 해결하며 호출 횟수만으로 승격하지 않는다.
   특정 finding 판정은 그 finding을 제공하고, 새 전체 리뷰와 구분해 기록한다.
5. 현재 산출물에 미해결 검증 지적·중요한 미판정 후보가 없고 필요한 검사가 통과하면 종료한다.
   이 결과를 완전한 무결함 증명으로 표현하지 않는다. 사용자 예산·중단·호스트 한계로 멈추면
   미해결과 `incomplete`/`blocked`를 보존한다. 세션·모델 변경으로 이력이나 예산을 초기화하지 않는다.
   같은 완료 결과를 횟수만 채우려고 다시 검토하지 않는다.

로컬 수정이 원격 head에 반영되지 않았으면 로컬 snapshot의 검토와 원격 PR 상태를 구분한다.
현재 원격 PR이 수정·수렴했다고 게시하지 않는다. 예상한 승인된 수정 외에 원격 base/head가
바뀌면 기존 결과를 보존하고 범위·권한·새 고정 입력을 다시 확인한다. 외부 SHA 변경은 자동 수정 권한이 아니다.

## 일시 실행 오류

Codex의 `Selected model is at capacity. Please try a different model.` 오류는
원인 미상의 일시 실행 오류로 기록한다. Claude Code에서도 일시 용량 오류는 실제 반환된 오류를 근거로 분류한다. 오류 문자열만으로 모델 미지원, 계정 한도,
로컬 슬롯·깊이 제한, 실제 서버 전체 장애를 확정하거나 사용자에게 모델 변경을 먼저 요구하지 않는다.

이 오류로 실패한 실행만 같은 모델·추론·고정 입력으로 짧게 간격을 두어 재시도한다. 기본은 최초 시도 뒤
최대 3회이며 사용자나 호스트가 정한 더 작은 한도가 있으면 따른다. 일시 오류만으로 원래 병렬 수를
자동 축소하지 않는다. 같은 세션을 이어 쓸 수 있으면 재사용하고, 세션이 복구 불가능하면 같은
입력의 새 세션을 만들되 이전 실행 종료를 확인하고 같은 논리 리뷰어의 재시도로 기록한다.
같은 완료 입력을 일시 오류 재시도로 반복하지 않고 재시도 횟수를 독립 리뷰어 수에 더하지 않는다.
승인된 수정 뒤 새 산출물을 검토하는 다음 라운드는 이 실행 오류 재시도와 별개다.

계속 실패하면 완료된 결과를 보존하고 `blocked`/`incomplete`로 보고한다. 실패를 지적 없음이나
성공으로 무시하지 않는다. 오류 원문·시도 횟수·설정을 남긴다. 다른 오류나 rate-limit·모델 지원·
슬롯 제한은 반환된 구조화된 정보·지원 목록 등 별도 근거로 분류하며 위 오류 문자열 자체를
그 근거로 다시 사용하지 않는다. 요청 형식·인증·권한 오류를 이 재시도 분기에 넣지 않는다.

## 통합과 GitHub 게시

1. 게시할 revision의 요청한 검토를 모두 모아 근거를 확인하고 원인·발생 조건·필요한 수정 기준으로 중복을 합친다.
   각 리뷰어가 같은 지적을 개별 게시하지 않는다. 근거 공백·상충 지적만 집중 재확인한다.
2. 최초 제출과 모든 쓰기 재시도 직전 PR state·base/head와 기존 리뷰·인라인 댓글을 페이지 끝까지 조회한다.
   기존 review ID 목록과 이번 제출의 인증 주체·commit_id·본문·댓글 payload를 기록한다. 대상이 닫혔거나
   SHA가 달라졌으면 이전 SHA의 결과를 보존해 로컬로 보고하며 현재 PR의 완료 리뷰로 게시하지 않는다.
   미완료 리뷰어가 있으면 전체 완료 게시를 보류하고 부족한 범위를 보고한다. 부분 게시를 명시적으로
   요청받은 경우에만 검토 SHA와 미완료 범위를 드러낸 `COMMENT`를 남긴다.
3. 현재 diff의 정확한 path·line·side에 근거가 있는 지적을 한 번씩 인라인으로 붙이고 검토 SHA를
   `commit_id`로 고정한 통합 `COMMENT` 리뷰를 제출한다. 이미 같은 원인·대상·근거의 미해결 댓글이
   있으면 새 중복 댓글 대신 요약에서 기존 댓글을 연결한다. 새 회귀나 별도 수정이 필요한 원인은 유지한다.
   인라인 위치를 사용할 수 없으면 가짜 위치를 만들지 않고 요약에 파일과 근거를 적는다.
4. 요약에는 검토 범위·완료 인원·확인된 결과·검사와 실행 한계를 적는다. 지적 0건도 검토 요약을
   게시하되 완전한 정확성·보안이나 미실행 CI를 보증하지 않는다. 댓글에는 repository의 언어 규칙을 따른다.
5. 응답의 review ID·URL·commit_id·state와 인라인 댓글을 재조회한다. 응답이 불명확하면 같은
   PR의 리뷰·댓글을 먼저 조회하고 게시 전 ID 목록과 인증 주체·검토 SHA·본문·댓글을 대조한다.
   이번 통합 리뷰가 유일하게 확인되면 그 URL을 반환하고 전체 review를 다시 만들지 않는다.
   미반영을 확인했을 때만 2단계부터 다시 수행하고 누락된 쓰기를 재시도한다. 조회 실패뿐 아니라
   기존 동일 리뷰·동시 게시 때문에 이번 반영 여부를 구분할 수 없을 때도 `publication: unknown`으로
   남기고 성공·미반영으로 단정하거나 맹목적으로 재게시하지 않는다.
   게시 도중 head가 바뀌었으면 게시된 검토 SHA와 현재 SHA를 구분해 보고한다.

로컬 전용 요청은 통합 보고서에서 완료하고, 게시 요청의 완료는 원격 readback으로 확인한다.
게시 권한·도구가 없으면 가능한 로컬 검토와 통합 보고서는 완료하되 `publication: blocked`와
원인을 별도로 남긴다. 게시 URL·게시 성공을 만들어내거나 확보한 리뷰 결과를 버리지 않는다.
보고에는 세션·워크트리·요청/관측 모델·추론·오류 재시도·중복 판정·게시 URL 또는 미게시 이유를 남긴다.
매 라운드 자기 리뷰어의 종료와 보고/복구 자료의 별도 보존을 확인한 뒤 소유한 clean 워크트리를 제거한다.
작업 결론에서도 남은 임시 공간을 같은 기준으로 정리하고 제거/보존 경로와 이유를 보고한다. 종료 불명,
dirty 변경 또는 복구에 필요한 자료가 있으면 경로와 상태를 보존하며 강제 삭제하지 않는다.
