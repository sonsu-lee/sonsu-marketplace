# 티켓·PR 작성 설계 근거

Workflow의 티켓·PR 작성 규칙과 기본형의 정본은 플러그인 파일이다. 이 문서는 정본 위치, 설계 결정과 외부 근거만 기록하며 규칙을 다시 쓰지 않는다. 규칙은 정본 파일에서 고치고, 결정이나 근거가 달라졌을 때만 이 문서를 고친다.

## 정본 위치

| 대상 | 정본 |
| --- | --- |
| 티켓 양식 선택·출력 언어·본문 내용·최종 점검 | [ticket-writing.md](../../plugins/workflow/skills/to-ticket/references/ticket-writing.md) |
| 티켓 기본형 항목 | [to-ticket 기본형](../../plugins/workflow/skills/to-ticket/assets/templates/) |
| 티켓 분할·게시·수정·결과 보고 | [to-ticket](../../plugins/workflow/skills/to-ticket/SKILL.md) |
| PR 양식 선택·출력 언어·기본형 적용 조건 | [pr-template.md](../../plugins/workflow/skills/to-pr/references/pr-template.md) |
| PR 본문 내용·검증·최종 점검 | [pr-writing.md](../../plugins/workflow/skills/to-pr/references/pr-writing.md) |
| PR 기본형 항목 | [pull-request.md](../../plugins/workflow/skills/to-pr/assets/templates/pull-request.md) |
| PR 모드·책임 경계·게시 직전 점검·결과 보고와 SKILL에 남긴 티켓 연결 규칙 | [to-pr](../../plugins/workflow/skills/to-pr/SKILL.md) |
| PR 저장소 상태·diff 범위·payload·게시 절차 | [github.md](../../plugins/workflow/skills/to-pr/references/github.md) |
| PR 경계와 stack | [stacked-prs.md](../../plugins/workflow/skills/to-pr/references/stacked-prs.md) |
| 티켓 연결과 status effect | [ticket-linking.md](../../plugins/workflow/skills/to-pr/references/ticket-linking.md) |
| 시각 자료와 첨부 | [visual-evidence.md](../../plugins/workflow/skills/to-pr/references/visual-evidence.md), [media-attachments.md](../../plugins/workflow/skills/to-pr/references/media-attachments.md) |
| 커밋 메시지 언어·제목·본문·trailer | [commit-message.md](../../plugins/workflow/references/commit-message.md) |
| 티켓·PR·커밋 공통 문장 형식(경량형·서식 밀도·서두·어조·제목·AI 사용 표기) | [tracker-prose.md](../../plugins/workflow/references/tracker-prose.md) |

## 설계 결정

