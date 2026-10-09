---
name: to-pr
description: 현재 Git 변경을 주제별 단일 PR 또는 준비된 GitHub stacked PR의 초안·게시 payload로 만들 때 사용하며, 필요한 GitHub Issues·Linear 티켓과 시각 증거를 연결한다. branch·commit 생성, 기존 PR 수정, code review와 merge에는 사용하지 않는다.
---

# to-pr: PR로 변환하기

현재 Git 변경에서 왜 바꿨고 무엇이 어떻게 달라졌는지, 리뷰·배포 전에 알아야 할 조건을 설명한다. 서로 의존하는 여러 주제는 GitHub의 native stacked PR로 연결한다. 화면 변경이 있거나 사용자·저장소가 화면 자료를 요구하면 판단에 필요한 매체와 준비 상태를 함께 다룬다.

## 작업 연속성

여러 단계의 작업이나 외부 쓰기를 맡은 메인 controller는 [연속성 참고 자료](../../references/continuity.md)로 진행과 근거를 기록한다. 컴팩션·재개 후에는 실제 상태와 대조한다. 짧은 단발 작업과 위임된 작업자는 별도 기록을 만들지 않으며, 파일 쓰기가 금지되면 checkpoint와 Git exclude도 수정하지 않는다.

## 작성 단계와 확인 근거

단계의 산출물은 작성·게시 판단에 필요한 정보이지 별도 파일이나 PR 본문 체크리스트가 아니다. 입력·최종 diff·초안·도구 결과를 대조하며, 검토했다는 자기 보고를 근거로 삼지 않는다.

| 단계 | 작업과 산출물 | 완료를 판단할 근거 |
| --- | --- | --- |
| W1 대상·양식·권한 | 아래 절차로 저장소, 최종 base/head와 전체 diff 범위, 양식·언어, draft/publish 및 미확인 조건을 정한다. | 조회 결과나 제공 자료와 일치하고 양식 미확인을 부재로 바꾸지 않는다. |
| W2 사실 수집 | [작성 지침](references/pr-writing.md)에 따라 티켓과 최종 diff에서 바뀐 동작·선택 이유·남은 작업을 확보한다. | 각 설명에 근거가 있으며 이전 초안과 다르면 최종 diff를 따른다. |
| W3 제목·본문 | 같은 지침으로 왜 바꿨고 무엇이 어떻게 달라지는지, 검토·배포에 필요한 조건을 설명한다. | 필요한 내용이 남고 확인되지 않은 효과나 이유를 만들지 않는다. |
| W4 화면 자료 | [시각 증거](references/visual-evidence.md)·[첨부 규칙](references/media-attachments.md)으로 자료와 볼 지점, 미준비 이유·조건을 정한다. | 필요한 상태·동작에 맞는 매체를 선택하고 준비 계획과 실제 생성·검사를 구분한다. |
| W5 최종 대조 | 초안을 최종 diff·양식·티켓 연결 문법·자료와 비교해 고치고 게시 전 조건을 확인한다. | 범위 불일치·요구 누락·연결 변조·하지 않은 검증이나 첨부의 완료 주장이 없다. |
| W6 게시·재조회 | publish일 때만 아래 기존 절차로 게시·첨부하고 결과를 남긴다. draft는 미게시 초안으로 끝낸다. | 원격 ID·URL·본문·연결·자료 표시를 실제 trace와 재조회로 확인한다. URL만으로 영상 재생을 단정하지 않는다. |

권한 확인→쓰기, 자료 검사→업로드, 쓰기→재조회의 의존 순서는 지킨다. diff나 자료가 달라지면 W2–W5를 다시 대조한다. 동등한 도구나 병렬 읽기는 허용하며 호출 순서만으로 이행 여부를 판단하지 않는다.

## 책임 경계를 지킨다

이 스킬은 새 PR의 초안과 게시를 담당한다. 준비된 여러 branch의 새 PR을 native stack으로 연결하는 것도 포함한다. branch·worktree·commit 생성, branch rename, commit rewrite, rebase·squash, force push, merge와 publish 시작 전에 존재하던 PR 수정은 담당하지 않는다. 다만 현재 publish 흐름에서 방금 만든 PR의 stack 연결·검토한 미디어 첨부와, 필수 첨부를 모두 검증한 뒤 사용자가 명시한 ready 상태로의 전환은 담당한다. 이 예외로 제목·티켓·reviewer·label과 다른 본문 내용은 바꾸지 않는다. 코드 구현, 일반적인 작업 완료, 티켓 작성, code review 또는 push 요청만으로 자동 실행하지 않는다.

이 스킬은 현재 대화, repository와 검증 가능한 티켓 정보를 바탕으로 독립적으로 동작한다. 다른 플러그인이나 스킬이 설치되었거나 먼저 실행되었다고 가정하지 않는다.

## 모드를 정한다

- `draft`: repository를 읽고 PR별 제목, 본문, base·head, 티켓 연결, 검증 상태와 필요한 시각 자료 계획을 완성한다. push, 미디어 업로드와 PR 생성은 하지 않는다.
- `publish`: 사용자가 현재 대화에서 새 PR 생성을 명시적으로 요청한 경우에만 검증된 branch를 일반 push하고 새 PR을 만든다. 여러 새 PR을 게시할 때는 요청 범위와 [stacked PR 규칙](references/stacked-prs.md)에 따라 처리한다.

