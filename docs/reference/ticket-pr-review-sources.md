# 티켓·PR·리뷰 규칙 근거

티켓·GitHub 이슈·PR·커밋·브랜치·리뷰 규칙의 정본 위치, 원문 근거와 운영 결정을 기록한다. 규칙 문장은 정본 파일에만 있으며 이 문서는 규칙을 다시 쓰지 않는다. 규칙은 정본에서 고치고, 근거나 결정이 달라졌을 때 이 문서를 고친다.

## 정본 위치

| 영역 | 정본 |
| --- | --- |
| 문서별 역할, 설명 선택, AI 사용 표기 | [tracker-prose.md](../../shared/delivery-writing/tracker-prose.md) |
| 커밋 메시지(Conventional Commits 1.0.0과 확장 규칙 E1–E6) | [conventional-commits.md](../../shared/delivery-writing/conventional-commits.md) |
| 화면 자료(캡처·형식·업로드) | [media.md](../../shared/delivery-writing/media.md) |
| 호스트별 도구 대응 | [hosts.md](../../shared/delivery-writing/hosts.md) |
| 브랜치 이름 | [branch-naming.md](../../shared/agent-policy/branch-naming.md) |
| 티켓 작성 | [ticket-writing.md](../../plugins/tickets/skills/write-ticket/references/ticket-writing.md) |
| 티켓 기본형 | [write-ticket 템플릿](../../plugins/tickets/skills/write-ticket/assets/templates/) |
| GitHub 이슈 양식 | [write-ticket 이슈 양식](../../plugins/tickets/skills/write-ticket/assets/github/ISSUE_TEMPLATE/) |
| PR 작성 | [pr-writing.md](../../plugins/git/skills/write-pr/references/pr-writing.md) |
| PR 기본 양식 | [pull-request.md](../../plugins/git/skills/write-pr/assets/templates/pull-request.md) |
| 리뷰 기준(리뷰어) | [review-criteria.md](../../shared/review-core/review-criteria.md) |
| 리뷰 대응(작성자) | [responding-to-review.md](../../shared/review-core/responding-to-review.md) |
| omp 순정 reviewer에 얹는 규칙 | [sonsu-review-standard.md](../../plugins/review/omp-rules/sonsu-review-standard.md) |
| 리뷰 응답 지연 판정 | [pr-inspection.md](../../plugins/git/references/pr-inspection.md) |

`shared/` 아래 파일은 `scripts/render-shared-files.py`·`scripts/render-agent-policy.py`가 각 플러그인의 `references/`로 복사한다. 이 저장소의 `.github/` 양식도 위 PR·이슈 양식에서 생성한다.

## 원문

모두 2026-10-11에 접근했다.

