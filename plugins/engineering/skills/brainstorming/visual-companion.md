# 시각 보조 도구 사용 안내

브라우저에서 화면 시안·배치·시각 비교를 보여 주는 도구다. 질문마다 직접 보는 편이 더 명확한지 판단한다. UI 배치·색·간격은 브라우저, 요구사항·개념 선택·장단점·기술 결정은 대화에서 다룬다. 사용자의 기존 선택을 따르고 처음 사용할 때만 필요한 동의를 확인한다.

## 동작 방식

서버는 `screen_dir`의 HTML 파일을 감시해 가장 최근 파일을 보여 준다. 사용자의 선택은 `state_dir/events`에 JSON Lines로 기록된다.

기본적으로 본문 HTML 조각을 작성한다. 서버가 머리말·CSS·연결 상태·상호작용 기능을 제공하는 화면 틀으로 감싼다. `<!DOCTYPE` 또는 `<html`로 시작하면 완전한 문서로 전달하며 보조 스크립트만 삽입한다. 전체 페이지 제어가 필요할 때만 완전한 문서를 사용한다.

## 세션 시작

이 스킬 디렉터리에서 다음을 실행한다.

```bash
scripts/start-server.sh --project-dir /path/to/project --open
```

반환 형식은 다음과 같다.

```json
{"type":"server-started","port":52341,"url":"http://localhost:52341/?key=ab12…","screen_dir":"/path/to/project/.engineering/brainstorm/12345-1706000000/content","state_dir":"/path/to/project/.engineering/brainstorm/12345-1706000000/state"}
```

`screen_dir`·`state_dir`·전체 `url`을 보존한다. `--open`이면 첫 화면을 작성할 때 브라우저를 연다. 화면 없는·원격 실행 환경의 대안으로 URL도 제공한다. `?key=…`는 HTTP·WebSocket 접근에 필요하므로 반환한 쿼리 문자열을 포함한다. 첫 접속 뒤 쿠키가 키를 보존해 새로고침과 `/files/*` 요청에 사용된다.

표준 출력을 놓쳤으면 `$STATE_DIR/server-info`를 읽는다. `--project-dir` 사용 시 `<project>/.engineering/brainstorm/`에 세션이 남는다. 프로젝트 루트를 지정하면 화면과 같은 포트를 재시작에 사용할 수 있다. 지정하지 않은 임시 세션은 `/tmp`에 생성되며 정리될 수 있다. `.engineering/`은 저장소 관례나 로컬 제외 규칙으로 Git에서 제외한다.

### 플랫폼별 실행

| 환경 | 실행 방법 |
| --- | --- |
| Claude Code | 위 기본 명령을 사용한다. 스크립트가 백그라운드를 처리한다. Windows는 포그라운드로 전환되므로 셸 도구의 `run_in_background: true`를 사용하고 다음 턴에 `server-info`를 읽는다. |
| Codex | 위 기본 명령을 사용한다. 실행기는 `CODEX_CI`에서 포그라운드로 전환하며 실제 실행 환경의 지속 실행 방식을 따른다. |
| Gemini CLI | `--foreground`와 셸 도구의 `is_background: true`를 사용한다. |
| Copilot CLI | `bash scripts/start-server.sh --project-dir /path/to/project --open --foreground`를 지속 실행 가능한 셸 기능으로 시작한다. Windows는 Git Bash의 `bash.exe`를 사용할 수 있다. |
| 기타 | 분리된 프로세스를 종료하는 환경이면 `--foreground`와 플랫폼의 백그라운드 실행 기능을 조합한다. |

원격 환경·컨테이너에서 루프백 URL에 접속할 수 없으면 필요한 호스트와 사용자에게 표시할 URL 호스트를 지정한다.

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

`--url-host`는 반환 JSON의 호스트 이름을 정한다. 환경에 필요한 노출 범위를 확인하고 전체 키 URL을 사용한다.

## 화면과 피드백 처리

