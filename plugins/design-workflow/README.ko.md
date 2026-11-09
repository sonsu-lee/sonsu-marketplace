# design-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

범위가 정해진 근거와 선택적 omp 검증 하네스를 사용해 인터페이스와 그래픽을
디자인하고 검토한다.

## 목차

- [설치](#설치)
  - [의존성](#의존성)
- [사용법](#사용법)
  - [이식 가능한 스킬](#이식-가능한-스킬)
  - [관련 스킬](#관련-스킬)
  - [omp 엄격 실행 시작](#omp-엄격-실행-시작)
  - [보고 및 완료](#보고-및-완료)
  - [중단 또는 범위 변경](#중단-또는-범위-변경)
- [근거와 신뢰 경계](#근거와-신뢰-경계)
- [리서치 범위](#리서치-범위)
- [기여](#기여)
  - [검증](#검증)
- [라이선스](#라이선스)

## 설치

[마켓플레이스 안내](../../README.md#install)에 따라 이 마켓플레이스를 등록한
다음, 선택한 클라이언트에 같은 패키지를 설치한다.

```sh
omp plugin install design-workflow@sonsu-marketplace
codex plugin add design-workflow@sonsu-marketplace
claude plugin install design-workflow@sonsu-marketplace
```

### 의존성

이식 가능한 스킬에는 런타임 확장이 필요 없다. 선택적 omp 하네스에는 omp
18.12.6 이상, Bun 1.4.3 이상과 설치된 Chrome 또는 Chromium이 필요하다. 자동
검색으로 브라우저를 찾지 못하면 `DESIGN_WORKFLOW_CHROME`에 실행 파일 경로를
설정한다. 캡처는 로그인된 브라우저가 아닌 새 브라우저 프로필을 사용한다.
엄격 모드의 명령 검사는 POSIX 플랫폼이 필요하며 Windows 검사는 지원하지
않는다. `/design-report`는 기존 omp 로그인과 세션의 모델 및 사고 수준을
사용해 `PATH`의 `omp` 명령도 실행한다. 따라서 시도마다 보고서 작성과 검토에
각각 한 번씩 모델을 호출한다.

이 패키지는 브라우저 전송 라이브러리와 axe-core를 `package.json`과
`bun.lock`에 고정한다. 의존성을 명시적으로 설정하려면
`omp plugin list --json`을 확인하고 `design-workflow` 항목의 `installPath`로
이동해 다음을 실행한다.

```sh
bun install --production --frozen-lockfile
```

설정 후 omp를 다시 시작한다. 브라우저나 의존성에 접근할 수 없으면 작업을
중단해야 하며, 스크린샷을 만들어 내거나 다른 어댑터로 조용히 대체해서는 안
된다. 이 패키지는 브라우저를 설치하거나 자격 증명을 설정하거나 프로젝트의
훅을 변경하지 않는다. Codex와 Claude Code는 omp 확장을 실행하지 않는다.

## 사용법

### 이식 가능한 스킬

- `designing-interfaces`: 파일을 수정하지 않는 제안을 포함해 디지털
  인터페이스를 만들거나 개선한다.
- `reviewing-designs`: 기존 디자인을 평가하고 결과물을 변경하지 않은 채
  근거에 기반한 문제를 보고한다.
- `designing-graphics`: 재현 및 인계 제약을 포함해 독립적인 아이콘,
  일러스트레이션, 아이덴티티 에셋을 만들거나 다듬는다.

예를 들면 다음과 같다.

```text
Propose a responsive checkout layout without removing payment or error states.
Review the supplied checkout screenshots without editing anything.
Design an icon family that stays legible in small monochrome reproduction.
```

각 스킬은 조건에 따라 참조하는 리서치를 자체 디렉터리에 보관하므로 스킬만
별도로 수정해도 지원 파일이 유지된다. 이 스킬은 세 클라이언트 모두에서
판단을 돕는 지침이며, 품질 보증이나 권한 경계가 아니다.

### 관련 스킬

다음 스킬은 이 플러그인이 의도적으로 다루지 않는 영역을 다룬다. 필요하면
별도로 설치한다.

- Vercel의
  [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines)는
  구체적인 접근성, 양식, 상호작용 규칙을 기준으로 UI 코드를 검사한다.
- Emil Kowalski의 [skills](https://github.com/emilkowalski/skills)는 이
  스킬들이 규정하지 않는 명확한 관점의 모션과 컴포넌트 값을 제공한다.
- Anthropic의
  [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design)은
  기존 디자인 시스템이 없는 새 인터페이스의 독창적인 시각적 방향을 탐색한다.

### omp 엄격 실행 시작

엄격 실행 게이트는 운영자가 명령을 호출하고 정확한 계획을 승인하기 전까지
비활성 상태다. 제어 대상 도구 다섯 개는 계속 직접 노출되지만 승인 없이는
범위 내 작업을 수행할 수 없다. 이 확장은 클라이언트의 기존 도구 선택이나
최상위/`xd://` 표시 방식을 변경하지 않는다. 먼저 기존 포그라운드 및
백그라운드 작업을 중단한다. 편집 가능 범위 밖에 JSON 계획을 저장한다. 예를
들어 `design-plan.json`을 사용한다.

```json
{
  "mode": "design",
  "paths": ["page.html"],
  "goal": "Make the primary action visible at the target size",
  "brief": "The checkout button is hidden below the fold on phones. Fix it.",
  "facts": [
    {
      "subject": "Checkout page",
      "approval": "not-supplied",
      "availability": "inspectable"
    }
  ],
  "captures": [
    {
      "id": "narrow",
      "kind": "file",
      "target": "page.html",
      "width": 390,
      "height": 844,
      "steps": [{ "action": "assert-visible", "selector": "button" }]
    }
  ],
  "checks": []
}
```

```text
/design-start design-plan.json
/design-status
```

승인하기 전에 표시된 작업 공간, 경로, 대상, 시나리오와 명령을 검토한다.
헤드리스 세션은 계획을 승인할 수 없다. 모델이 작성한 승인 필드에는 권한이
없다. 도구 호출로 범위를 확장할 수 없으므로 중단한 뒤 새로 승인한 계획을
시작한다.

`brief`는 원래 요청이다. `facts`에는 확인한 프로젝트 사실을 나열한다. 각
`subject`의 `approval`은 `approved`, `rejected`, `pending`,
`not-supplied` 중 하나이고, `availability`는 `inspectable`(이번 실행에서
제공됨), `exists-not-supplied`, `does-not-exist`, `unknown` 중 하나다.
알고 있는 사실만 기록하며 모델의 추측은 넣지 않는다. 최종 보고서의 사실
표는 이 필드에서 생성하고 본문도 이에 맞게 검사한다.

`design`, `graphics`, `review` 계획에는 캡처가 하나 이상 필요하며 각 뷰포트
치수는 1~4096픽셀이어야 한다. 명령 검사는 선택 사항이다. `advisory` 계획은
결과물 작업 없이 조언만 하는 경우에 사용한다. 캡처나 검사를 선언하지 않고,
승인된 경로를 읽을 수 있지만 쓸 수 없으며, `completed`가 아닌 `advised`로
종료된다.

`paths`에는 디렉터리나 glob 권한이 아닌 작업 공간 기준의 정확한 파일 경로를
기존 파일과 새 파일 모두 포함한다. 파일 캡처는 HTML/SVG를 지원하며, 대상이
불러오는 모든 로컬 CSS, 스크립트, 이미지와 글꼴 리소스를 `paths`에 포함해야
한다. 승인되지 않았거나 불러오지 못한 에셋이 있으면 캡처가 거부된다. 웹
캡처는 정확한 루프백 HTTP(S) origin을 받으며 관찰 전용 대상에는 `paths: []`를
사용할 수 있다. 엄격 모드는 원격 사이트와 네이티브 Figma/에디터의 캡처 또는
쓰기를 지원하지 않는다. 웹 대상에는 에이전트의 작업 큐 밖에서 이미 실행
중인 일회용 서버를 제공한다. 이 확장은 서버 수명 주기를 관리하지 않는다.

캡처 단계는 선언적인 `click`, `fill`, `press`, `assert-visible`,
`assert-text`, `assert-accessible`, `assert-no-overflow` 작업이다. 각 단계에는
`selector`가 있으며, `fill`에는 `value`, `press`에는 `key`, `assert-text`에는
`text`도 있다. `assert-accessible`은 선택한 요소에
[axe-core](https://github.com/dequelabs/axe-core)를 실행하고 감지된 위반이
하나라도 있으면 실패한다. 자동화된 규칙은 접근성 문제의 일부만 찾으므로 통과가
곧 적합성을 뜻하지는 않는다. `assert-no-overflow`는 선택 영역 안의 텍스트가
영역 또는 이를 잘라내는 상위 요소를 가로로 벗어나면 실패한다. 스크롤 가능한
컨테이너 안의 텍스트, 실제로 적용된 말줄임표로 잘린 텍스트, `clip`이나
`clip-path`로 숨긴 텍스트(시각적으로 숨긴 레이블 등)는 계산하지 않으며 필드
값과 텍스트가 아닌 상자는 측정하지 않는다. 최악의 콘텐츠를 테스트하려면 해당
픽스처를 제공하는 URL을 `web` 캡처 대상으로 지정한다. `review` 계획은 단언만
허용하며 쓰기와 명령 검사는 허용하지 않는다. `graphics`는 `design`과 같은
제어된 파일 경로를 사용하며 보통 SVG가 대상이다.

검사는 `id`, `command`, `args`, `timeoutMs`를 선언한다. 셸 없이 지정된 실행
파일과 argv를 그대로 실행하며 시간 제한과 합산 출력 제한이 적용된다. 검사를
승인하면 실제 프로세스 접근을 허용하는 것이며, 읽기 전용 검사나 파일 시스템
샌드박스 검사가 아니다. 일회용 작업 공간과 로컬 서버를 사용한다.

### 보고 및 완료

에이전트는 `design_read`, `design_write`, `design_capture`, `design_check`,
`design_status`를 사용한다. 캡처는 실제 PNG 이미지와 JSON 영수증을 반환하고,
성공한 검사는 실제 프로세스 결과로 영수증을 생성한다. 근거가 최신 상태이면
에이전트가 멈추고 확장이 계속 진행할 것을 요청한다.

```text
/design-report
/design-accept
```

`/design-report`는 스트리밍되거나 대화에 추가되지 않는 omp 별도 턴에서 보고서
본문을 작성한 다음, 원래 요청과 사실 표를 함께 새 `omp -p` 프로세스로 보낸다.
이 프로세스는 세션의 모델을 사용하며 도구, 스킬, 확장 또는 컨텍스트 파일이
없다. 사실이 뒷받침하지 않는 승인, 결재 요건, 결과물 가용성 또는 검사를
단정하는 문장이 있으면 보고서가 거부된다. 거부된 문장이 표시되며 아무것도
기록되지 않는다. 다시 생성하거나 실행을 중단한다. 거부되었거나 읽을 수 없는
판정은 게시로 대체되지 않는다.

`/design-accept`는 근거와 검사된 정확한 보고서를 보여 준다. 승인하기 전에
이미지, 시나리오 결과와 결과물을 직접 살펴본다. 승인하면 해당 바이트 그대로의
수락이 기록되고 변경 없이 공식 결과로 게시되며 실행이 `completed`(또는
`advised`)로 종료된다. 수락 전 소스, 근거, 사실 또는 보고서가 변경되면
보고서는 무효가 된다. 수락은 모든 품질 요건을 충족한다는 자동화된 주장이 아닌
사용자의 판단이며, 사실 검토도 오류를 놓칠 수 있는 모델의 판단이다.

보고서와 사용자의 검토만 남으면 확장은 모델에 자체 승인을 요청하는 대신
에이전트 턴을 중단한다. 기계적으로 확인할 근거가 없으면 중단 훅이 완료를
거부하며, 변경 없이 거부가 반복되면 실행은 성공이 아닌 `blocked`로 종료된다.

### 중단 또는 범위 변경

```text
/design-stop Change the approved scope
/design-blocked Browser unavailable
/design-limited Native editor cannot be captured by this adapter
```

이 명령은 성공이 아닌 종료 방식이다. 보고서 생성을 포함해 진행 중인 제어 대상
작업을 취소하고 클라이언트의 도구 선택을 변경하지 않은 채 실행 게이트를
해제한다. 클라이언트 자체의 중단은 `/design-report` 같은 운영자 명령을
취소하지 않으므로 `/design-stop`을 사용한다. 일반적인 운영자 중단은 실행을
활성 상태로 유지하며 완료로 표시하지 않는다. 계속하기 전에 상태를 확인한다.
위의 명시적 명령은 실행을 종료한다. 종료된 실행을 재개하려면 새로 승인한
계획을 시작한다.

## 근거와 신뢰 경계

- 소스 내용과 결과물 해시는 근거와 검토를 하나의 리비전에 묶는다. 이전에
  완료된 실행을 다시 검증할 때를 포함해 변경이 발생하면 근거가 무효가 된다.
  세션 복원은 현재 브랜치만 읽으며 다른 세션은 승인을 이어받을 수 없다.
  안전하지 않은 복원은 운영자가 중단할 때까지 제어 대상 작업을 차단한다.
  캡처나 검사 재시도를 시작하면 새 시도가 실패하거나 취소되더라도 실행 전에
  이전 영수증과 수락이 제거된다.
- 실행 중인 루프백 콘텐츠는 지속적으로 모니터링하지 않는다. 영수증은 캡처한
  관찰 결과를 설명하며 이후의 모든 서버 상태를 설명하지 않는다. 소스 리비전은
  서버의 실시간 상태나 외부 의존성이 아닌 `paths`만 지문으로 기록한다. 이런
  추적이 필요하면 관련 로컬 소스를 포함한다. 그래도 수락으로 서버 상태의
  지속적인 동일성을 입증할 수는 없다.
- 실행 중에는 광범위한 셸, Eval/브라우저 브리지, 임의 쓰기, MCP 작업, 알 수
  없는 도구와 서브에이전트 생성이 차단된다. 네이티브 읽기는 패키지에 포함된
  스킬 참조 자료와 이번 실행의 결과물로 제한하며 소스 읽기에는 `design_read`를
  사용한다. 관련 없는 도구가 계속 노출될 수 있지만 게이트가 활성화된 동안 실행
  훅이 호출을 거부한다. 스키마를 숨기는 것은 권한 경계가 아니다.
- 브라우저 캡처는 교차 출처 HTTP 요청, 변경을 수행하는 HTTP 메서드, HTTP
  리디렉션, 예상치 못한 탐색, 다운로드, 팝업과 서비스 워커를 차단한다. 같은
  출처의 에셋에도 최종 직접 리소스 URL을 사용한다. 같은 출처의 GET 요청과
  스크립트도 부작용을 일으킬 수 있으므로 일회용 대상을 사용한다.
- 이는 프로세스 내부의 협력 경계이지 OS 샌드박스가 아니다. 악의적인 확장,
  동시에 실행되는 외부 쓰기 작업, 운영자가 수동으로 실행한 명령이나 독립적으로
  실행되는 프로세스를 격리하지 않는다. 승인된 검사는 계획 밖의 파일을 수정할
  수 있다. 신뢰할 수 없는 코드에 검사 권한을 부여하지 않는다.
- 공식 결과는 어시스턴트의 설명이 아닌 게시된 보고서와 실행 상태다. 보고서만
  사실 검사를 받으며 에이전트의 일반 메시지나 나중에 보고서를 바꿔 쓴 내용은
  검사받지 않는다. 유효한 영수증은 기록된 작업과 단언을 증명할 뿐 사용성,
  접근성 적합성, 법적 준수 또는 전반적인 시각적 품질을 증명하지 않는다.

[제안된 런타임 경계 결정](../../docs/decisions/0010-enforce-design-evidence-at-the-omp-runtime-boundary.md)은
이식 가능한 스킬과 omp 제어를 별도로 유지하는 이유를 설명한다. 가이드는 구현을
설명하며, 아키텍처 기록은 의사 결정자가 별도로 승인할 때까지 제안 상태다.

## 리서치 범위

조건에 따라 참조하는 자료 대부분은 검토한 Madia 자료에서 맥락에 따른 디자인
관찰 48개와 인계 워크플로 6개를 추려 낸 것이다. 출처 링크와 시간 구간은 각
관찰에 함께 기록되어 있다. 이것은 보편적인 규칙 48개나 독립적으로 측정한
사용자 성과가 아니다. 패키지에는 원본 영상, 자막, 스크린샷, 비공개 회원 전용
콘텐츠나 작성자의 로컬 리서치 경로에 대한 의존성이 포함되지 않는다. Photoshop
리터칭, 장비 홍보와 경력/사업에만 관한 조언은 이 스킬의 범위 밖이며, 여러
주제가 섞인 영상에서는 관련 디자인 근거만 사용한다. 최악의 데이터, 터치 웹,
모션 참조 자료는 Emil Kowalski의
[skills](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9)
`a81dbca07f2217b7103e510c0f13f8d5b017afc9` 버전을 로컬에 맞게 적용한 것으로,
자동 미러가 아니다. 업데이트할 때 원본 고지와 리비전 참조를 유지한다.

## 기여

풀 리퀘스트를 환영한다. 문제는
[마켓플레이스 이슈 트래커](https://github.com/sonsu-lee/sonsu-marketplace/issues)에
보고한다. [플러그인 절차](../../CONTRIBUTING.md#adding-a-plugin), 독립적인
스킬 검토와 [클라이언트 검증](../../CONTRIBUTING.md#testing-a-plugin)을 따른다.

### 검증

이 패키지 디렉터리에서 실행한다.

```sh
bun install --frozen-lockfile
bun run check
export DESIGN_WORKFLOW_CHROME=\
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
bun run test
```

사용하는 플랫폼에 맞게 실행 파일 경로를 설정한다. 경로가 없으면 브라우저와
SDK 캡처 회귀 테스트를 명시적으로 건너뛰므로 전체 검증이 아니다. 테스트는 실제
파일, 브라우저 캡처와 명령을 실행한다. SDK 수명 주기 테스트는 운영자 UI 선택과
결정적인 중단 시점만 대체하고 프로덕션 `AgentSession`, 도구 래퍼와 전체 세션
포크를 사용한다. 실제 렌더링된 캡처는 별도로 확인한다. 이 테스트는 시각적
품질을 증명하지 않는다.

이 스킬은 `origin/main`에 이전 버전이 없으므로 각 스킬의 `evals/` 디렉터리에
있는 사례와 `--baseline without`을 사용해 저장소의
[스킬 평가 절차](../../CONTRIBUTING.md#evaluating-skills)에 따라 평가한다.
통과율뿐 아니라 출력도 검토한다. 모델 실행은 CI가 아닌 로컬에서만 수행한다.

## 라이선스

마켓플레이스 콘텐츠는 [MIT](../../LICENSE) 라이선스를 따르며 저작권은
sonsu-lee에게 있다. 업스트림 부분은 [interface](skills/designing-interfaces/LICENSE-emilkowalski-skills)
및 [review](skills/reviewing-designs/LICENSE-emilkowalski-skills) 스킬에 포함된
MIT 고지를 유지한다.
