# PR 미디어 첨부 규칙

PR에 로컬 이미지나 비디오를 넣어야 할 때 읽는다.

## 로컬 산출물을 준비한다

미디어는 repository 밖의 `${TMPDIR}/codex-to-pr/<owner-repository>/<head-sha>/` 아래에 둔다. repository의 `docs/assets`, `public`, `static`, `.github/assets`나 source tree에 자동으로 추가하고 commit하지 않는다. 최종 첨부 사본은 제어 문자와 `#`가 없는 생성형 basename을 사용한다.

operation과 각 파일에 다음 manifest 정보를 기록한다.

```text
repository
base
head
head_ref_oid
pr_url
target_pr_state

attachments[].source_path
attachments[].local_path
attachments[].kind
attachments[].purpose
attachments[].body_section
attachments[].display_order
attachments[].required_for_ready
attachments[].alt_text_or_caption
attachments[].mime_type
attachments[].file_size
attachments[].width
attachments[].height
attachments[].duration
attachments[].codec
attachments[].sha256
attachments[].annotation_status
attachments[].annotation_method
attachments[].sensitive_data_check
attachments[].embedded_metadata_check
attachments[].upload_status
attachments[].body_status
attachments[].provider
attachments[].remote_url
attachments[].deletion_locator
```

secret, token, cookie, 개인정보, 실제 고객 data, 내부 URL, 제한된 보안 정보와 불필요한 local path가 보이면 게시하지 않는다. 애니메이션 GIF를 포함한 이미지는 [시각 증거 규칙](visual-evidence.md)에 따라 변경 위치가 마킹된 사본만 첨부한다. GIF는 변경을 보여 주는 모든 관련 frame에서 marker가 유지되는지 확인하며, 신뢰할 수 있게 마킹할 수 없으면 마킹된 정적 이미지나 비디오로 대체하거나 업로드하지 않는다. GitHub CLI는 이미지를 마킹하지 않으므로 annotation은 upload 전에 이미지에 반영해야 한다. 비디오에는 무엇을 언제 확인할지 설명하는 caption과 필요한 timestamp를 PR body에 둔다.

업로드 전에 이미 설치된 신뢰할 수 있는 decoder로 실제 content type, decode 가능 여부와 확장자의 일치를 확인한다. GIF의 모든 frame과 비디오의 전체 영상·audio track을 검토하여 민감정보가 없는지도 확인한다. EXIF·GPS·XMP, SVG metadata와 video container metadata 같은 embedded metadata도 최종 첨부 사본에서 확인한다. 민감하거나 불필요한 metadata가 있으면 이미 설치된 도구로 정제한 별도 사본을 만들고 다시 검사한다. 전체 내용이나 metadata를 신뢰할 수 있게 검사하지 못하면 각각 `sensitive_data_check` 또는 `embedded_metadata_check`를 `inconclusive`로 기록하고 업로드하지 않는다. 이를 위해 image library, codec, `ffmpeg`, metadata 도구나 player를 자동 설치하지 않는다.

## GitHub CLI 지원을 감지한다

GitHub native attachment를 기본으로 사용한다. 실행 직전에 `gh --version`, `gh pr create --help`, `gh pr edit --help`와 `gh pr ready --help`를 확인하고, 실제로 사용할 명령의 도움말에 필요한 flag가 있을 때만 CLI attachment를 사용한다. `--attach`는 GitHub CLI `2.99.0`에서 추가됐지만 배포판의 backport나 지연을 고려하여 help output을 최종 기준으로 삼는다. 현재 CLI가 지원하지 않아도 자동으로 설치하거나 upgrade하지 않는다.

지원되는 CLI에서는 다음 계약을 지킨다.

- image: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, 파일당 최대 `10 × 1024²` bytes
- video: `.mp4`, `.mov`, `.webm`; Free plan의 server 제한은 10 MB, paid plan은 100 MB이며 CLI의 로컬 상한은 `100 × 1024²` bytes
- 파일 확장자는 대소문자를 구분하지 않으며 실제 bytes나 codec이 아니라 확장자로 유형을 판정한다.
- 한 명령에는 최대 50개의 서로 다른 regular file만 허용한다. 빈 파일, directory, named pipe, stdin `-`, 없는 경로와 같은 파일을 가리키는 중복 경로는 허용하지 않는다.
- GitHub.com과 GitHub Enterprise Cloud with data residency를 지원하고 GitHub Enterprise Server는 지원하지 않는다.
- OAuth, classic PAT와 fine-grained PAT를 사용할 수 있다. GitHub App token과 확인할 수 없는 token 유형은 지원하지 않는다. 대상 base repository에 `WRITE`, `MAINTAIN` 또는 `ADMIN` 권한이 필요하므로 base에 write 권한이 없는 fork contributor에게는 CLI attachment를 사용하지 않는다.