1. URL을 안내하거나 화면을 쓰기 전에 `$STATE_DIR/server-info`가 있고 `server-stopped`가 없는지 확인한다. 종료됐으면 같은 `--project-dir`로 재시작한다. 같은 포트를 재사용하며 기존 탭이 다시 연결된다. 기본 유휴 종료는 4시간이고 `--idle-timeout-minutes`로 조정한다.
2. `screen_dir`에 의미가 있는 새 파일을 작성한다. 예: `layout.html`, `layout-v2.html`. 수정 시각이 가장 최근인 파일을 제공하므로 화면마다 고유 이름을 사용한다.
3. 실제 화면 내용과 전체 URL을 짧게 안내한다. 선택이 필요한 단계에서는 사용자의 피드백을 받는다.
4. 다음 턴에 `state_dir/events`가 있으면 읽고 대화 응답과 함께 해석한다. 대화의 명시적인 응답이 우선하며 클릭은 보조 근거다. 이벤트가 없으면 대화 내용만 사용한다.
5. 피드백에 따라 새 버전을 작성하거나 다음 단계로 진행한다. 대화로 돌아갈 때에는 새 대기 화면으로 이전 선택지를 지운다.

```html
<!-- waiting.html; 다음 대기 화면은 waiting-2.html처럼 새 이름을 사용한다. -->
<div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
  <p class="subtitle">대화에서 계속 진행합니다.</p>
</div>
```

## HTML 조각 예시

```html
<h2>어느 배치가 더 읽기 편한가요?</h2>
<p class="subtitle">정보 순서와 시각적 계층을 비교합니다.</p>
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content"><h3>한 열</h3><p>내용을 순서대로 읽는 배치</p></div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content"><h3>두 열</h3><p>탐색 영역과 본문을 나눈 배치</p></div>
  </div>
</div>
```

화면 틀이 제공하는 기능을 사용하면 별도 `<html>`·CSS·스크립트 없이 선택 화면을 만들 수 있다.

## 제공되는 CSS와 상호작용

| 구조·클래스 | 용도 |
| --- | --- |
| `.options` 안 `.option` | A/B/C 선택지. `data-choice`와 `onclick="toggleSelect(this)"`를 지정한다. |
| `.options[data-multiselect]` | 여러 선택지를 독립적으로 선택·해제한다. |
| `.letter`, `.content` | 선택지 문자와 본문 |
| `.cards` 안 `.card` | 시각적 선택지. `.card-image`와 `.card-body`로 나누고 선택 속성을 지정한다. |
| `.mockup`, `.mockup-header`, `.mockup-body` | 미리보기 틀과 제목·본문 |
| `.split` | 두 화면 시안을 나란히 배치한다. |
| `.pros-cons` 안 `.pros`, `.cons` | 장점·단점 비교 |
| `.mock-nav`, `.mock-sidebar`, `.mock-content` | 와이어프레임 탐색·측면 영역·본문 |
| `.mock-button`, `.mock-input`, `.placeholder` | 버튼·입력·미정 영역 |
| `h2`, `h3`, `.subtitle`, `.section`, `.label` | 페이지 제목·섹션 제목·보조 설명·섹션·작은 라벨 |

시각 비교 예시의 카드도 `data-choice="design1"`와 `onclick="toggleSelect(this)"`를 사용한다. 다중 선택은 컨테이너에 `data-multiselect`를 추가한다.

## 브라우저 이벤트 형식

새 화면을 작성하면 이벤트 파일이 초기화된다. 각 클릭은 다음 형태다.

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

여러 클릭은 탐색 과정일 수 있다. 마지막 선택만으로 사용자 계약을 확정하지 않고 명시적인 대화 응답과 대조한다.

## 표현과 종료

질문에 맞는 충실도를 고른다. 배치는 와이어프레임, 시각 완성도는 필요한 실제 색·간격·내용으로 비교한다. 각 화면의 판단 기준을 밝히고 2~4개 선택지에 집중한다. 중요한 실제 내용은 자리표시자로 가리지 않으며 다음 단계 전에 관련 피드백을 반영한다.

종료할 때 해당 세션만 지정한다.

```bash
scripts/stop-server.sh "$SESSION_DIR"
```

`--project-dir` 세션의 화면은 `.engineering/brainstorm/`에 보존된다. `/tmp` 세션은 종료 시 삭제된다.

- CSS 정본: [frame-template.html](scripts/frame-template.html)
- 클라이언트 helper: [helper.js](scripts/helper.js)
