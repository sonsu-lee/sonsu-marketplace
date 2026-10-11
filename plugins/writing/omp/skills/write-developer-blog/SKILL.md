---
name: write-developer-blog
description: 개발자 블로그·기술 아티클·TIL·디버깅 회고·기술 선택 글을 자료·코드·검증 결과에 근거해 기획·작성·수정·검토할 때 사용한다. 일반 기술 질의응답, 업무 문서·README·티켓·PR 작성과 블로그 작성법 조사는 각 담당 절차로 다룬다.
---

# 개발자 블로그 작성

독자가 겪는 문제와 확인한 근거를 연결해 기술 글을 쓴다. 저자의 경험·의견은 저자가 제공하거나 확인한 범위에서 사용하고 코드·출처·실행 결과로 설명을 보강한다.

## 절차

1. 요청을 `plan`, `draft`, `revise`, `audit`으로 구분하고 사용자 메모·저자가 확인한 경험·허용된 저장소 자료·출처를 모은다. 저자의 1인칭 경험·동기·감정·의사결정 이유는 저자 자료로 확인한다. 핵심 저자 정보가 부족하면 필요한 질문만 반환한다. 이때 `plan`이거나 흐름을 요청한 경우에만 가능한 각도와 흐름도 함께 반환한다. 핵심 정보가 충분하고 세부 사실만 부족하면 확인한 범위로 초안을 쓰고 나머지는 초안 밖의 미확인 사항으로 둔다.
2. TIL, debugging, technical-decision, deep-dive, how-to, retrospective, opinion 중 독자의 질문에 맞는 모드를 고른다. [글의 골격과 문단 흐름](references/article-shapes.md)에서 필요한 부분을 읽고 본문보다 먼저 아래 여섯 필드로 흐름 의사코드를 정한다. 짧은 TIL은 필드마다 한 줄이면 충분하며 독자·핵심 답·근거·한계를 남긴다. 글에 맞는 절과 연결을 선택하고 제목·문단 수나 SEO 키워드, 일률적인 서론·결론 대신 독자의 질문을 기준으로 구성한다.

   ```text
   reader: 이 글을 읽을 사람
   reader_problem: 독자가 막힌 지점이나 내려야 할 결정
   main_answer: 글이 전달할 한 가지 핵심 답
   section_sequence: 답에 도달하는 절의 순서
   evidence_by_section: 각 절의 코드·출처·관찰 근거
   ending_and_limits: 독자가 적용할 다음 행동과 남은 경계
   ```

   `revise`·`audit`에서 원문에 흐름이 없으면 현재 글로부터 최소한으로 복원한다. 저자 의도·인과관계는 원문에 있는 범위로 둔다. `draft`에서 짧은 TIL이나 논지·근거가 충분한 글은 흐름을 정한 같은 응답에서 본문까지 작성한다. 한 번에 작성해 달라는 요청도 핵심 저자 정보가 있는 범위에서 완성하고, 흐름 공개 여부는 결과 계약을 따른다.
3. 핵심 기술 주장이 자료로 뒷받침되지 않으면 [기술 근거와 직접 검증](references/technical-evidence.md)에 따라 필요한 최소 범위를 확인한다. 안전한 local inspection·기존 test·build·local browser로 판정할 수 있을 때 수행한다. 새 재현 코드는 tracked 파일 밖의 격리 임시 디렉터리에 만들고 정리한다. 실행 전 `environment`, `input`, `command`, `expected`를 정하고 실행 뒤 `observed`와 한계를 기록한다. 예상과 결과가 다르면 논지와 흐름을 관찰에 맞춰 갱신한다. 실행 권한·자료가 부족한 부분은 `not_run`과 필요한 권한·자료로 구분한다.
4. 한 문단이 하나의 주장·질문·결정을 맡도록 `주장 또는 질문 → 근거·메커니즘 → 의미·다음 문단으로의 연결` 순서로 쓴다. 코드 앞뒤에 무엇을 보여 주는지 설명하고 핵심과 무관한 부분만 덜어 낸다. 본문에는 독자에게 필요한 근거·한계를 자연스럽게 포함하고 내부 evidence ledger는 작성 판단에 사용한다. 사실의 확실성·시점·수치·이름·링크·인과관계를 유지하며 시간 순서와 원인을 구분한다.
5. 외부 다중 출처 조사나 언어별 표현 지침이 필요하면 [협업과 언어 선택](../../references/collaboration.md)을 적용한다. 여러 차례 이어지는 장문·여러 파일 작성만 [작업 연속성](../../references/continuity.md)으로 이어 간다.
6. 흐름과 본문이 같은 핵심 답을 향하는지, 각 실질적 주장이 제공 자료·출처·관찰에 연결되는지 대조한다. 1인칭·의견·원인과 결과·성공과 검증 범위가 근거보다 강해졌으면 고친다. 실행하지 않은 검증과 다른 환경의 결과는 해당 상태로 보존한다. [퇴고 점검](../../references/revision.md)과 [제목과 리드](../../references/headings.md)를 적용한다.

