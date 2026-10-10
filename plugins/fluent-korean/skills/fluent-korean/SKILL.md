---
name: fluent-korean
metadata:
  version: "2.3.2"
description: 한국어 블로그·문서·메시지·티켓·PR을 새로 쓰거나 기존 글의 AI 티·번역투를 윤문·진단할 때 사용한다. 일반 대화 답변·단순 맞춤법 교정·번역은 각 요청에 직접 답하는 경로로 처리한다.
---

# Fluent Korean — im-not-ai 기반

한국어 글의 표현 문제를 근거에 따라 줄이고 의미와 필자의 말투를 보존한다. 파일·정량 윤문은 light·standard·heavy 경로와 결정적 게이트로 검증한다.

## 절차

1. [적용 경로](references/drafting-rules.md#적용-경로)로 새 글·국소 수정·진단·파일 윤문을 구분한다.
2. 새 글은 같은 문서의 생성 규칙을 적용해 작성한다.
3. 기존 글은 [공통 보존 규칙](references/quick-rules.md#공통-보존-규칙)을 따른다. 짧은 국소 수정과 진단은 근거가 있는 표현만 다루고 결과를 채팅으로 반환한다.
4. 파일·정량 윤문은 [파일 윤문 절차](references/file-workflow.md)를 따른다. 이 스킬 디렉터리는 `${CLAUDE_SKILL_DIR}`이며, 절차 문서의 `<skill-dir>`를 이 절대 경로로 바꿔 실행한다. 입력 준비 → 경로 선택 → 역할별 윤문 → 서법·쉼표 후처리 → `verify_gates.py` → 필요한 finalize 순서로 진행한다.
5. 게이트의 실제 수치와 종료 코드로 결과 상태를 정한다. 경고·보류·미확인 상태는 완료와 구분해 보고한다.

## 결과

새 글·국소 수정은 요청한 본문을, 진단은 문제 위치와 근거를 반환한다. 파일·정량 윤문은 상태 줄, 윤문본, summary 핵심 표와 필요한 재실행 안내를 반환한다. 상세 형식은 [Finalize와 결과](references/file-workflow.md#finalize와-결과)에 있다.

## 예시

입력: `_workspace/notice.md`의 회의 안내문을 정밀 모드로 윤문한다.

결과:

```text
fluent-korean — 경로: heavy (사용자 지정) / run_id: 2026-10-09-001-a3f9
완료. 경로 heavy / 변경률 18.4% / 등급 A / 자체검증 6/6 통과
```

함께 반환하는 summary에는 `A-8 진행되어질 예정입니다 → 진행할 예정입니다` 같은 탐지 표를 넣는다. 게이트가 exit 2를 반환하면 이 윤문본을 채택하지 않고 보수 강도로 한 번 다시 실행한다.

## 경계

- 사용자가 요청한 구간만 고친다.
- 파일·정량 윤문은 사용자 원본 파일을 덮어쓰지 않고 결과를 run 디렉터리의 `final.md`에 쓴다.

## 참고 자료

- [적용 경로와 새 글 생성 규칙](references/drafting-rules.md)
- [파일 윤문 절차](references/file-workflow.md)
- [공통 보존·패턴·자체검증·등급](references/quick-rules.md) — `build_quick_rules.py`가 taxonomy와 header·footer에서 생성
- [진단 인덱스](references/diagnosis-rules.md) — `build_diagnosis_rules.py`가 taxonomy에서 생성
- [분류 체계](references/ai-tell-taxonomy.md)
- [카테고리별 처방](references/rewriting-playbook.md)
- [학술 인용](references/scholarship.md)
- [설계 노트](references/design-notes.md)
- [웹 서비스 스펙](references/web-service-spec.md)
