# Tickets

GitHub Issues·Linear 티켓을 작업·요청·버그·조사 양식으로 짧고 직접적으로 쓰고, 기존 티켓의 상태·담당자·관계를 승인 범위 안에서 바꿉니다.

## 설치

```bash
codex plugin add tickets@sonsu-marketplace
claude plugin install tickets@sonsu-marketplace
omp plugin install tickets@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `write-ticket` | 버그·요청·작업·조사를 티켓으로 쓰거나 기존 티켓의 제목·본문을 고칠 때, 저장소 이슈 양식을 설치할 때 | 티켓 초안 또는 필드별 실제 반영 상태 |
| `update-ticket` | 기존 티켓의 상태·담당자·blocking·related·duplicate 관계를 바꿀 때 | operation별 applied·unapplied·unknown·no-op |

## 사용 예시

요청: “고객이 ‘팀 단위로 알림을 끌 수 없어서 불편하다’고 했어. GitHub Issue 초안으로 써 줘. 게시하지 마.”

`write-ticket`이 요청형 양식으로 제목 `팀 단위로 알림을 끌 수 없음`, 고객 원문 인용과 출처를 담은 `문제`, 구현 방식 없이 달라져야 할 상태만 쓴 `원하는 결과`를 초안으로 냅니다. 해법은 담당자가 정하므로 쓰지 않습니다.

## 구성

- 티켓 작성 기준은 `write-ticket`의 [티켓 작성 지침](skills/write-ticket/references/ticket-writing.md)과 [기본 양식](skills/write-ticket/assets/templates/)에 있습니다. 저장소 이슈 양식(issue form)은 [저장소 양식](skills/write-ticket/references/repository-templates.md) 절차로 설치합니다.
- 공통 기준: [문장 형식](references/tracker-prose.md), [작성 지침 조합](references/writing-composition.md), [화면 자료](references/media.md), [호스트별 도구](references/hosts.md)
- 공유 기준은 `shared/`의 정본에서 생성기로 복사합니다. 생성물은 직접 고치지 않습니다.
- branch·commit·PR은 `git` 플러그인이 담당합니다.
- [작업 연속성](references/continuity.md)은 여러 단계 작업의 계약·진행·근거 위치를 `.sonsu/continuity/`에 기록합니다. omp 배포본은 omp 순정 todo·session을 씁니다.
- 작성 지침·양식의 출처 고지는 [MIT 고지](WRITING_LICENSE.md)에, 설계 참고는 [UPSTREAM.md](UPSTREAM.md)에 있습니다.

## 검증

```bash
python3 scripts/render-shared-files.py --check
python3 scripts/render-continuity.py --check
```
