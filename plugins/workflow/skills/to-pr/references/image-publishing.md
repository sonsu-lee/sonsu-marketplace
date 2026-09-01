# PR 이미지 게시 규칙

PR에 screenshot이나 visual diff를 넣어야 할 때 읽는다.

## 로컬 산출물을 준비한다

이미지는 repository 밖의 `${TMPDIR}/codex-to-pr/<owner-repository>/<head-sha>/` 아래에 둔다. repository의 `docs/assets`, `public`, `static`, `.github/assets`나 source tree에 자동으로 추가하고 commit하지 않는다.

각 이미지에 다음 manifest 정보를 기록한다.

```text
local_path
purpose
body_section
display_order
alt_text
mime_type
file_size
width
height
sha256
sensitive_data_check
upload_status
provider
remote_url
deletion_locator
```

secret, token, cookie, 개인정보, 실제 고객 data, 내부 URL, 제한된 보안 정보와 불필요한 local path가 보이면 게시하지 않는다.

## GitHub native attachment를 기본으로 한다

별도 provider 설정이 없는 GitHub PR은 GitHub native attachment를 사용한다. 사용 가능한 credential이나 connector만 보고 R2, S3, Gist, 임의 image host 또는 repository asset을 선택하지 않는다.

public repository의 첨부는 인증 없이 접근될 수 있고, private·internal repository의 첨부는 repository 접근 권한을 따른다. 이미지 공개 범위가 PR과 맞는지 확인한다.

GitHub가 지원하는 PNG, GIF, JPEG 또는 SVG 형식을 사용하고 이미지·GIF 한 개가 10MB를 넘지 않는지 확인한다. 제한을 넘으면 설치되어 있는 안전한 도구로만 크기를 줄이거나 업로드를 중단하고 정확한 이유를 보고한다.

공식 참고: [GitHub 파일 첨부](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)

## browser로 자동 첨부한다

사용 가능한 GitHub browser 제어 기능과 기존 로그인 session이 있으면 관련 browser skill을 먼저 읽고 다음 순서로 진행한다.

1. final title, body, base, head, ticket link와 validation을 완성한다.
2. 이미지 manifest와 민감정보 검사를 완료한다.
3. 정확한 GitHub PR 작성 화면을 연다.
4. title과 body를 입력하고 `Visual evidence` 위치에 이미지를 첨부한다.
5. GitHub가 만든 Markdown URL, alt text와 순서를 확인한다.
6. 그 후에만 PR을 제출한다.
7. 저장된 PR body와 이미지 접근을 다시 확인한다.

파일을 작성란에 넣는 순간 업로드될 수 있으므로 attachment는 PR 준비의 마지막 단계다. 업로드 후 PR 생성이 실패하면 URL, PR 미생성, orphan 가능성과 확인 가능한 삭제 경로를 보고한다. GitHub native attachment에는 독립적인 deletion locator가 없을 수 있으므로 값을 만들지 않는다. 원격 상태를 확인하지 않고 같은 파일을 다시 올리지 않는다.

새 browser plugin 설치, 로그인, 로그아웃, 계정 전환과 credential 입력은 자동으로 하지 않는다.

## 자동 첨부가 없으면 마지막 조작만 넘긴다

공식적으로 지원되는 browser 파일 첨부를 자동 제어할 수 없으면 비공식 GitHub upload endpoint를 사용하지 않는다. 대신 다음을 모두 준비한다.

- final PR title과 body
- attachment placeholder
- 업로드할 이미지와 manifest
- 이미지별 alt text와 순서
- 정확한 base와 head

가능하면 현재 공식 CLI의 web 흐름으로 정확한 base와 head의 PR 작성 화면을 열고 운영체제의 파일 탐색기로 이미지 폴더도 연다. 현재 CLI가 title과 body prefill을 지원하면 final payload를 미리 채운다. 사용자가 repository 구조, Markdown과 이미지 hosting을 몰라도 되도록 한 번의 구체적인 안내만 남긴다.

```text
GitHub PR 작성 화면과 첨부 이미지 폴더를 열었습니다.
after.png와 diff.png를 Visual evidence 위치에 순서대로 끌어놓고
Create pull request를 누르세요.
```

screenshot 포함이 필수이면 이미지가 빠진 non-draft PR을 임의로 만들지 않는다. 모든 자동 준비를 끝낸 뒤 drag-and-drop과 제출 단계에서만 멈춘다.

## object storage는 명시적인 opt-in이다

R2, S3 또는 다른 object storage는 사용자가 provider를 직접 선택했고 기존 bucket, public base URL, credential, 공개 범위와 key 정책을 확인할 수 있을 때만 사용한다. bucket, public access, custom domain, credential과 lifecycle rule을 만들지 않는다. 기존 object를 overwrite하거나 delete하지 않고, 만료되는 signed GET URL을 PR body에 넣지 않는다.

content-addressed key의 예시는 `<prefix>/<owner-repository>/<head-sha>/<kind>-<sha256>.png`다. 업로드 후 URL, content type, size, hash, 만료 여부, 공개 범위와 deletion locator를 확인한다.

`publish-image` 같은 별도 스킬은 사용자가 외부 storage를 선택한 경우의 optional adapter다. GitHub native attachment에 필수로 요구하지 않는다.