- Workflow는 Linear와 GitHub Issues를 지원하며, 티켓·PR 기본형은 두 tracker에 공통으로 적용한다.
- 티켓은 문제·원하는 결과·합의된 제약을 전달하고, 이미 합의된 제약이 아닌 원인 분석·해결 방법·작업 순서·검증 방법은 작업자가 정한다.
- PR은 리뷰어와 이후 history 독자가 알아야 할 것만 설명한다. 한 티켓에는 여러 PR이 연결될 수 있으며 각 PR은 자기 변경과 확인 결과만 설명한다.
- 대상 공간의 양식이 내부 기본형보다 우선하며, 조회하지 못한 상태는 양식 부재와 구분한다.
- 기본형에 완료조건 체크리스트를 강제하지 않고, 모르는 값을 채우기 위해 빈 항목이나 반복적인 `미확인` 문구를 만들지 않는다.
- 티켓은 독립적으로 우선순위를 정하거나 담당·완료 여부를 판단할 결과가 있을 때만 나눈다. Terraform처럼 앞 단계의 merge와 apply 뒤에 다음 변경을 진행해야 한다면 같은 티켓의 순차 PR로 추적할 수 있다.
- 부분 PR은 비종결 관계로 연결하고, 완료 표현은 그 PR의 병합 자체가 티켓의 전체 결과를 충족할 때만 쓴다. [Linear는 한 이슈에 여러 PR을 연결하고 비종결 관계를 지원한다](https://linear.app/docs/github).
- 티켓 연결 채널은 PR 본문이며 티켓 연동을 이유로 branch 이름에 티켓 ID를 넣지 않는다. [Linear 연동](https://linear.app/docs/github), [GitHub Issues 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
- 제품 화면·상호작용 변경은 마킹한 스크린샷이나 timestamp caption 영상을 PR 본문에 둔다. 사용자 요청이나 대상 PR 양식의 요구가 우선한다. VRT 결과 링크는 리뷰어가 PR 밖으로 이동해야 하고 변경 위치를 표시하지 않으므로 본문 자료를 대체하지 않는다.
- 티켓·PR·커밋의 언어는 사용자 지정과 저장소·대상 공간의 명시 규칙을 먼저 따르고, 근거가 없으면 마지막 단계로 영어를 쓴다. 대화 언어는 근거로 쓰지 않는다.
- AI 사용 표기는 저장소가 요구할 때만 그 형식대로 넣고, 요구가 없으면 AI용 trailer나 서명을 붙이지 않는다.
- 배경과 변경을 한 문단으로 설명할 수 있는 PR과 필수 항목 하나만 채워지는 티켓은 제목 없는 경량형을 허용한다.

## 외부 근거

### 티켓 제목과 버그 보고

영어 원문 [Mozilla의 Bug Writing Guidelines](https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html)는
“Cancelling a File Copy dialog crashes File Manager”를 좋은 제목의 예로 제시한다.
발생 조건·동작과 문제가 생기는 대상을 함께 알려 주기 때문이다. 재현 절차와 실제·기대 결과를
구분하는 구조도 참고한다. 버그 보고 지침이므로 기능 제안·조사 티켓에 재현 절차를 강제하는 근거는 아니다.

### PR 설명

아래는 배대준의 [공통시스템개발팀 코드 리뷰 문화 개선 이야기](https://techblog.woowahan.com/7152/)에 실린 한국어 MR 사례의 짧은 발췌다. 원문은 빌드 오류와 의존성 버전 변경을 설명한 뒤 해결을 연결한다.

> TS2305: Module '"react-router"' has no exported member 'useHistory'. 에러를 내면서 빌드가 깨집니다.
>
> 사용하는 react-router의 버전을 package.json에 명시합니다.

이 사례에서 가져올 점은 “버전 명시”라는 수정 행위를 독자가 겪는 빌드 실패와 연결하는 구조다. 원인·결과는 해당 MR의 설명이며 다른 PR에 자동 적용할 근거가 아니다. 글의 평가는 팀의 실무 경험에 따른 것이고, 모든 PR에 동일한 길이·항목을 강제하는 규칙은 아니다.

일본어 원문 [Wantedly의 PR 작성법](https://docs.wantedly.dev/fields/dev-process/how-to-write-a-pull-request)은
라우팅·controller 수정 목록을 나쁜 예로, 데모 화면에서 할 수 있는 동작과 접근 범위를 좋은 예로
제시한다. 그중 제한을 밝히는 원문은 “デモメニューは本番環境以外でのみアクセスできる。”다.
파일 이름을 지우라는 규칙이 아니라, 변경 목록을 읽고 사용 동작과 적용 범위를 추론해야 하는 부담을
줄이는 예시다. 이 문서는 일본어 저자의 원문으로 참고했으며 번역판을 별도 표본으로 세지 않는다.

영어 원문 [Google의 CL 설명 지침](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)은
첫 줄에서 구체적인 변경을 식별하고 본문에서 문제·접근 방법·제약을 설명하는 예를 제시한다. 같은 지침은
코드가 소프트웨어가 무엇을 하는지는 보여 줘도 왜 존재하는지는 보여 주지 않으므로, 이후 독자가 결정을
바꿔도 되는지 판단할 맥락을 남기라고 설명하며 benchmark 결과와 설계 문서 링크를 그 맥락의 예로 든다.
CL은 Google의 코드 변경 단위이며 이 저장소 PR 양식과 같지는 않다. 구조의 판단 근거로 참고하고,
원문의 길이나 제목 규칙을 팀 양식보다 우선하지 않는다.

### PR 크기

[stacked PR 규칙](../../plugins/workflow/skills/to-pr/references/stacked-prs.md)의 약 400줄 기준은 Cisco 팀을 대상으로 한 [SmartBear 연구](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)의 “한 번의 리뷰에서 200–400줄을 넘기면 결함 발견 능력이 떨어진다”는 관찰을 PR 크기 기준으로 차용한 값이다. [Google의 Small CLs 지침](https://google.github.io/eng-practices/review/developer/small-cls.html)도 100줄은 대체로 적당하고 1000줄은 대체로 크다고 보며, 작은 변경이 롤백하기 쉽고 리팩터링은 기능 변경과 분리하되 작은 정리는 같은 CL에 둬도 된다고 설명한다.

### 커밋 메시지와 AI 사용 공개

- [Git SubmittingPatches](https://github.com/git/git/blob/master/Documentation/SubmittingPatches): 본문에 문제, 택한 방식의 이유, 버린 대안을 쓴다.
- [Linux kernel의 AI coding assistant 지침](https://docs.kernel.org/process/coding-assistants.html): AI는 `Signed-off-by`를 붙이지 않고 `Assisted-by:`로 사용을 밝힌다.
- [How to Write a Git Commit Message](https://cbea.ms/git-commit/): 명령형 제목, 제목 길이 제한, 본문에 무엇과 왜를 쓰는 관례를 정리한다.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): `type(scope): description` 제목과 `BREAKING CHANGE` footer 형식의 명세다.
- [GitHub squash merge 기본 제목 변경 공지](https://github.blog/changelog/2022-05-11-default-to-pr-titles-for-squash-merge-commit-messages/): squash 병합 시 PR 제목이 기본 커밋 제목이 된다.
- [Kubernetes PR 템플릿](https://github.com/kubernetes/kubernetes/blob/master/.github/PULL_REQUEST_TEMPLATE.md): PR 본문에 AI 사용 공개 칸을 둔 저장소 사례다.
- [LLVM AI Tool Policy](https://github.com/llvm/llvm-project/blob/main/llvm/docs/AIToolPolicy.md): 저장소가 AI 도구 사용 공개 방식을 정책으로 정한 사례다.
- [Linear Method: Write issues not user stories](https://linear.app/method/write-issues-not-user-stories): 이슈 설명은 필요한 만큼만 쓴다.

## 변경 절차

규칙이나 기본형을 바꾸면 정본 파일, 이 문서의 결정·근거와 [라우팅 평가 사례](../../evals/skill-routing/cases.json)와 [Workflow 작성 사례](../../evals/writing/workflow-cases.json)를 함께 대조한다. 정적 형식 검사와 사례 정의는 실제 tracker 자동화·미디어 게시 성공의 증거가 아니므로, 원격 작업에서는 결과를 다시 읽는다.