## 결과

| 요청 | 반환 내용 |
|---|---|
| `plan` | 여섯 필드의 이름·값을 모두 채운 흐름 의사코드, 절별 근거 공백, 글을 바꾸는 질문 |
| `draft` | 내부에서 흐름을 고정한 뒤 확인된 범위의 새 본문. 흐름을 요청받았을 때만 본문 앞에 함께 표시 |
| `revise` | 영향받은 흐름 필드의 변경 전후와 지정 제목·문단의 수정본. 꼭 필요한 인접 연결을 바꿨다면 그 범위도 표시 |
| `audit` | 판단 기준으로 쓴 현재 흐름 필드와 위치·근거 상태·저자성 또는 한계의 문제·영향·최소 수정 방향이 있는 finding |

설명이나 평가를 요청받지 않았다면 해당 결과와 실제로 남은 근거 사항만 반환한다. 초안이 실행 결과에 기대거나 미확인·미실행 사항이 남으면 초안 뒤에 근거·미확인 항목을 둔다. 각 항목에는 `observed`, `source-confirmed`, `inference`, `unknown`, `not_run` 중 하나인 `state`와 `observer`를 두고, 실행 근거에는 `current_task_rerun`과 `limits`도 둔다. 값은 [기술 근거 계약](references/technical-evidence.md#근거-상태)을 따른다.

## 예시

입력: “디버깅 글 초안을 써 줘. Windows 11의 Docker Desktop 4.34에서 `docker compose up`을 실행하자 app 컨테이너가 바로 종료됐고 `docker compose logs app`에 `exec /app/start.sh: no such file or directory`가 남았어. `start.sh`의 줄바꿈을 CRLF에서 LF로 바꾸고 다시 실행하니 컨테이너가 계속 실행됐어. 다른 OS와 base image는 확인하지 않았어.”

내부 흐름(흐름을 요청받지 않았으므로 응답에 표시하지 않음):

```text
reader: Windows에서 셸 스크립트를 컨테이너 시작 명령으로 쓰는 개발자
reader_problem: `start.sh`가 없다는 오류와 함께 컨테이너가 바로 종료된다
main_answer: 저자 환경에서는 `start.sh`의 줄바꿈을 LF로 바꾸자 컨테이너가 계속 실행됐다
section_sequence: 증상과 로그 → 줄바꿈 변경과 재실행 결과 → 확인 범위
evidence_by_section: 저자가 제공한 `docker compose logs app` 출력과 LF 변경 뒤 실행 결과
ending_and_limits: 다른 OS·base image와 오류가 생기는 메커니즘은 확인하지 않았다
```

본문:

> Windows 11의 Docker Desktop 4.34에서 `docker compose up`을 실행하자 app 컨테이너가 바로 종료됐어요. `docker compose logs app`에는 `exec /app/start.sh: no such file or directory`가 남아 있었어요. `start.sh`의 줄바꿈을 CRLF에서 LF로 바꾸고 다시 실행하자 컨테이너가 계속 실행됐어요. 다른 OS와 base image에서는 확인하지 않았어요.

근거:

```text
state: observed
observer: author
environment: Windows 11, Docker Desktop 4.34
command: docker compose up, docker compose logs app
observed: CRLF일 때 `exec /app/start.sh: no such file or directory`와 함께 종료, LF로 바꾼 뒤 계속 실행
current_task_rerun: false
limits: 다른 OS·base image와 줄바꿈이 오류를 일으키는 메커니즘은 확인하지 않음
```

대조: 허용된 로컬 환경에서 같은 compose 파일로 현재 작업 중에 다시 실행했다면 그 결과는 `observer: agent`, `current_task_rerun: true`인 별도 항목으로 둔다. 실행 환경이 저자와 다르면 저자 환경의 결과를 대신하지 않는다.

## 경계

- 글 작성 요청만으로 파일 생성·게시·Git 작업을 수행하지 않는다. 운영·공유 환경 변경, 사용자·고객 데이터 접근, 유료 서비스, 배포, 원격 쓰기·tracked 파일 수정은 별도 권한을 확인한다.
- `revise`는 지정 구간과 필요한 인접 연결만 바꾸고 나머지 제목·문단·코드·링크·주장 순서를 보존한다. `audit`은 원문을 수정하지 않는다.
- 실제 제품 결함의 진단·수정이 주목적이면 사용할 수 있는 Dev Workflow 절차가 맡고 이 스킬은 전달된 근거로 글을 구성한다.

## 참고 자료

- [글의 골격과 문단 흐름](references/article-shapes.md)
- [기술 근거와 직접 검증](references/technical-evidence.md)
- [협업과 언어 선택](../../references/collaboration.md)
