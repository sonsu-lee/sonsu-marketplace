# PR 미디어 첨부 규칙

PR에 로컬 이미지나 비디오를 넣어야 할 때 읽는다.

## 로컬 산출물을 준비한다

미디어는 저장소 밖의 `${TMPDIR}/codex-to-pr/<owner-repository>/<head-sha>/` 아래에 둔다. repository의 `docs/assets`, `public`, `static`, `.github/assets`나 source tree에 자동으로 추가하고 commit하지 않는다. 최종 첨부 사본은 제어 문자와 `#`가 없는 생성형 basename을 사용한다.

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

화면과 파일에 secret, token, cookie, 개인정보·개인 email, 고객 정보·실제 고객 data, 내부 URL·hostname, notification과 다른 application의 내용, 제한된 보안 정보와 불필요한 local path가 없는지 확인한다. 안전하게 제거할 수 없으면 업로드하지 않는다. 애니메이션 GIF를 포함한 이미지는 [시각 증거 규칙](visual-evidence.md#첨부-이미지에-마킹한다)에 따라 변경 위치가 마킹된 사본만 첨부한다. GitHub CLI는 이미지를 마킹하지 않으므로 annotation은 upload 전에 반영해야 한다. 비디오는 실제 애플리케이션 동작을 녹화한 자료를 사용한다. 마킹 대신 볼 지점의 caption을 두고 여러 구간 중 특정 시점을 찾아야 할 때만 timestamp를 붙인다. 비디오의 `annotation_status`는 이 caption이 준비됐는지로 판정하며 이미지 마커를 요구하지 않는다.

업로드 전에 신뢰할 수 있는 decoder로 실제 content type, decode 가능 여부와 확장자의 일치를 확인한다. GIF의 모든 frame과 비디오의 전체 영상·audio track을 검토하여 민감정보가 없는지도 확인한다. EXIF·GPS·XMP, SVG metadata와 video container 메타데이터 같은 embedded metadata도 최종 첨부 사본에서 확인한다. 민감하거나 불필요한 metadata가 있으면 정제한 별도 사본을 만들고 다시 검사한다. 전체 내용이나 metadata를 신뢰할 수 있게 검사하지 못하면 각각 `sensitive_data_check` 또는 `embedded_metadata_check`를 `inconclusive`로 기록하고 업로드하지 않는다.

영상이 있으면 크기와 관계없이 `command -v ffmpeg ffprobe`로 검사·인코딩 도구를 확인한다. 이미 제공된 동등 도구로 필요한 검사·변환을 수행할 수 있으면 그것을 사용한다. 도구가 없으면 필요한 이유와 환경별 설치 방법을 제안한다. macOS에 Homebrew가 있으면 `brew install ffmpeg`, 다른 환경에서는 확인된 OS 패키지 관리자의 설치 방법을 안내한다.

캡처·마킹·image library·codec·메타데이터 도구·player에도 같은 원칙을 적용한다. 프로젝트가 지정한 도구가 있으면 그 설치 방법을, 없으면 작업 환경에서 필요한 기능을 제공하는 최소 도구를 제안한다. 설치·업그레이드·`npx --yes` 다운로드를 승인 없이 실행하지 않는다. 설치 제안은 PR 본문 밖에 두고 도구·실행 환경이 없는 상태를 검사나 자료 준비 완료로 보고하지 않는다. 동작 증거가 필수이면 도구 부재를 이유로 스크린샷으로 조용히 대체하지 않는다.

## manifest를 검사한다

[`validate_attachment_manifest.py`](../../../scripts/validate_attachment_manifest.py)는 manifest와 로컬 파일을 읽기만 한다. 파일을 고치거나 upload하지 않고 decoder도 실행하지 않는다. `to-pr` SKILL.md가 있는 실제 디렉터리에서 실행한다.

```bash
../../scripts/validate_attachment_manifest.py --manifest <manifest.json> --phase pre-create [--video-plan unknown|free|paid] [--paid-video-eligible]
../../scripts/validate_attachment_manifest.py --manifest <manifest.json> --phase pre-upload --attachment-order <display_order> [video 옵션]
```

manifest는 UTF-8 JSON object다. 위 operation 필드와 각 `attachments[]` 필드가 모두 있어야 하며, 값이 없을 때는 `null`을 쓴다. 중복 key와 `NaN`·`Infinity`는 입력 오류다.

| 필드 | 값 |
|---|---|
| `repository`, `base`, `head` | 비어 있지 않은 문자열. `repository`는 `owner/repository` |
| `head_ref_oid` | 40자 또는 64자 Git object ID |
| `pr_url` | `pre-create`는 `null`, `pre-upload`는 같은 `repository`의 `https://<host>/<owner>/<repository>/pull/<number>` |
| `target_pr_state` | `draft` 또는 `ready` |
| `source_path`, `local_path` | 제어 문자가 없는 절대 경로. `local_path` basename에는 `#`가 없다 |
| `purpose`, `body_section`, `alt_text_or_caption` | 비어 있지 않은 문자열 |
| `display_order`, `file_size`, `width`, `height` | 양의 정수. `display_order`는 manifest 안에서 고유하다 |
| `required_for_ready` | boolean |
| `kind`, `mime_type` | 확장자와 일치하는 쌍: `.png` `image/png`, `.jpg`·`.jpeg` `image/jpeg`, `.gif` `image/gif`, `.webp` `image/webp`, `.svg` `image/svg+xml`, `.mp4` `video/mp4`, `.mov` `video/quicktime`, `.webm` `video/webm` |
| `duration`, `codec` | video는 양수 초와 decoder가 보고한 codec. image는 `null` 또는 같은 형식의 값 |
| `sha256` | 64자 hex |
| `annotation_status` | `not_checked`, `verified`, `failed`, `inconclusive` |
| `annotation_method` | 마킹 또는 caption 방법 문자열, 아직 없으면 `null` |
| `sensitive_data_check`, `embedded_metadata_check` | `not_checked`, `passed`, `failed`, `inconclusive` |
| `upload_status`, `body_status` | [실패와 부분 성공](#실패와-부분-성공을-복구한다)의 상태 값 |
| `provider`, `deletion_locator` | 문자열 또는 `null` |
| `remote_url` | HTTPS URL 또는 `null` |

도구가 판정하는 항목은 다음과 같다.

- 필수 필드, 형식, 확장자 기준의 `kind`·`mime_type` 일치
- `local_path`가 symbolic link를 따라간 결과로 존재하는 비어 있지 않은 regular file인지
- 실제 크기와 `file_size`, 실제 SHA-256과 `sha256`의 일치. hash 중 파일이 바뀌면 실패한다.
- 크기 상한: image는 `10 × 1024²` bytes. video는 `unknown`·`free` plan과 eligibility 미확인 `paid`가 10,000,000 bytes, `--video-plan paid --paid-video-eligible`이 100,000,000 bytes다. 둘 다 CLI의 `100 × 1024²` bytes 상한 안이다.
- 경로가 달라도 device와 inode가 같으면 `duplicate-file`이다. symbolic link, hard link와 같은 경로 반복이 여기에 해당한다. 내용만 같은 서로 다른 파일은 통과한다.
- `pre-create`: `pr_url`이 `null`이고 모든 항목이 `upload_status: not_started`, `body_status: not_checked`, `remote_url`·`deletion_locator: null`인지. 필수 항목은 기록된 `annotation_status: verified`, `annotation_method`, `sensitive_data_check: passed`, `embedded_metadata_check: passed`가 있어야 한다. 모든 파일을 hash한다.
- `pre-upload`: `pr_url`이 같은 저장소의 PR이고, `--attachment-order`로 지정한 항목이 `not_started`이며 기록된 검토 상태를 통과했는지. upload 순서는 `required_for_ready: true` 항목을 먼저, 같은 그룹 안에서는 `display_order` 순으로 정하며 지정 항목보다 앞선 항목은 모두 `uploaded`여야 한다. 모든 파일의 identity·크기를 다시 보고, 지정한 파일만 hash한다.

`--paid-video-eligible`은 paid plan과 [GitHub의 큰 비디오 조건](#github-cli-지원을-감지한다)을 사람이 확인한 뒤에만 붙인다.

출력은 `schema_version`, `phase`, `status`, `errors`, `checked_files`, `manual_checks`를 담은 JSON이다. `errors[]`는 `field`, `code`, `message`를 갖는다. `checked_files[]`는 `field`, `display_order`, `realpath`, `device`, `inode`, `file_size`, `limit_bytes`, `sha256`을 갖고, hash하지 않은 파일의 `sha256`은 `null`이다.

| exit | `status` | 행동 |
|---|---|---|
| 0 | `passed` | 로컬 판정만 통과했다. `manual_checks`의 decoder·내용·권한·원격 재조회를 마친 뒤 다음 단계로 간다. |
| 1 | `blocked` | `errors`를 고치고 영향받은 manifest 필드를 다시 기록한 뒤 같은 phase를 다시 실행한다. 그 전에는 PR 생성이나 upload를 하지 않는다. |
| 2 | `input-error` 또는 출력 없음 | manifest나 CLI 인자를 고친다. 출력이 없으면 stderr의 argparse 오류다. |

exit 0도 실제 content type, decode·재생 가능 여부, annotation 품질, 민감정보와 embedded metadata가 안전하다는 뜻이 아니다. 도구는 확장자와 사람이 기록한 검토 상태만 대조한다. decoder 결과와 내용 검토는 위 규칙대로 직접 수행하고 그 결과를 manifest에 기록한다.

## GitHub CLI 지원을 감지한다

GitHub native attachment를 기본으로 사용한다. 실행 직전에 `gh --version`, `gh pr create --help`, `gh pr edit --help`와 `gh pr ready --help`를 확인하고, 실제로 사용할 명령의 도움말에 필요한 flag가 있을 때만 CLI attachment를 사용한다. `--attach`는 GitHub CLI `2.99.0`에서 추가됐지만 배포판의 backport나 지연을 고려하여 help output을 최종 기준으로 삼는다. 현재 CLI가 지원하지 않아도 자동으로 설치하거나 upgrade하지 않는다.

지원되는 CLI에서는 다음 계약을 지킨다.

- image: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, 파일당 최대 `10 × 1024²` bytes
- video: `.mp4`, `.mov`, `.webm`; Free plan의 server 제한은 10 MB, paid plan은 100 MB이며 CLI의 로컬 상한은 `100 × 1024²` bytes
- 파일 확장자는 대소문자를 구분하지 않으며 실제 bytes나 codec이 아니라 확장자로 유형을 판정한다.
- 한 명령에는 최대 50개의 서로 다른 regular file만 허용한다. 빈 파일, directory, named pipe, stdin `-`, 없는 경로와 같은 파일을 가리키는 중복 경로는 허용하지 않는다.
- GitHub.com과 GitHub Enterprise Cloud with data residency를 지원하고 GitHub Enterprise Server는 지원하지 않는다.
- OAuth, classic PAT와 fine-grained PAT를 사용할 수 있다. GitHub App token과 확인할 수 없는 token 유형은 지원하지 않는다. 대상 base repository에 `WRITE`, `MAINTAIN` 또는 `ADMIN` 권한이 필요하므로 base에 write 권한이 없는 fork contributor에게는 CLI attachment를 사용하지 않는다.

video plan이나 저장소 소유자의 plan을 확인하지 못하면 10 MB를 안전한 상한으로 사용한다. paid plan에서 10 MB를 넘는 비디오는 GitHub가 요구하는 organization member, outside collaborator 또는 paid-plan 사용자 조건도 확인한다. GitHub가 권장하는 H.264처럼 실제 reviewer 환경에서 재생 가능한 codec인지도 확인한다. token scope가 충분한지 추측하거나 scope 확대, 로그인과 계정 전환을 자동으로 수행하지 않는다.

파일은 repository나 임의 object storage에 넣지 않고 GitHub user attachment storage에 올라간다. public repository의 첨부는 인증 없이 접근될 수 있고 private·internal repository의 첨부는 저장소 접근 권한을 따른다. 업로드 전에 PR visibility와 media 공개 범위가 맞는지 확인한다.

GitHub Draft PR의 가용성은 저장소 visibility와 plan에 따라 다르다. 계정명이나 visibility만으로 지원을 단정하지 않고, 미디어를 올리기 전에 attachment 없는 Draft PR 생성으로 실제 지원 여부와 정확한 대상 PR을 확인한다.

공식 참고: [GitHub CLI 파일 첨부](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli), [`gh pr edit`](https://cli.github.com/manual/gh_pr_edit), [GitHub 첨부 형식과 크기](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files), [Draft PR 가용성](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request), [GitHub CLI 2.99.0](https://github.com/cli/cli/releases/tag/v2.99.0)

## 크기 제한을 넘으면 압축한다

최종 첨부 사본이 위에서 정한 상한을 넘으면 첨부를 포기하지 않고 압축한 사본을 만든다. 플랜을 확인하지 못한 영상의 상한은 10 MB다. 원본은 `source_path`에 남기고, 같은 manifest 항목의 `local_path`·`mime_type`·`file_size`·`width`·`height`·`codec`·`duration`·`sha256`을 압축 사본 기준으로 갱신한다. 영상을 단계별로 나눌 때만 새 항목을 만든다.

1. 영상은 변경을 보여 주는 구간만 남긴다. 판단과 무관한 앞뒤 대기만 자르고, 변경의 핵심인 로딩·전환 타이밍은 보존한다.
2. `ffmpeg`로 H.264로 다시 인코딩한다. 음성이 변경 설명에 필요할 때만 `-an` 대신 `-map '0:a:0?' -c:a aac -b:a 96k`를 쓴다.

   ```sh
   ffmpeg -i input.mov -map 0:v:0 -map_metadata -1 -an \
     -vf "scale='trunc(min(1280,iw)/2)*2':-2,fps=30" \
     -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -movflags +faststart output.mp4
   ```

   여전히 크면 CRF를 2씩 올리되 32를 넘기지 않는다. 그다음 너비 960px, 15fps 순으로 낮춘다. 길이가 길어 이 방법으로 맞추기 어려우면 `목표 영상 kbps = 상한 bytes × 8 × 0.9 ÷ 길이(초) ÷ 1000 − 음성 kbps`로 2-pass bitrate 인코딩을 한다.
3. 사용자가 설치를 원하지 않으면 macOS에서는 `avconvert --source input.mov --output output.mov --start <초> --duration <초> --preset Preset1280x720`으로 구간 자르기와 해상도 낮추기만 시도한다. bitrate를 지정할 수 없어 상한 안에 들어온다는 보장이 없고, `PresetMediumQuality` 이하는 568×320 수준으로 줄어 UI 글자를 읽기 어렵다. 아래 재검사를 할 도구가 없으면 결과는 `inconclusive`이며 업로드하지 않는다.
4. 이미지는 긴 변을 2560px 이하로 줄인다. macOS에서는 `sips -Z 2560`을 쓸 수 있다. 그래도 크면 사진성 화면만 JPEG 품질 85로 바꾸고, 글자 중심 UI는 PNG를 유지한다.

압축 사본은 다시 검사한다. 크기가 상한 이하이고 영상이 H.264(`avc1`)·`yuv420p`로 decode되며 길이가 의도한 구간과 맞아야 한다. 영상은 caption이 가리키는 볼 지점의 대표 프레임을 직접 열어 UI 글자를 읽을 수 있는지 확인한다. timestamp가 있으면 그 시점도 대조하며, 없다고 판독 검사를 생략하거나 timestamp를 새로 강제하지 않는다. 이미지는 marker와 변경부가 읽히는지 확인한다. 민감정보·embedded metadata 검사와 SHA-256 기록도 새 사본 기준으로 다시 한다.

읽을 수 있는 품질로 상한을 맞추기 어려우면 동작을 보존하는 짧은 클립으로 나눈다. 그것도 불가하면 미완료와 필요한 조건을 본문 밖에 알린다. 이미지로 같은 판단을 할 수 있는 정적 변경만 마킹 스크린샷으로 대체하며, 동작 증거가 필수인 경우 용량 문제로 정적 이미지 대체 완료를 주장하지 않는다.

## 기본 흐름에서는 로컬 경로를 body에 노출하지 않는다

GitHub CLI는 body가 같은 로컬 파일을 참조하면 그 위치의 destination을 upload URL로 바꿀 수 있다. 하지만 여러 upload 중 일부만 성공해도 PR을 생성하므로 실패한 파일의 local path가 body에 남을 수 있다. `to-pr`의 기본 흐름에서는 local reference를 body에 쓰지 않는다.

대신 각 이미지의 marker와 영상에서 볼 지점을 설명한다. 외부 양식의 지정 위치를 우선하며 기본형은 해당 설명 바로 뒤, 여러 자료를 구분할 때만 화면 자료 묶음에 둔다. body가 참조하지 않은 attachment는 flag 순서대로 끝에 추가되므로 manifest의 `display_order`와 `--attach` 순서를 일치시킨다. 여러 파일이면 설명에도 `Attachment 1`, `Video 3`처럼 같은 번호를 붙여 파일과 caption을 대응시킨다.

첨부 후 아래 게시 절차에 따라 확인된 URL을 계획한 설명 뒤나 지정 항목에 배치하고, 본문 끝의 중복 attachment와 local placeholder가 제거됐는지 재조회한다.

이미지 인자는 shell 해석을 피하도록 전체를 quote하고 `--attach '/absolute/path/annotated-after.png#Marker 1 shows the changed navigation state'`처럼 alt text를 붙인다. 비디오는 alt text를 지원하지 않으므로 `#` 뒤의 설명을 주지 않는다. 비디오는 append되면 bare URL로 기록되어 player로 표시된다.

공식 CLI가 지원하는 in-place rewrite를 사용자가 특별히 요청하면 상대 경로가 본문 file이 아니라 `gh` 실행 directory 기준임을 확인한다. 부분 실패 때 공개되어도 안전한 경로만 사용하고 절대 home path는 body에 넣지 않는다. 이미지의 본문 reference에 이미 alt text가 있으면 `--attach` 인자보다 body의 alt text가 우선한다.

비디오를 in-place player로 배치하려면 inline-style image 문법인 `![설명](./clip.mp4)`가 해당 문단의 유일한 내용이어야 한다. 이때 image node 전체가 bare upload URL로 바뀌고 설명 text는 제거된다. 같은 문법을 문장 안에 두면 일반 link로 바뀐다. 일반 inline link와 reference-style link는 link로 유지되고, video를 가리키는 reference-style image는 첫 upload 전에 거부된다. Markdown node가 아닌 bare local path는 rewrite되지 않은 채 body에 남고 업로드 URL은 끝에 별도로 append된다. 기본 append 흐름을 우선하며 in-place rewrite를 썼다면 게시 후 player가 별도 문단에 저장됐는지 확인한다.

## Draft PR을 먼저 만들고 한 파일씩 첨부한다

`draft` 모드에서는 업로드하지 않는다. 사용자가 visual evidence가 포함된 새 PR 게시를 요청했고 final manifest와 body가 확정된 `publish` 모드에서만 GitHub native attachment를 실행한다. 이 승인은 검토한 manifest의 GitHub attachment만 포함하며 외부 storage, 다른 파일 또는 publish 시작 전에 이미 존재하던 PR의 수정으로 확대하지 않는다.

`target_pr_state`는 기본 Draft 정책과 GitHub 규칙에 따라 publish 전에 확정하고 upload 결과에 따라 바꾸지 않는다. `required_for_ready`도 사전에 확정한다. 사용자·PR 양식·`CONTRIBUTING`이 요구한 파일과 [필요 정보에 따라 선택한](visual-evidence.md#필요성을-판정한다) 화면 증거는 필수다. 정적 변경은 마킹 이미지, 동적 변경은 caption 영상, 서로 다른 정보가 필요할 때만 둘 다 선택한다. 접근 가능한 VRT가 있어도 본문 증거를 생략하지 않는다. 주장을 판단하는 데 없어도 되는 보조 diff·추가 viewport·대체 recording만 선택으로 둘 수 있으며 불명확하면 필수로 취급한다. 필수 항목 하나라도 annotation, 실제 content type·MIME·decode, 전체 내용의 민감정보 검사와 embedded 메타데이터 검사를 완료하지 못하면 PR 생성 명령 자체를 실행하지 않는다.

Draft PR을 만들기 전에 전체 manifest의 로컬 파일 identity를 비교한다. realpath, hard link나 symbolic link를 통해 같은 underlying file을 가리키는 항목이 둘 이상이면, 각 파일을 별도 명령으로 올리더라도 중복으로 보고 upload를 시작하지 않는다. 내용 hash만 같은 서로 다른 파일은 자동으로 같은 파일이라고 단정하지 않는다. 이 비교와 필수 항목의 기록 상태 확인은 [manifest 검사](#manifest를-검사한다)를 `--phase pre-create`로 실행해 수행하며, exit 0일 때만 다음 순서를 시작한다.

미디어가 있는 publish는 다음 순서를 지킨다.

1. multiline body를 임시 파일에 기록한다. 로컬 검토용 attachment placeholder를 실제 caption·순서 설명으로 바꾸거나 제거하여 local path와 placeholder가 없는 final body를 만든 뒤, `--attach` 없이 `gh pr create --draft --body-file ...`를 실행한다.
2. 응답 URL을 다시 읽어 현재 흐름에서 생성한 정확한 PR인지, Draft인지, 저장소·base·head와 `headRefOid`가 고정한 값과 같은지 확인한다. 실패나 응답 불명확이면 같은 create를 반복하지 않고 같은 head의 PR을 먼저 조회한다.
3. 실행 직전에 [manifest 검사](#manifest를-검사한다)를 `--phase pre-upload --attachment-order <display_order>`로 실행하여 한 파일의 size와 SHA-256을 manifest와 다시 대조하고 identity와 순서를 확인한다. exit 0이 아니거나 파일이 달라졌으면 중단한다.
4. 필수 파일부터 manifest 순서대로 `gh pr edit`에 검증한 PR URL과 한 파일의 `--attach` 인자만 전달한다. `--body`나 `--body-file`을 함께 전달하지 않는다.
5. 파일 하나를 추가할 때마다 실제 body를 다시 읽어 고유한 remote URL과 render 형태를 확인하고 `upload_status`를 갱신한다. 다음 파일은 확인이 끝난 뒤에만 처리한다.
6. 계획한 첨부 위치가 본문 끝이 아니면 확인된 URL을 해당 설명 뒤 또는 외부 양식의 지정 항목에 배치한 body를 `gh pr edit --body-file`로 기록한다. 재조회하여 append된 중복 URL이 없고 각 attachment가 계획한 위치·순서로 렌더링될 때만 `body_status: verified`로 둔다. 원래 위치가 본문 끝이면 append 결과의 순서·render 형태를 확인해 같은 상태로 둔다.
7. 필수 항목이 모두 `upload_status: uploaded`, `body_status: verified`일 때만 다음 단계로 진행한다. 하나라도 `failed`, `not_attempted`, `missing`, `wrong_render`, `unknown` 또는 `inconclusive`이면 Draft 상태를 유지한다.
8. 사용자가 ready PR을 명시한 경우에만 unresolved local path와 placeholder가 없고 이미지 alt text·marker 설명, 비디오의 caption·순서와 bare URL 단독 문단까지 확인한다. native stack의 층이라면 [stack 연결 검증](stacked-prs.md#native-stack으로-게시하고-검증한다)까지 끝난 뒤 전환한다. `gh pr ready` 직전에 PR을 다시 읽어 `isDraft: true`, 저장소, base, head와 `headRefOid`가 manifest에 고정한 값과 같은지 확인한다. `headRefOid`가 달라졌으면 시각 증거를 현재 변경의 증거로 사용하지 않고 Draft 상태를 유지한다. 모두 통과했을 때만 ready로 전환하고, 이후 `isDraft: false`와 같은 `headRefOid`를 다시 확인한다. 상태 미지정 또는 Draft 요청이면 전환하지 않는다.

예시는 한 번에 한 파일만 처리한다.

```sh
gh pr edit "https://github.com/OWNER/REPOSITORY/pull/123" \
  --attach '/absolute/path/annotated-after.png#Marker 1 outlines the relocated navigation trigger'
```

`gh pr create --attach`는 `--web`이나 `--dry-run`과 함께 사용할 수 없다. attachment dry-run은 없으므로 첫 upload 전에 모든 로컬 검사를 마친다.

## 실패와 부분 성공을 복구한다

GitHub CLI는 한 명령의 파일을 순서대로 올리고 첫 upload 실패에서 멈춘다. 앞선 성공을 되돌리지 않으며 upload 뒤 PR 본문 update가 실패하면 독립 삭제 endpoint가 없는 orphan attachment가 남을 수 있다. 기본 흐름은 한 명령에 파일 하나만 전달하여 다중 파일의 부분 성공을 피하지만 upload와 본문 update 자체는 원자적이지 않다.

exit code만 보고 같은 명령을 반복하지 않는다. stdout의 URL, remote branch, 같은 head의 PR과 실제 body를 먼저 조회한다. `upload_status`는 `not_started`, `uploaded`, `failed`, `not_attempted`, `unknown`으로, `body_status`는 `not_checked`, `verified`, `missing`, `wrong_render`, `unknown`으로 구분한다. 서버가 파일을 받지 않았음이 확정된 경우에만 `failed`를 사용하고, timeout·응답 유실·process interruption처럼 upload 여부를 확정할 수 없으면 `unknown`을 사용한다. `not_started`는 아직 정상 순서가 도달하지 않은 상태이고 `not_attempted`는 앞선 실패로 이번 publish 흐름에서 시도하지 않기로 확정한 상태다.

정상 순서에서 `not_started`인 다음 파일만 실행한다. 앞선 실패 뒤 `not_attempted`로 확정한 파일과 `unknown` 파일은 이번 publish 흐름에서 업로드하지 않는다. `failed` 파일도 deterministic 검증 오류나 권한 문제의 원인이 해결되고 중복 upload가 없음을 확인하기 전에는 재시도하지 않는다. 필수 파일을 확인할 수 없으면 Draft를 유지한다. 확인할 수 없는 remote URL이나 deletion locator를 만들지 않는다.

## CLI를 쓸 수 없으면 fallback한다

현재 CLI에 `--attach`가 없거나 host, credential 또는 base 저장소 권한이 CLI attachment를 지원하지 않으면 기존 로그인 session을 사용하는 공식 GitHub 브라우저 attachment를 시도한다. final 제목, 본문, 마킹된 이미지·비디오와 manifest를 먼저 완성하고 attachment와 제출을 마지막 단계에서 수행한다.

플랫폼이 target repository에서 Draft PR 자체를 지원하지 않는다고 확인되면 `target_pr_state: draft` 요청은 상태를 ready로 바꾸지 않고 중단하여 이유를 보고한다. `target_pr_state: ready`인 경우에만 브라우저 작성 화면에서 모든 필수 첨부와 final body를 확인한 뒤 ready PR을 생성할 수 있다. CLI의 `--draft` flag나 attachment 기능만 없는 경우와 플랫폼의 Draft PR 미지원을 구분한다.

브라우저 파일 첨부도 자동 제어할 수 없으면 비공식 upload endpoint를 사용하지 않는다. PR 작성 화면과 미디어 폴더를 준비하여 사용자가 drag-and-drop과 제출만 수행하게 한다. 스크린샷 포함이 필수이면 미디어가 빠진 non-draft PR을 임의로 만들지 않는다.

## object storage는 명시적인 opt-in이다

R2, S3 또는 다른 object storage는 사용자가 provider를 직접 선택했고 기존 bucket, public base URL, credential, 공개 범위와 key 정책을 확인할 수 있을 때만 사용한다. bucket, public access, custom domain, credential과 lifecycle rule을 만들지 않는다. 기존 object를 overwrite하거나 delete하지 않고, 만료되는 signed GET URL을 PR body에 넣지 않는다.

content-addressed key의 예시는 `<prefix>/<owner-repository>/<head-sha>/<kind>-<sha256>.<ext>`다. 업로드 후 URL, content type, size, hash, 만료 여부, 공개 범위와 deletion locator를 확인한다. `publish-image` 같은 별도 스킬은 사용자가 image용 외부 storage를 선택한 경우의 optional adapter이며 GitHub native attachment나 video upload에는 필요하지 않다.
