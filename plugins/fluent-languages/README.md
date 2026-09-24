# Fluent Languages

한국어·일본어·영어를 자연스럽게 작성하고 코드·사실·조건을 보존하는 독립 Codex·Claude Code·OMP 플러그인이다.
지침은 한국어로 관리하며, 출력 언어는 사용자의 요청을 따른다.

```sh
codex plugin add fluent-languages@sonsu-marketplace
```

## 언어별 독립 스킬

각 언어의 `SKILL.md`와 그 아래 참고 자료가 정본이다. 공통 언어 코어, include와 언어 스킬 생성기는
사용하지 않는다. 문법·생략·용어·격식·보존 기준을 언어별로 직접 관리하며 한 언어를 수정해도
다른 언어에 전파하지 않는다.

- [한국어](skills/fluent-korean/SKILL.md): `snflkd/fluent-korean`의 문장 구성과
  `epoko77-ai/im-not-ai`의 A–J 패턴을 새 작성과 윤문에 적용한다.
  기술 답변·코드 리뷰·README·API 문서·runbook도 대상이다.
- [일본어](skills/fluent-japanese/SKILL.md)와 [영어](skills/fluent-english/SKILL.md):
  독립 정본으로 관리한다. 이번 한국어 확장의 규칙을 자동으로 적용하지 않는다.

한국어는 작성 후 [윤문 절차](skills/fluent-korean/references/post-editing.md)와
[빠른 규칙](skills/fluent-korean/references/quick-rules.md)으로 점검한다. 적용 여부가 모호하면
[전체 패턴](skills/fluent-korean/references/ai-tell-taxonomy.md)과 교정 예시를 확인한다.
각 규칙의 적용 조건과 예외를 따르며 의미·정보·형식·문체를 보존한다.
이미 자연스러운 글은 그대로 둔다. 진단 등급·변경률·파일 출력을 강제하지 않는다.
[원본 출처](UPSTREAM.md)와 [라이선스 고지](THIRD_PARTY_NOTICES.md)를 함께 제공한다.

## Writing·Workflow와 함께 사용하기

Fluent는 언어별 문장·표현·어조를, Writing은 정보 선별·문서 배치·문장과 문단의 구성을 담당한다.
Workflow는 티켓·PR의 실제 양식과 필수 항목, 근거 확인·연결·게시를 담당한다.
각 플러그인은 단독으로 쓸 수 있고 다른 플러그인의 설치나 재호출을 요구하지 않는다.

함께 사용할 때는 선별한 사실, 편집 범위와 정해진 양식을 같은 초안에 적용한다. Fluent가 표현을
다듬는 과정에서 제외한 내용을 복원하거나 조건·코드·고정 양식을 바꾸지 않는다.

## 한국어 결과물 평가

[한국어 평가](../../evals/fluent-korean/README.md)는 대표 사례의 정보·의미·편집 범위 보존과
자연스러움·명료성·문체 적합성을 확인한다. 자동 검사와 사람의 판단을 구분하며 수정량이나
AI 탐지 점수를 품질 기준으로 사용하지 않는다.

## 컴팩션 후 작업 재개

Codex·Claude의 [`fluent-languages:fluent-languages-task-continuity`](skills/task-continuity/SKILL.md) 또는 OMP의 [`skill://fluent-languages-task-continuity`](skills/task-continuity/SKILL.md)는 장문·여러 문서 편집의
원문·초안·완료 구간을 `.sonsu/continuity/`에 기록한다. 다른 작업의 표현만 도울 때는
주 작업 담당자의 기록을 따르며 짧은 단발 작업에는 기록하지 않는다.

`SessionStart` hook은 활성 기록이 있을 때 경로를 전달한다. hook의 신뢰 여부는 호스트에서
관리하며, 사용할 수 없으면 작업 연속성 스킬로 수동 복구한다. helper는 Python 3.9+와 POSIX를
사용한다. 이 작업 재개 도구는 언어 표현 규칙을 공유하거나 주입하는 코어가 아니다.
[운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고한다.