video plan이나 repository 소유자의 plan을 확인하지 못하면 10 MB를 안전한 상한으로 사용한다. paid plan에서 10 MB를 넘는 비디오는 GitHub가 요구하는 organization member, outside collaborator 또는 paid-plan 사용자 조건도 확인한다. GitHub가 권장하는 H.264처럼 실제 reviewer 환경에서 재생 가능한 codec인지도 확인한다. token scope가 충분한지 추측하거나 scope 확대, 로그인과 계정 전환을 자동으로 수행하지 않는다.

파일은 repository나 임의 object storage에 넣지 않고 GitHub user attachment storage에 올라간다. public repository의 첨부는 인증 없이 접근될 수 있고 private·internal repository의 첨부는 repository 접근 권한을 따른다. 업로드 전에 PR visibility와 media 공개 범위가 맞는지 확인한다.

GitHub Draft PR의 가용성은 repository visibility와 plan에 따라 다르다. 계정명이나 visibility만으로 지원을 단정하지 않고, 미디어를 올리기 전에 attachment 없는 Draft PR 생성으로 실제 지원 여부와 정확한 대상 PR을 확인한다.

공식 참고: [GitHub CLI 파일 첨부](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli), [`gh pr edit`](https://cli.github.com/manual/gh_pr_edit), [GitHub 첨부 형식과 크기](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files), [Draft PR 가용성](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request), [GitHub CLI 2.99.0](https://github.com/cli/cli/releases/tag/v2.99.0)

## 기본 흐름에서는 로컬 경로를 body에 노출하지 않는다

GitHub CLI는 body가 같은 로컬 파일을 참조하면 그 위치의 destination을 upload URL로 바꿀 수 있다. 하지만 여러 upload 중 일부만 성공해도 PR을 생성하므로 실패한 파일의 local path가 body에 남을 수 있다. `to-pr`의 기본 흐름에서는 local reference를 body에 쓰지 않는다.

대신 repository template이 허용하면 `Visual evidence`를 body의 마지막 section으로 두고 각 marker와 video에서 확인할 내용을 text로 설명한다. body가 참조하지 않은 attachment는 flag 순서대로 끝에 추가되므로 manifest의 `display_order`와 `--attach` 순서를 일치시킨다. 여러 파일이면 설명에도 `Attachment 1`, `Video 3`처럼 같은 번호를 붙여 각 파일과 caption이 일대일로 대응하게 한다. before와 after를 표로 비교해야 하면 가능할 때 마킹된 두 화면을 하나의 안전한 comparison image로 합친다.

template이 section 순서를 고정하여 visual section을 마지막으로 옮길 수 없으면 append된 상태를 최종 body로 사용하지 않는다. Draft PR에 파일을 하나씩 첨부하고 저장된 body에서 각 remote URL을 확인한 뒤, URL을 template의 지정된 visual section에 넣은 완성 body를 `gh pr edit --body-file`로 다시 기록한다. 재조회하여 body 끝의 중복 attachment와 local placeholder가 제거되었고 URL이 지정 section에만 남았는지 확인한다.

이미지 인자는 shell 해석을 피하도록 전체를 quote하고 `--attach '/absolute/path/annotated-after.png#Marker 1 shows the changed navigation state'`처럼 alt text를 붙인다. 비디오는 alt text를 지원하지 않으므로 `#` 뒤의 설명을 주지 않는다. 비디오는 append되면 bare URL로 기록되어 player로 표시된다.

공식 CLI가 지원하는 in-place rewrite를 사용자가 특별히 요청하면 상대 경로가 body file이 아니라 `gh` 실행 directory 기준임을 확인한다. 부분 실패 때 공개되어도 안전한 경로만 사용하고 절대 home path는 body에 넣지 않는다. 이미지의 body reference에 이미 alt text가 있으면 `--attach` 인자보다 body의 alt text가 우선한다.

비디오를 in-place player로 배치하려면 inline-style image 문법인 `![설명](./clip.mp4)`가 해당 문단의 유일한 내용이어야 한다. 이때 image node 전체가 bare upload URL로 바뀌고 설명 text는 제거된다. 같은 문법을 문장 안에 두면 일반 link로 바뀐다. 일반 inline link와 reference-style link는 link로 유지되고, video를 가리키는 reference-style image는 첫 upload 전에 거부된다. Markdown node가 아닌 bare local path는 rewrite되지 않은 채 body에 남고 업로드 URL은 끝에 별도로 append된다. 기본 append 흐름을 우선하며 in-place rewrite를 썼다면 게시 후 player가 별도 문단에 저장됐는지 확인한다.

## Draft PR을 먼저 만들고 한 파일씩 첨부한다

`draft` 모드에서는 업로드하지 않는다. 여기서 `draft`는 로컬에서 payload만 준비하는 스킬 모드이며 GitHub의 Draft PR 상태와는 다르다. 사용자가 visual evidence가 포함된 새 PR 게시를 요청했고 final manifest와 body가 확정된 `publish` 모드에서만 GitHub native attachment를 실행한다. 이 승인은 검토한 manifest의 GitHub attachment만 포함하며 외부 storage, 다른 파일 또는 publish 시작 전에 이미 존재하던 PR의 수정으로 확대하지 않는다.

`target_pr_state`와 `required_for_ready`는 publish 전에 확정하고 upload 결과에 따라 낮추지 않는다. 사용자가 명시적으로 요청했거나 PR template·`CONTRIBUTING`이 요구한 파일, 또는 PR이 주장하는 화면 동작을 입증하는 유일한 증거는 필수다. 없어도 PR의 주장과 검증 결과가 완전한 보조 diff, 추가 viewport나 대체 recording만 선택으로 둘 수 있다. 불명확하면 필수로 취급한다. 필수 항목 하나라도 annotation, 실제 content type·MIME·decode, 전체 내용의 민감정보 검사와 embedded metadata 검사를 완료하지 못하면 PR 생성 명령 자체를 실행하지 않는다.

Draft PR을 만들기 전에 전체 manifest의 로컬 파일 identity를 비교한다. realpath, hard link나 symbolic link를 통해 같은 underlying file을 가리키는 항목이 둘 이상이면, 각 파일을 별도 명령으로 올리더라도 중복으로 보고 upload를 시작하지 않는다. 내용 hash만 같은 서로 다른 파일은 자동으로 같은 파일이라고 단정하지 않는다.

미디어가 있는 publish는 다음 순서를 지킨다.

1. multiline body를 임시 파일에 기록한다. 로컬 검토용 attachment placeholder를 실제 caption·순서 설명으로 바꾸거나 제거하여 local path와 placeholder가 없는 final body를 만든 뒤, `--attach` 없이 `gh pr create --draft --body-file ...`를 실행한다.
2. 응답 URL을 다시 읽어 현재 흐름에서 생성한 정확한 PR인지, Draft인지, repository·base·head와 `headRefOid`가 고정한 값과 같은지 확인한다. 실패나 응답 불명확이면 같은 create를 반복하지 않고 같은 head의 PR을 먼저 조회한다.
3. 실행 직전에 한 파일의 size와 SHA-256을 manifest와 다시 대조한다. 달라졌으면 중단한다.
4. 필수 파일부터 manifest 순서대로 `gh pr edit`에 검증한 PR URL과 한 파일의 `--attach` 인자만 전달한다. `--body`나 `--body-file`을 함께 전달하지 않는다.
5. 파일 하나를 추가할 때마다 실제 body를 다시 읽어 고유한 remote URL과 render 형태를 확인하고 `upload_status`를 갱신한다. 다음 파일은 확인이 끝난 뒤에만 처리한다.
6. repository template의 visual section이 body 끝이 아니면 확인한 remote URL을 그 section에 배치한 완성 body를 `gh pr edit --body-file`로 다시 기록한다. body를 재조회하여 append된 중복 URL이 없고 각 attachment가 지정된 위치와 예상한 순서로 렌더링될 때만 `body_status: verified`로 둔다. body 끝이 visual section이면 append 결과의 순서와 render 형태를 확인하여 같은 상태로 둔다.
7. 필수 항목이 모두 `upload_status: uploaded`, `body_status: verified`일 때만 다음 단계로 진행한다. 하나라도 `failed`, `not_attempted`, `missing`, `wrong_render`, `unknown` 또는 `inconclusive`이면 Draft 상태를 유지한다.
8. 원래 요청이 ready PR이면 unresolved local path와 placeholder가 없고 이미지 alt text·marker 설명, 비디오의 caption·순서와 bare URL 단독 문단까지 확인한다. `gh pr ready` 직전에 PR을 다시 읽어 `isDraft: true`, repository, base, head와 `headRefOid`가 manifest에 고정한 값과 같은지 확인한다. `headRefOid`가 달라졌으면 시각 증거를 현재 변경의 증거로 사용하지 않고 Draft 상태를 유지한다. 모두 통과했을 때만 ready로 전환하고, 이후 `isDraft: false`와 같은 `headRefOid`를 다시 확인한다. 원래 요청이 Draft PR이면 전환하지 않는다.

예시는 한 번에 한 파일만 처리한다.

```sh
gh pr edit "https://github.com/OWNER/REPOSITORY/pull/123" \
  --attach '/absolute/path/annotated-after.png#Marker 1 outlines the relocated navigation trigger'
```

같은 publish 흐름에서 방금 만든 Draft PR에는 아직 확인하지 않은 manifest 첨부를 위 방식으로 추가하고 원래 요청한 ready 상태로 전환할 수 있다. title, ticket, reviewer, label과 다른 body 내용은 이 예외로 변경하지 않는다.

`gh pr create --attach`는 `--web`이나 `--dry-run`과 함께 사용할 수 없다. attachment dry-run은 없으므로 첫 upload 전에 모든 로컬 검사를 마친다.

## 실패와 부분 성공을 복구한다

GitHub CLI는 한 명령의 파일을 순서대로 올리고 첫 upload 실패에서 멈춘다. 앞선 성공을 되돌리지 않으며 upload 뒤 PR body update가 실패하면 독립 삭제 endpoint가 없는 orphan attachment가 남을 수 있다. 기본 흐름은 한 명령에 파일 하나만 전달하여 다중 파일의 부분 성공을 피하지만 upload와 body update 자체는 원자적이지 않다.

exit code만 보고 같은 명령을 반복하지 않는다. stdout의 URL, remote branch, 같은 head의 PR과 실제 body를 먼저 조회한다. `upload_status`는 `not_started`, `uploaded`, `failed`, `not_attempted`, `unknown`으로, `body_status`는 `not_checked`, `verified`, `missing`, `wrong_render`, `unknown`으로 구분한다. 서버가 파일을 받지 않았음이 확정된 경우에만 `failed`를 사용하고, timeout·응답 유실·process interruption처럼 upload 여부를 확정할 수 없으면 `unknown`을 사용한다. `not_started`는 아직 정상 순서가 도달하지 않은 상태이고 `not_attempted`는 앞선 실패로 이번 publish 흐름에서 시도하지 않기로 확정한 상태다.

정상 순서에서 `not_started`인 다음 파일만 실행한다. 앞선 실패 뒤 `not_attempted`로 확정한 파일과 `unknown` 파일은 이번 publish 흐름에서 업로드하지 않는다. `failed` 파일도 deterministic validation 오류나 권한 문제의 원인이 해결되고 중복 upload가 없음을 확인하기 전에는 재시도하지 않는다. 필수 파일을 확인할 수 없으면 Draft를 유지한다. 확인할 수 없는 remote URL이나 deletion locator를 만들지 않는다.

## CLI를 쓸 수 없으면 fallback한다

현재 CLI에 `--attach`가 없거나 host, credential 또는 base repository 권한이 CLI attachment를 지원하지 않으면 기존 로그인 session을 사용하는 공식 GitHub browser attachment를 시도한다. final title, body, 마킹된 이미지·비디오와 manifest를 먼저 완성하고 attachment와 제출을 마지막 단계에서 수행한다.

플랫폼이 target repository에서 Draft PR 자체를 지원하지 않는다고 확인되면 `target_pr_state: draft` 요청은 상태를 ready로 바꾸지 않고 중단하여 이유를 보고한다. `target_pr_state: ready`인 경우에만 browser 작성 화면에서 모든 필수 첨부와 final body를 확인한 뒤 ready PR을 생성할 수 있다. CLI의 `--draft` flag나 attachment 기능만 없는 경우와 플랫폼의 Draft PR 미지원을 구분한다.

browser 파일 첨부도 자동 제어할 수 없으면 비공식 upload endpoint를 사용하지 않는다. PR 작성 화면과 미디어 폴더를 준비하여 사용자가 drag-and-drop과 제출만 수행하게 한다. screenshot 포함이 필수이면 미디어가 빠진 non-draft PR을 임의로 만들지 않는다.

## object storage는 명시적인 opt-in이다

R2, S3 또는 다른 object storage는 사용자가 provider를 직접 선택했고 기존 bucket, public base URL, credential, 공개 범위와 key 정책을 확인할 수 있을 때만 사용한다. bucket, public access, custom domain, credential과 lifecycle rule을 만들지 않는다. 기존 object를 overwrite하거나 delete하지 않고, 만료되는 signed GET URL을 PR body에 넣지 않는다.

content-addressed key의 예시는 `<prefix>/<owner-repository>/<head-sha>/<kind>-<sha256>.<ext>`다. 업로드 후 URL, content type, size, hash, 만료 여부, 공개 범위와 deletion locator를 확인한다. `publish-image` 같은 별도 스킬은 사용자가 image용 외부 storage를 선택한 경우의 optional adapter이며 GitHub native attachment나 video upload에는 필요하지 않다.
