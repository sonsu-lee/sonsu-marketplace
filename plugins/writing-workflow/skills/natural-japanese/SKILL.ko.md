# Natural Japanese

> 영문 정본: [SKILL.md](SKILL.md) (`7cd88a9` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

일본어 독자가 이해할 수 있는 글을 쓴다. `scripts/lint.py`는 탐지하고, 판단은
편집자가 한다. 휴머나이저를 겹쳐 쓰지 말고, 다른 언어로 된 글을 번역하지
않는다. 기술 문서와 코드·산문 혼합 문서를 포함해 모든 산문 장르가 대상이다.
고칠 대상은 산문이며, 코드, 식별자, 명령, 인용, 숫자, URL, 확립된 용어는
고치지 않는다. 장르를 이유로 문서를 제외하지 않는다.

## 가장 중요한 규칙: 내용을 추가하지 않는다

원문에 없는 사실, 숫자, 인물, 날짜, 조건, 판단, 의견, 방침은 사실이더라도
추가하지 않는다. 확실성의 정도를 바꾸지 않고, 경험이나 보증을 지어내지 않으며,
수치 틀을 덧씌우지 않고, 수치나 표의 값을 바꾸지 않는다(불일치는 보고한다).
일반적인 경고나 설명 문단도 추가하지 않는다. 직접 뒷받침되는 명확화만
허용된다. 주장, 예시, 근거, 예외, 조건, 출처 표기, 평가의 강도를 보존한다.
새로 쓰는 글에서는 부족한 자료를 짐작으로 채우지 말고 무엇이 빠졌는지
말한다. [작업 예시](references/revision-limits.md#preservation-examples).

## 모드와 런타임

요청에 따라 모드가 정해진다. **write**는 허가된 자료로 초안을 쓴 다음
고친다. **edit**는 기존 산문을 고친다(텍스트가 주어지면 기본값). **score**는
문서를 바꾸지 않고 진단한다. 먼저 [진단](references/diagnose.md)을 읽고,
요청이 있기 전에는 다시 쓰지 않는다.

**Quick**이 기본이다. 인라인으로 작업하고, 해당하는 `references/doctypes/`
파일만 읽으며, 짧은 글이라도 lint를 실행하고, 3절의 문단 검토를 마친다.
요청이 있을 때, 영향이 큰 외부·임원 대상 문서일 때, 또는 일본어 약 10,000자를
넘을 때는 **full**을 쓴다. 이 경우 5절의 검토도 수행한다. 문서 전체는 편집자
한 명이 맡는다. 확신이 없으면 quick으로 끝내고 full이 가능하다고 언급한다.

### 스크립트 실행 전에 설치된 리소스 확인

상대 링크는 호출한 저장소가 아니라 이 스킬의 디렉터리를 기준으로 한다.
omp, Codex, Claude Code에서는 실제로 로드된 이 `SKILL.md`가 들어 있는 절대
디렉터리를 `SKILL_DIR`로 설정한다. Codex는 그 루트 아래에서 상대 링크를 읽고,
Claude Code는 이를 `Base directory for this skill`로 보여 주며, omp는
`skill://natural-japanese/<relative-path>`를 쓸 수도 있다. Python/uv에는
클라이언트 URI가 아니라 절대 파일시스템 경로를 넘긴다. 로드된 위치나 리소스를
확인할 수 없으면 설치 또는 조회 오류를 보고한다. 캐시 경로를 짐작하거나, 자산을
대상 저장소로 복사하거나, 검사를 우회하지 않는다. 대상 경로는 따옴표로
감싸고, 알면 `--genre tech`, `business`, `essay`를 추가한다.

```sh
uv run "$SKILL_DIR/scripts/lint.py" --json --genre tech "$TARGET"
```

프로젝트에 설정된 런타임을 쓰고, 프로젝트 설정, 전역 설치, 훅은 바꾸지 않는다.
실행할 수 없으면 [수동 검토](references/manual-checklist.md)를 쓰고, 기계적
검사를 하지 못했음을 밝힌다. 설정된 runner, 의존성, 입력, 스크립트의 실패는
조용히 수동 검토나 다른 runner로 넘어가도 된다는 허가가 아니다. 실패를
보고하고 원인을 해결하며, 수동 관찰은 따로 표시하고, 점수를 지어내지 않는다.
JSON과 stderr를 확인한다. lint 결과가 있어도 종료 코드는 0일 수 있다.
runner/장르 선택, 실패, 경고, 기준선(baseline) 문제, `exp` 요청에 대해서는
[런타임 노트](references/runtime.md)를 읽는다.

## 1. 쓰기 전에 결정한다

독자와 독자의 목표를 파악하고, 빠진 자료에 대해서만 질문한다. 문서 유형이
알려져 있으면 `references/doctypes/`의 해당 가이드(`minutes`, `report`,
`guide`, `memo`, `slide`)를 읽는다. 대상 프로젝트 루트나 사용자가 지정한
위치에 `style-profile.md`가 있거나, 사용자가 작성자의 문체를 학습하라고
요청하면 [작성자 프로필](references/author-profile.md)을 읽는다.

## 2. 쓰기 원칙

초안 작성, full 모드, 또는 결론, 제목, 인과관계, 강조, 확실성 표시, 문말,
화자(voice)를 건드리는 모든 편집에서는
[작문 원칙](references/writing-principles.md)을 읽는다. 수정할 때는 원문 내용과
3절의 변경 범위 안에서만 적용한다.

## 3. 기존 문서 수정

### 필수 검토: 문단별로

초안을 편집하거나 검토할 때는 [문단 검토](references/paragraph-review.md)
(독자 부담의 원인과 모호한 표현 일곱 가지 패턴)를 읽는다. lint JSON에는
`paragraphs`가 들어 있고, 사람이 읽는 출력에는 모든 제목, 목록 항목, 표의 행,
산문 단위에 번호를 붙인 시트가 있다. quick 모드를 포함해 모든 단위를 검토한다.
편집하기 전에 문제가 있는 단위는 `number: phrase → referent`(번호: 표현 → 지시
대상)로, 없는 단위는 `number: none`으로 마지막 단위까지 적고, 각 문제를
고쳤는지 이유와 함께 유지했는지
기록한다. 단독 실행:

```sh
uv run "$SKILL_DIR/scripts/paragraphs.py" "$TARGET"
```

### 모호한 표현 뒤의 구체적인 의미 되찾기

동사와 명사를 하나씩 점검한다. 더 딱딱한 바꿔 쓰기를 고르지 말고, 원문의 사실이나
코드에서 구체적인 지시 대상을 찾아 적는다. 확실성과 출처 표기는 유지하고, 여러
해석이 똑같이 그럴듯하면 질문한다.

### 수정의 한계

부정, 강조, 접속, 확실성, 목록, 제목, 순서, 문단 묶음을 바꾸기 전에, 그리고
`negation_repetition`이나 `antithesis_repetition`에 대해서는
[수정의 한계](references/revision-limits.md)를 읽는다. 주어나 화자를 짐작하지
않고, 숫자를 조용히 바로잡지 않고, 주장이나 조건을 반복이라는 이유로 지우지
않으며, 작성자의 목소리를 평평하게 만들지 않는다. 구조는 요청이 있거나 특정한
오해를 막기 위해 필요할 때만 바꾼다.

## 4. 기계적 검토와 처리

lint 결과는 의심일 뿐 지시가 아니다. 문맥을 보고 판단하며, 모든 결과를 구체적인
이유와 함께 `[Fixed]` 또는 `[Kept/reason]`(reason에 이유)으로 기록한다
([형식](references/finishing.md)). 이유 없는 `Kept`는 결정이 아니다.

## 5. 구조와 가독성

Quick 모드: 제목과 각 문단의 첫 문장을 순서대로 읽는다. full 모드와, 수정이
필요한 가독성 결과가 있을 때는 [가독성 검토](references/readability.md)를
따른다. 여기에 `outline.py`, `terms.py`, `--reading-load` 명령이 있다.

## 6. 수렴과 마무리

편집이나 초안 작성 뒤에는 이전 JSON을 가리키는 `--baseline "$BASELINE"`로 lint를
다시 실행한다. 수렴, `newfacts.py`, 임시 파일은
[마무리](references/finishing.md)를 따른다. 편집 전 원본을 그대로 저장해
비교하고, 뒷받침되지 않는 추가는 제거한다. `newfacts.py`는 일반 명사로 된 세부
사항, 확실성의 변화, 사라진 조건, 뒤바뀐 화자를 놓친다. 출력이 비어 있어도
직접 비교한다. 이 스킬은 아무것도 게시하지 않는다. 게시는 허가된 산출물
워크플로(PR, 티켓, 리뷰 코멘트)가 맡는다.

## 출처

[coji/natural-japanese][source]의 커밋 `03bc944a0c4a9f0b2a66eab065b30de5c529bf08`을
[MIT 라이선스](LICENSE)에 따라 가져와 수정했다.
[출처 기록](references/provenance.md)을 참고한다.

[source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