단순한 작성 요청은 `draft`로 처리한다. 여기서 `draft`는 원격 PR을 만들지 않는 준비 모드이며
GitHub Draft 상태와 다르다.

`publish`의 `target_pr_state`는 기본 `draft`다. 사용자가 Ready, non-draft 또는 즉시 review 가능한 상태를 명시한 경우에만 `ready`로 정하고 근거를 payload에 남긴다. “PR을 올려 줘”는 상태 지정이 아니다. 검증 통과나 미디어 부재도 Ready 전환 근거가 아니다. 대상이 Draft PR을 지원하지 않으면 Draft 요청을 Ready로 바꾸지 않는다.

명시적인 publish 요청은 정확한 기존 remote로 대상 branch를 일반 push하는 데 필요한 권한을 포함한다. 같은 권한을 반복해서 묻지 않되 위 책임 경계를 확대하지 않는다.

## PR 경계를 정한다

[stacked PR 규칙](references/stacked-prs.md)으로 실제 변경의 주제와 의존 관계를 확인해 주제별로 단일 PR, 서로 독립적인 별도 PR 또는 native stack을 정한다. 현재 branch에 여러 주제가 섞였거나 필요한 branch·commit이 아직 없으면 주제와 의존 관계에 맞는 PR 계획과 필요한 Git 작업을 제시한다. 이 스킬에서 변경을 임의로 재배치하거나 새 branch를 만들지 않고, 필요한 branch·commit이 준비되거나 사용자가 별도 Git 작업을 함께 허가한 뒤에 게시한다.

## repository와 변경을 고정한다

[GitHub PR 규칙](references/github.md#저장소-상태를-확인한다)으로 저장소·base·head·기존 PR과 diff 범위를 읽기 전용으로 확인한다. [PR 템플릿 규칙](references/pr-template.md)으로 적용 양식과 언어를 정하고, [PR 작성 지침](references/pr-writing.md)에 따라 전체 diff와 현재 검증 근거로 제목·본문을 작성한다. commit 제목이나 `--fill` 결과만으로 변경 내용을 추론하지 않는다. 선택적 Writing·Fluent 적용은 [작성 지침 함께 적용하기](../../references/writing-composition.md)를 따르며, 적용 양식과 확인 상태, 출력 언어, 실제 근거·편집 범위와 보호할 연결 문법을 함께 전달한다. 임시 초안은 양식 확정이나 게시 조건 충족을 뜻하지 않는다.

## 티켓을 연결한다

티켓 ID나 URL이 있거나 사용자가 연동을 요청하면 [티켓 연결 규칙](references/ticket-linking.md)을 따른다. 티켓 연결을 위해 branch 이름이나 PR 제목에 ID를 추가하지 않는다. 이미 존재하는 branch 이름의 ID는 가장 낮은 신뢰도의 hint로만 취급한다. branch에 ID가 없다는 이유로 PR을 막거나 branch를 만들고 rename하지 않는다.

GitHub Issues와 Linear 중 provider를 문자열 모양만으로 추측하지 않는다. 지원하지 않는 tracker의 연결이 필수인 요청은 연결 없는 PR로 바꿔 게시하지 않고 범위를 알린다.

티켓 intent와 PR event의 status effect는 분리한다. 게시 전에 대상 저장소·team·site의 integration과 automation 정책을 확인하고, native automation이 해당 event를 처리하면 직접 같은 transition을 실행하지 않는다.

## 시각 증거를 준비한다

사용자가 screenshot을 요청했거나 diff가 제품 화면·상호작용을 바꾸거나 저장소 규칙이 요구하면 [시각 증거 규칙](references/visual-evidence.md)을 따른다. UI와 무관한 변경에는 빈 스크린샷 섹션을 만들지 않는다. 로컬 이미지나 비디오를 넣을 때는 [미디어 첨부 규칙](references/media-attachments.md)도 따른다.

## 새 PR을 게시한다

`publish` 직전에 저장소·인증 주체·base·head SHA·remote ref·기존 PR과 최종 payload를 다시 확인한다. 양식 출처, 언어, 티켓 연결, 검증 상태와 `target_pr_state`가 현재 변경·요청에 맞는지 대조한다. 미디어가 있으면 필수 자료의 준비·검사 결과도 확정한다.

단일 PR과 서로 독립적인 PR은 [GitHub 게시 절차](references/github.md#생성하고-검증한다)를 PR별로 따른다. 여러 PR의 native stack은 [stacked PR 게시 절차](references/stacked-prs.md#native-stack으로-게시하고-검증한다)를 따른다. 미디어가 있는 경우의 Draft 생성·파일별 첨부·상태 전환과 CLI를 사용할 수 없을 때의 대안은 GitHub 게시 절차가 연결하는 미디어 문서에서 처리한다.

## 결과를 확인한다

게시 후에는 PR·미디어 재조회 결과를 최종 payload와 대조한다. 가능하면 canonical ticket도 다시 읽어 link 적용과 status effect를 별도로 확인한다.

branch별 push, PR 생성, native stack 연결, 미디어별 업로드·본문 반영, ready 전환, 티켓 link와 status effect의 결과를 각각 보고한다. 실행하지 않은 검증과 확인하지 못한 상태를 성공으로 표현하지 않는다. 준비한 초안과 실제 게시 결과, 부분 성공을 구분한다.