- 티켓: [Linear Method — Write issues not user stories](https://linear.app/method/write-issues-not-user-stories)
- 버그: [Mozilla Bugzilla — Bug Writing Guidelines](https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html)
- GitHub 템플릿·양식
  - [리포지토리에 대한 문제 템플릿 구성](https://docs.github.com/ko/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
  - [이슈 양식 구문](https://docs.github.com/ko/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
  - [GitHub 형식 스키마 구문](https://docs.github.com/ko/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema) (영어판 [Syntax for GitHub's form schema](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema)과 대조)
  - [리포지토리에 대한 끌어오기 요청 템플릿 만들기](https://docs.github.com/ko/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
- 첨부
  - [Attaching files](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)
  - [Attaching files with GitHub CLI](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
  - 로컬 `gh version 2.102.0 (2026-09-30)`의 `gh pr create --help`
- 커뮤니티 템플릿: [stevemao/github-issue-templates](https://github.com/stevemao/github-issue-templates)의 `checklist/`, `system/`
- Google Engineering Practices(CC BY 3.0)
  - [개요](https://google.github.io/eng-practices/), [Code Review 소개](https://google.github.io/eng-practices/review/)
  - 리뷰어: [standard](https://google.github.io/eng-practices/review/reviewer/standard.html), [looking-for](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [navigate](https://google.github.io/eng-practices/review/reviewer/navigate.html), [speed](https://google.github.io/eng-practices/review/reviewer/speed.html), [comments](https://google.github.io/eng-practices/review/reviewer/comments.html), [pushback](https://google.github.io/eng-practices/review/reviewer/pushback.html)
  - 작성자: [cl-descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html), [small-cls](https://google.github.io/eng-practices/review/developer/small-cls.html), [handling-comments](https://google.github.io/eng-practices/review/developer/handling-comments.html)
  - [emergencies](https://google.github.io/eng-practices/review/emergencies.html)
- [Chromium — Respectful Code Reviews (cr_respect)](https://chromium.googlesource.com/chromium/src/+/master/docs/cr_respect.md)
- 커밋: [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). 사이트 footer의 License 표기는 [Creative Commons - CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)이다.
- 이름
  - [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) "Naming conventions"
  - [Plugins reference](https://code.claude.com/docs/en/plugins-reference) `name`
- omp 18.8.9: 설치 바이너리 `/Users/sonsu/.local/bin/omp`, 문서 `omp://rulebook-matching-pipeline.md`, `omp://slash-command-internals.md`, `omp://config-usage.md`

## 규칙별 근거

| 규칙 | 위치 | 출처 | 원문 요지 |
| --- | --- | --- | --- |
| 체크리스트형 양식(테스트 통과·린트 확인 체크박스)을 쓰지 않는다 | tracker-prose.md "문서별 역할" | stevemao `checklist`·`system` 템플릿과의 대비, Google cl-descriptions | stevemao `checklist/PULL_REQUEST_TEMPLATE.md`는 "Does your submission pass tests?", "Have you lint your code locally prior to submission?" 같은 체크박스로, `system/PULL_REQUEST_TEMPLATE.md`는 "`make -j4 test` … passes" 체크리스트로 구성된다. cl-descriptions는 설명이 "What change is being made?"와 "Why are these changes being made?"를 전달하는 "public record of change"라고 한다. |
| 티켓은 결과가 분명한 작업 하나다. 아이디어·큰 기능은 문서·논의로 넘기거나 나누고, 탐색은 결과물 형태로 만든다 | ticket-writing.md "티켓으로 만들지 정한다" | Linear "Describe concrete tasks or problems" | "An issue should describe a task with a clear, defined outcome." 작업이 아니면 이슈 트래커에 두지 않고 문서·대화로 다듬거나 작은 작업으로 나눈다. 탐색은 "Explore design" 같은 placeholder나 "Write project spec" 같은 deliverable로 만든다. |
| 한 티켓에 문제 하나, 만들기 전에 중복 검색 | ticket-writing.md "티켓으로 만들지 정한다" | Bugzilla "Open a new bug report for each issue", Linear | Bugzilla: "Open a new bug report for each issue!", "If you have multiple issues, please file separate bug reports.", 요약을 쓰며 "check if the bug has already been reported". Linear는 이슈를 "a task with a clear, defined outcome"으로 정의한다. 중복 검색 문장은 Bugzilla에만 있다. |
| 유저 스토리 형식을 쓰지 않는다 | ticket-writing.md "제목과 본문" | Linear | "we don't write user stories and think they're an anti-pattern"; 대신 "short and simple issues that describe the task in plain language"를 쓴다. |
| 제목은 할 일을 짧고 직접적으로, 본문은 필요한 만큼만 | ticket-writing.md "제목과 본문" | Linear "Write clearly and directly" | "Write short and simple issue titles that directly state what the task is." 제목은 목록·보드에서 훑어보기 쉬워야 한다. "Write only as much as you need to share to perform the task and communicate relevant information to the team." |
| 사용자 피드백은 요약하지 않고 원문을 인용하고 출처를 링크한다 | ticket-writing.md "제목과 본문" | Linear | "quote user feedback directly instead of summarizing it", "Link to the customer conversation so that if more information is needed, it's easy to get." |
| 요청·버그에는 해법이 아니라 문제를 쓰고, 담당자가 작업 티켓으로 다시 쓴다 | ticket-writing.md "제목과 본문" | Linear "Write your own issues" | 남을 위해 이슈를 쓸 때는 "frame it as an ask or describe the problem. Let the assignee come up with the solution and then rewrite the issue as a task." |
| 버그 제목은 60자 안팎의 증상, 해법을 쓰지 않는다 | ticket-writing.md "버그를 쓴다" | Bugzilla | "Summary: How would you describe the bug in less than 60 characters?", "explain the problem, not your suggested solution". Good "Cancelling a File Copy dialog crashes File Manager", Bad "Software crashes". |
| 재현 단계가 가장 중요하고, 재현 빈도와 각 단계의 조작·의도를 쓴다 | ticket-writing.md "버그를 쓴다" | Bugzilla | "Steps to reproduce are the most important part of any bug report." "Indicate whether you can reproduce the bug at will, occasionally, or not at all." "Describe your method of interacting with Firefox in addition to the intent of each step." |
| 기대 결과와 실제 결과를 나누고, 실제 결과에는 관찰한 사실만 쓴다. 추정은 따로 둔다 | ticket-writing.md "버그를 쓴다", "사실과 추정을 구분한다" | Bugzilla | "precisely describe the observed (actual) result and the expected result. Clearly separate facts (observations) from speculations." |
| 환경에는 재현되는 가장 이른 버전과, 알면 마지막 정상 버전을 쓴다 | ticket-writing.md "버그를 쓴다" | Bugzilla | "Version: select the earliest Version with what the problem can be reproduced"; 최근 생긴 버그는 "finding a regression window can help identify the cause". |
| 종류별 증거(크래시·느림·메모리·회귀·특정 입력·간헐) | ticket-writing.md "버그를 쓴다" | Bugzilla | 크래시는 Breakpad ID나 stack trace를 첨부하고 "include the crash signature in the bug summary". 느림·CPU는 performance profile 링크. 메모리는 about:memory 출력과 증가를 재현하는 단계. 회귀는 regression window. 특정 페이지는 "reduced testcase". 간헐적 버그는 별도 안내 링크. |
| 이슈 양식은 버그와 요청 두 개만 둔다 | `ISSUE_TEMPLATE/` | Linear "Write your own issues" | "Everyone on the team should write their own issues." 남을 위해 쓰는 경우의 예로 버그 보고를 든다. |
| 양식 label을 섹션 제목의 영어와 같게 둔다 | `ISSUE_TEMPLATE/` | syntax-for-issue-forms | "참가자가 문제 양식을 작성하면 각 입력에 대한 응답이 Markdown으로 변환되고 문제 본문에 추가됩니다." |
| `required`는 필수 섹션에만 건다. 공개 저장소에서만 동작한다 | `ISSUE_TEMPLATE/` | form schema `required` | `required`: "요소가 완료될 때까지 양식 제출을 방지합니다. 퍼블릭 리포지토리에서만 사용 가능." |
| `render`는 Logs에만 둔다 | `ISSUE_TEMPLATE/1-bug.yml` | form schema textarea `render` | 아래 "원문으로 확인한 사실" 참고 |
| 증거는 `upload`로 받고 `accept`는 `validations` 아래에 둔다 | `ISSUE_TEMPLATE/1-bug.yml` | form schema upload 검증 표·예시 | 아래 "원문으로 확인한 사실" 참고 |
| `blank_issues_enabled: false`여도 쓰기 이상 권한자에게 빈 이슈가 보인다 | `ISSUE_TEMPLATE/config.yml`, `repository-templates.md` | configuring-issue-templates "템플릿 선택기 구성" | 아래 "원문으로 확인한 사실" 참고 |
| PR 양식은 `.github/pull_request_template.md` 하나로 둔다 | pull-request.md, `.github/` | creating-a-pull-request-template | "파일을 숨겨진 디렉터리에 저장하려면 끌어오기 요청 템플릿의 이름을 `.github/pull_request_template.md`로 지정합니다." 루트·`docs/`·`PULL_REQUEST_TEMPLATE/` 위치도 지원한다. |
| 커밋 기반은 Conventional Commits 1.0.0 원문이다 | conventional-commits.md "Conventional Commits 1.0.0" | conventionalcommits.org, CC BY 3.0 | `<type>[optional scope]: <description>` 구조와 명세 1–16. 사이트 footer License는 "Creative Commons - CC BY 3.0"이다. |
| 확장 규칙(E1–E6)이 명세보다 우선한다 | conventional-commits.md "확장 규칙" | 명세 FAQ | "the flexibility of Conventional Commits allows your team to come up with their own types", 확장 명세에 대해 "(and encourage you to make these extensions!)". |
| `revert` 커밋은 footer에 `Refs: <SHA>`를 쓴다 | conventional-commits.md E1 | 명세 FAQ revert | "One recommendation is to use the revert type, and a footer that references the commit SHAs that are being reverted", 예시 `Refs: 676104e, a215868`. |
| PR 제목 description은 명령형 한 문장이며 다른 PR과 구분되어야 한다 | pr-writing.md "제목" | Google cl-descriptions "First Line" | "Short summary of what is being done.", "Complete sentence, written as though it was an order." 첫 줄은 "should stand alone" 해서 다른 CL과의 차이를 설명 없이 알 수 있어야 한다. |
| 나쁜 PR 제목 예 | pr-writing.md "제목" | Google cl-descriptions "Bad CL Descriptions" | "Fix bug" is an inadequate CL description. 이 밖에 "Fix build.", "Add patch.", "Moving code from A to B.", "Phase 1.", "Add convenience functions.", "kill weird URLs." |
| PR 본문 Why·Changes·Notes·Verification 작성법, 외부 링크에 기대지 않기, 병합 전 재확인 | pr-writing.md "본문 섹션", "최종 점검" | Google cl-descriptions "Body is Informative", "Review the description before submitting" | 본문은 "a brief description of the problem that's being solved, and why this is the best approach", 단점, 버그 번호·벤치마크·설계 문서 링크를 담는다. 외부 링크는 "may not be visible to future readers"이므로 맥락을 남긴다. "Even small CLs deserve a little attention to detail." 리뷰 중 크게 바뀔 수 있으므로 제출 전 설명이 "still reflects what the CL does"인지 확인한다. |
| PR 경계: 자기 완결, 테스트 포함, 리팩터링 분리, 새 API는 사용처와 함께, 크기 신호, 분할 방법 | pr-writing.md "PR 경계를 점검한다" | Google small-cls | "the right size for a CL is one self-contained change", "The CL should include related test code", 새 API는 "include a usage of the API in the same CL". "100 lines is usually a reasonable size for a CL, and 1000 lines is usually too large"; 파일 전체 삭제는 한 줄로 셀 수 있고 50개 파일에 흩어진 200줄은 크다. 리팩터링은 별도 CL, "Small cleanups such as fixing a local variable name can be included". 분할은 stacking, by files, horizontally, vertically. 의존하는 CL은 "Don't Break the Build". |
| 공개 저장소 첨부는 인증 없이 열람되므로 민감 정보를 가린다 | media.md "캡처한다" | attaching-files | "For public repositories, uploaded files can be accessed without authentication." |
| 영상은 H.264 MP4 | media.md "형식과 용량" | attaching-files의 H.264 권장 | 아래 "원문으로 확인한 사실" 참고 |
| 이미지 10MB, 영상 무료 플랜 10MB·유료 플랜 100MB | media.md "형식과 용량" | attaching-files | "10MB for images and gifs", 무료 플랜 저장소 영상 "10MB", 유료 플랜 저장소 영상 "100MB", 그 밖의 파일 "25MB". |
| 영상 참조는 한 문단에 단독으로 둔다 | media.md "본문에 배치한다" | attaching-files-with-github-cli | 영상 참조는 "must be the only content in its paragraph". "If the reference appears within a sentence, it renders as a link instead." |
| 영상에는 대체 텍스트를 붙일 수 없으므로 앞 줄에 설명을 쓴다 | media.md "본문에 배치한다" | attaching-files-with-github-cli, `gh pr create --help` | "Alt text is not supported on video files." `gh pr create --help`: "Video renders as a player and has no alt text, so it cannot be given any." |
| 본문의 로컬 참조는 업로드 URL로 바뀌고, 참조되지 않은 첨부는 본문 끝에 붙는다 | media.md "GitHub에 올린다" | attaching-files-with-github-cli | "GitHub CLI rewrites the reference in place to point at the uploaded file", "Any attached file that the body does not reference is appended to the end of the body, in the order you passed the flags." |
| 첨부에는 push 권한이 필요하다 | media.md "GitHub에 올린다" | attaching-files-with-github-cli | "You need push access to the repository to attach files." |
| 일부 첨부만 실패한 경우의 동작 | media.md "GitHub에 올린다" | `gh pr create --help`, gh 2.102.0 | 아래 "원문으로 확인한 사실" 참고 |
| 코드 건강도를 분명히 높이면 승인하고, 원치 않는 기능은 거절할 수 있으며, 다듬을 점은 `Nit:` | review-criteria.md "승인 기준" | Google standard | "reviewers should favor approving a CL once it is in a state where it definitely improves the overall code health of the system being worked on, even if the CL isn't perfect." 원치 않는 기능은 "can certainly deny approval even if the code is well-designed". "there is no such thing as 'perfect' code—there is only better code"; 덜 중요한 지적은 "Nit: "를 붙인다. 코드 건강도를 확실히 낮추는 CL은 긴급 상황 말고는 받지 않는다. |
| 사실·데이터 우선, 스타일 가이드만 권위, 설계는 원칙으로, 동등하면 작성자 선택, 기존 코드와의 일관성 | review-criteria.md "판단 원칙" | Google standard "Principles" | "Technical facts and data overrule opinions and personal preferences." "On matters of style, the style guide is the absolute authority." 설계는 "should be weighed on those principles"; 동등한 선택지면 작성자의 선호를 받아들인다. "If no other rule applies, then the reviewer may ask the author to be consistent with what is in the current codebase". |
| 리뷰 순서: 전체 → 핵심 설계 → 나머지 | review-criteria.md, review-code SKILL "절차" | Google navigate | Step One "Take a broad view of the change"(필요 없는 변경이면 즉시 이유와 대안을 정중하게), Step Two "Examine the main parts of the CL"(큰 설계 문제는 "send those comments immediately"), Step Three "Look through the rest of the CL in an appropriate sequence"; "Sometimes it's also helpful to read the tests first". |
| 볼 것 목록 | review-criteria.md "볼 것" | Google looking-for | Design, Functionality(엣지 케이스·동시성, UI 변경은 직접 확인하거나 demo 요청), Complexity와 over-engineering, Tests("Will the tests actually fail when the code is broken?"), Naming, Comments(왜를 설명), Style(큰 스타일 변경을 다른 변경과 섞지 않음), Consistency, Documentation, Every Line(생성 코드·데이터는 훑어봄), Context, Good Things. |
| 코멘트 라벨: 라벨 없음 = 필수, `Nit:`, `Optional:`, `FYI:`. 해법 전체보다 문제·이유 | review-criteria.md "코멘트 라벨" | Google comments, cr_respect | comments "Label comment severity": "Nit: This is a minor thing", "Optional (or Consider): … not strictly required", "FYI: I don't expect you to do this in this CL". "Giving Guidance": 해법을 상세 설계할 의무는 없으며 "pointing out problems and providing direct guidance" 사이에서 균형을 잡는다. cr_respect "Explain why": "please don't say 'This is wrong'". |
| 어조: 간결·중립, 이유를 붙이고, 주어는 코드, 확신이 없으면 여지, 의도를 모르면 묻기, 망신·극단 표현 금지 | review-criteria.md "어조와 문체" | Google comments "Courtesy"·"Explain Why", cr_respect | comments: "always making comments about the code and never making comments about the developer", Bad "Why did you use threads here when there's obviously no benefit to be gained from concurrency?", Good "The concurrency model here is adding complexity…". cr_respect: "Maybe I'm missing something, but…", "Ask for the why", "Don't shame people"("How could you not see this"), "Don't use extreme or very negative language", "Discuss the code, not the person." |
| 잘한 점은 근거가 있을 때만 구체적으로, 의례적 칭찬은 넣지 않는다 | review-criteria.md "어조와 문체" | cr_respect "No need to be all fake smiles" | "Mention the positives": "No need to be all fake smiles, but if there's a good decision, … acknowledging that is a nice thing to do." Google comments도 좋아한 점에 "include why you liked something"이라고 한다. |
| 중요하지 않은 취향은 지적하지 않거나 `Nit:`, 같은 논점을 끝없이 반복하지 않는다 | review-criteria.md "어조와 문체" | cr_respect "Don't bikeshed", "Find an end" | "Always ask yourself if this decision really matters in the long run, or if you're enforcing a subjective preference." "If it looks good, move on." 큰 리팩터링은 새 CL로 옮긴다. |
| 판정 `Approve with comments`의 조건 | review-criteria.md, review-code SKILL "결과" | Google speed "LGTM With Comments" | 남은 코멘트가 있어도 승인하는 경우: "The reviewer is confident that the developer will appropriately address all the reviewer's remaining comments", "The comments don't have to be addressed by the developer", "The suggestions are minor". |
| "나중에 정리하겠다"를 받지 않는다. 주변 문제는 작성자 할당 이슈로 | review-criteria.md "받지 않는 것" | Google pushback | "Cleaning It Up Later": "usually unless the developer does the clean up immediately after the present CL, it never happens." "If a CL introduces new complexity, it must be cleaned up before submission unless it is an emergency." 주변 문제는 "file a bug for the cleanup and assign it to themselves"; 버그를 참조하는 TODO는 선택이다. |
| 이해되지 않는 코드는 리뷰 답글이 아니라 코드·주석으로 명확하게 | review-criteria.md "받지 않는 것" | Google comments | "Accepting Explanations": 설명을 요청하면 "that should usually result in them rewriting the code more clearly"; "Explanations written only in the code review tool are not helpful to future code readers." |
| 큰 변경은 분할 요청, 못 나누면 설계 코멘트부터. 일부만 리뷰했으면 범위를 밝힌다 | review-code SKILL "결과" | Google speed "Large CLs", looking-for "Exceptions" | speed: "ask the developer to split the CL into several smaller CLs that build on each other"; 나눌 수 없으면 "at least write some comments on the overall design". looking-for: 일부만 리뷰한 경우 "note in a comment which parts you reviewed". |
| 긴급 변경의 정의, 정확성과 속도만 보고 이후 전체 리뷰 | review-criteria.md "긴급 변경" | Google emergencies | 긴급 CL은 "a small change that: allows a major launch to continue instead of rolling back, fixes a bug significantly affecting users in production, handles a pressing legal issue, closes a major security hole". 리뷰어는 속도와 정확성만 보고, 해결 후 "give them a more thorough review". "What Is NOT An Emergency?"와 "What Is a Hard Deadline?" 목록을 둔다. |
| 리뷰 요청 뒤 1영업일 넘게 응답이 없는 PR을 표시한다 | pr-inspection.md "리뷰 응답 지연" | Google speed "One business day is the maximum" | "One business day is the maximum time it should take to respond to a code review request (i.e., first thing the next morning)." |
| 이해하지 못했다는 지적에는 코드 → 코드 주석 → 답글 순서 | responding-to-review.md "이해하지 못했다는 지적" | Google handling-comments "Fix the Code" | "your first response should be to clarify the code itself. If the code can't be clarified, add a code comment … only then should your response be an explanation in the code review tool." |
| 동의하지 않을 때 먼저 검토하고, 이유·트레이드오프 → 대안이 나쁜 이유 → 질문 순서로 반론 | responding-to-review.md "동의하지 않을 때" | Google handling-comments "Think Collaboratively" | 첫 질문은 "Do I understand what the reviewer is asking for?". Bad "No, I'm not going to do that." Good "I went with X because of [these pros/cons] … using Y would be worse because of [these reasons]. Are you suggesting that Y better serves the original tradeoffs, that we should weigh the tradeoffs differently, or something else?" |
| 이번 변경이 만든 복잡도는 지금 정리하고 주변 문제는 이슈로 | responding-to-review.md "미루는 정리" | Google pushback | 위 "Cleaning It Up Later"와 같다. |
| 작성자 어조: 개인 공격으로 받지 않고, 건설적 내용에 답하고, 화난 채 답하지 않는다. 비건설적이면 대화에서 다투지 않는다 | responding-to-review.md "어조와 문체" | Google handling-comments "Don't Take it Personally", cr_respect | "Ask yourself, 'What is the constructive thing that the reviewer is trying to communicate to me?'", "Never respond in anger to code review comments." 비건설적인 리뷰어에게는 직접 또는 비공개로 설명하고 필요하면 관리자에게 올린다. 이 저장소는 그 판단을 사용자에게 넘긴다. cr_respect "Discuss the code, not the person." |
| 감사 표현은 실제 결함을 찾아 줬을 때만 짧게 | responding-to-review.md "어조와 문체" | cr_respect "a 'thank you' to the reviewers is occasionally a nice thing" | "And on the converse, a 'thank you' to the reviewers is occasionally a nice thing, too." |
| 스킬·플러그인 이름 | 플러그인 구성(아래 운영 결정) | Claude best-practices, plugins-reference `name`, omp `config-usage.md` | best-practices: `name`은 "lowercase letters, numbers, and hyphens only", "Action-oriented: `process-pdfs`"를 허용하고 "Vague names", "Overly generic" 이름을 피한다. plugins-reference: "Claude Code namespaces every component under it, so an agent `reviewer` in plugin `deploy-tools` appears as `deploy-tools:reviewer`." omp: dedup key는 "skills: `name`", "same key => first item wins". |

## 운영 결정

원문에 없는 수치·형식이다. 원문은 판단 근거로만 쓰고 아래 값은 이 저장소가 정했다.

- 화면 자료 형식
  - 스크린샷은 PNG, 폭 1600px 이하다.
  - 영상은 MP4(H.264 `libx264`, `yuv420p`, 오디오 없음, `+faststart`), 폭 1280px 이하, 30fps 이하, 20초 안팎이다. 기본 인코딩은 `-preset slow -crf 28`이다.
  - 상한을 넘으면 crf 30–32 → fps 24·15 → 폭 960 순서로 낮춘다.
  - GIF는 쓰지 않는다.
  - 기본 상한은 10MB다. 원문 상한(이미지 10MB, 영상은 플랜에 따라 10MB·100MB) 중 어느 저장소에서나 통과하는 값이다.
  - 자료는 PR이면 `${TMPDIR}/pr-media/<branch>/`, 티켓이면 `${TMPDIR}/ticket-media/<slug>/`에 두고, 이름은 `NN-{before|after}-<slug>.{png,mp4}`다. 커밋하지 않는다.
- 커밋 확장 규칙 E1–E6
  - E1: type을 `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `revert`로 고정한다.
  - E2: 헤더는 `<type>[(<scope>)][!]: <description>`, 소문자 type·scope, 명령형 description(영어는 소문자 시작·마침표 없음, 한국어·일본어는 명사형), 72자 이하다.
  - E3: 본문에 변경 이유를 쓰고, 이유가 자명한 오타·포맷·생성물 갱신만 생략한다.
  - E4: breaking change는 `!`와 `BREAKING CHANGE:` footer를 둘 다 쓴다. `BREAKING-CHANGE`는 읽을 때만 같은 뜻으로 인정한다(명세 16번).
  - E5: 커밋 하나에 type 하나다. 명세 FAQ의 "Go back and make multiple commits whenever possible."과 같은 방향이다.
  - E6: 티켓은 footer `Refs: <ID>`로만 참조하고 헤더·브랜치 이름에 넣지 않는다.
- 브랜치 이름: 접두사는 커밋 type과 같되 `feat`만 `feature/`로 쓴다. 설명은 소문자 kebab-case이고 티켓 ID·team key·사용자명은 넣지 않는다.
- 티켓 기본형은 작업·요청·버그·조사 4종이다. 섹션 제목은 출력 언어에 따라 한국어·영어 대응표를 쓴다.
- 이슈 양식
  - 필드 구성: 버그는 Steps to reproduce, Expected result, Actual result, Environment, Logs, Evidence, Hypothesis이고 요청은 Problem, Desired outcome, Alternatives considered다.
  - 중복 확인은 필수 체크박스가 아니라 `markdown` 안내문으로 둔다.
  - `contact_links`는 Discussions나 비공개 취약점 신고가 켜진 저장소에서만 추가한다.
- PR 기본 양식의 섹션 이름은 `Why`, `Changes`, `Notes`, `Screenshots`, `Verification`이다. 출력 언어와 관계없이 영어로 둔다. 리뷰 라벨(`Nit:`·`Optional:`·`FYI:`)과 판정 이름(`Approve`, `Approve with comments`, `Request changes`)도 영어로 고정한다.
- 리뷰 응답 지연의 1영업일 계산
  - UTC 기준 월–금으로 센다. 토·일에 들어온 요청은 다음 월요일 00:00부터 센다.
  - 요청 기록이 없거나 수집이 partial이면 판정하지 않는다.
  - 원문은 "first thing the next morning"까지만 말하고 시간대·휴일 규칙은 정하지 않는다.
- 문체: 한국어 리뷰 코멘트와 답글은 합니다체로 쓴다. 영어는 평이한 문장으로 쓰고, 느낌표와 이모지는 쓰지 않는다.
- 작성자 답글 형식 문장
  - 수정함: "수정했습니다. <무엇을 어떻게 바꿨는지 한 문장> (<짧은 커밋 SHA>)"
  - 근거로 기각: 근거 위치와 바꾸지 않은 이유를 쓰고, 다른 경로를 뜻했는지 묻는다.
  - 추가 확인 필요: 판단에 필요한 결정과 선택지를 쓴다.
  - 범위 밖: "이번 변경 범위 밖이라 #<번호>로 등록했습니다."
- 라벨과 omp reviewer priority 대응
  - 라벨 없음(필수)은 병합을 막아야 하는 결함(데이터 손실·보안·크래시·빌드 실패)이면 `P0`, 그 밖이면 `P1`이다. `Optional:`은 `P2`, `Nit:`과 `FYI:`는 `P3`이다.
  - 판정 줄은 `summary.explanation` 첫 줄에 둔다. 필수 지적이 있으면 `incorrect`와 `Request changes`다. 그 밖의 지적만 있으면 `correct`와 `Approve with comments`이고, 지적이 없으면 `correct`와 `Approve`다.
  - 순정 reviewer의 P0–P3 정의 문구는 바이너리에서 찾지 못했다. `strings`에는 `P0`–`P3` 열거 검사와 색상 매핑만 있고, reviewer 프롬프트는 `/$bunfs/root/reviewer-q3dt0q8v.md`로 묶여 있어 본문을 읽지 못했다. 그래서 이 대응은 원문 정의와 맞춘 것이 아니라 운영 결정이다.
- 플러그인 구성
  - `git`: `branch`, `commit`, `push`, `write-pr`, `inspect-prs`, `repair-pr`
  - `tickets`: `write-ticket`, `update-ticket`
  - `review`: `review-code`, `review-overengineering`, `review-maintainability`, `review-operability`, `review-failure-modes`, `audit-overengineering`, `address-review`
  - `dev-workflow`: 설계·계획·구현·디버깅·검증 스킬
  - omp에서는 스킬이 플러그인 접두사 없이 `name`으로 중복 정리되므로 스킬 이름은 저장소 전체에서 유일하게 둔다.
- omp 기본 배포는 `git`, `tickets`, `review`, `fluent-korean`, `fluent-english`, `fluent-japanese`, `design` 7개다. `dev-workflow`는 omp 기본 배포에서 제외한다. `review`는 순정 `reviewer` 위에 규칙 `sonsu-review-standard`를 얹는다. 이 규칙은 omp 패키지에만 들어간다.

## 원문으로 확인한 사실

### omp 마켓플레이스 플러그인 규칙

`omp --version`은 `omp/18.8.9`이고 바이너리는 `/Users/sonsu/.local/bin/omp`다. `strings`로 `claude-plugins` provider의 규칙 등록문과 로더를 확인했다.

```text
var B0 = "claude-plugins", IUe = "Claude Code Marketplace", OUe = 70;
    description: "Load rules from marketplace plugin rules directories",
    priority: OUe,
    load: asp
```

`asp`는 각 플러그인 루트의 `rules` 디렉터리에서 `md`·`mdc` 파일을 읽는다(`xd.join(i.path, "rules")`, `extensions: ["md", "mdc"]`).

`omp://rulebook-matching-pipeline.md`의 `agents` 절은 다음과 같다.

> Restricts a rule to matching agents. … patterns are lowercased glob patterns matched case-insensitively against the agent definition name (`scout`, `reviewer`, `foreman-*`).
>
> Omitted (or an empty list) means the rule applies to every agent — the pre-existing behavior.
>
> Subagents receive the parent's unfiltered discovered rule list and re-evaluate `agents` under their own name, so a scout-only rule loads in scouts and nowhere else.

같은 문서의 bucket 단계는 "Drop rules whose `agents` globs do not match the session's agent name (`main` for a top-level session, otherwise the agent definition name)"이고, `alwaysApply === true` 규칙은 "Full content injected into system prompt"다. 다만 같은 문서의 제한 사항 목록("The rule providers currently loaded for `rules` are `native`, `omp-plugins`, `agents`, `cursor`, `windsurf`, `cline`, `github`, and embedded `builtin-defaults`")에는 `claude-plugins`가 없다. `claude-plugins`가 규칙을 읽는다는 사실은 바이너리에서만 확인했다.

### 순정 reviewer 결과 스키마

omp 문서(`omp://` 전체)에서는 `overall_correctness`·`line_start`가 검색되지 않는다. 그래서 바이너리의 결과 정규화 코드에서 확인했다.

```text
const r = o.overall_correctness;
const i = o.explanation;
const a = o.confidence;
if (r !== "correct" && r !== "incorrect" || typeof i !== "string" || typeof a !== "number") {
  return;
return {
  summary: {
    overall_correctness: r,
    explanation: i,
    confidence: a
  },
  findings: qXa(o.findings)
```

finding 하나는 `title`, `body`(문자열), `priority`(`"P0"`–`"P3"`, 숫자 0–3도 같은 값으로 정규화), `confidence`(0–1), `file_path`, `line_start`, `line_end`를 모두 갖춰야 결과에 남는다. 필드 목록은 `["findings", "array"]`, `["overall_correctness", "scalar"]`, `["explanation", "scalar"]`, `["confidence", "scalar"]`다.

### `gh` 일부 첨부 실패 시 동작

로컬 `gh --version`은 `gh version 2.102.0 (2026-09-30)`이다. `gh pr create --help`는 다음과 같다.

> If some attachments upload and others fail, the pull request is still created with the ones that succeeded. The command then exits with a non-zero status, but the new pull request's URL is still printed to stdout.

### textarea `render`가 첨부를 막는다

form schema의 textarea `render`:

> 값이 제공되면 제출된 텍스트의 서식이 코드 블록으로 지정됩니다. 이 키를 제공하면 파일 첨부 파일 또는 Markdown 편집을 위해 텍스트 영역이 확장되지 않습니다.

영어판: "When this key is provided, the text area will not expand for file attachments or Markdown editing."

### 빈 이슈가 쓰기 권한자에게 계속 보인다

configuring-issue-templates "템플릿 선택기 구성":

> `blank_issues_enabled`이 `false`로 설정되면, 쓰기, 유지 관리, 또는 관리자 역할의 쓰기 액세스 이상 권한이 있는 사용자는 템플릿 선택기에서 **빈 문제** 옵션을 **유지 관리자만**으로 레이블이 지정된 상태로 계속 볼 수 있습니다. 읽기 또는 심사 역할이 있는 참가자는 구성된 템플릿만 볼 수 있습니다.

### `upload`의 `accept`는 `validations` 아래에 있다

form schema "Validations for `upload`" 표에는 `required`와 `accept`가 있다. `accept`는 "A comma-separated list of file extensions that are accepted. If omitted, all supported file types are accepted."이다. 예시도 `validations` 아래에 둔다.

```yaml
- type: upload
  id: screenshots
  attributes:
    label: Upload relevant files
    description: "Drag and drop any relevant screenshots or log files."
  validations:
    required: false
    accept: ".png,.jpg,.gif,.log,.txt,.zip"
```

한국어판도 같은 표와 예시를 싣는다. 다만 표 렌더링이 깨져 `accept` 행이 표 밖에 나온다.

### H.264 권장

attaching-files "Image and media files":

> Video codec compatibility is browser specific, and it's possible that a video you upload to one browser is not viewable on another browser. At the moment we recommend using H.264 for greatest compatibility.

## 미검증

- 표 안 로컬 경로 치환: `gh … --attach`가 Markdown 표 셀 안의 로컬 이미지 경로도 업로드 URL로 바꾸는지 확인하지 않았다. 원문은 본문의 로컬 참조를 "no matter where the body text comes from" 바꾼다고만 하고 표 안의 경우는 따로 다루지 않는다. 확인에는 원격 draft PR 생성이 필요해 실행하지 않았다. 바뀌지 않으면 [media.md](../../shared/delivery-writing/media.md)의 대안(`### Before`·`### After` 아래 이미지 하나씩)을 쓴다.
- reviewer 규칙의 실제 적용: `claude-plugins` provider가 `rules/`를 읽는다는 사실과 `agents` 필터 동작은 위에서 확인했다. 격리 profile에 설치하면 `sonsu-review-standard.md`가 플러그인 캐시의 `rules/`에 놓이는 것도 확인했다. 그러나 격리 profile에 모델 인증이 없어 `/review`를 실행하지 못했으므로, 이 규칙이 `/review`·`/annotate code-review`의 순정 `reviewer` system prompt에 실제로 들어가는지는 관찰하지 않았다.
