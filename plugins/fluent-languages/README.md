# Fluent Languages

코드·명령어·사실을 보존하며 한국어·일본어·영어를 자연스럽게 작성하는 독립 Codex·Claude Code
플러그인이다. 지침은 한국어로 관리하고, 출력 언어는 사용자가 요청한 언어를 따른다.

```sh
# Codex
codex plugin add fluent-languages@sonsu-marketplace

# Claude Code
claude plugin install fluent-languages@sonsu-marketplace
```

## Writing·Workflow와 함께 사용하기

Fluent는 언어별 어순·표현·어조를, Writing은 문장 관계·문단 구성·정보 순서를 담당한다.
Workflow는 티켓·PR의 실제 양식과 필수 항목, 근거 확인·연결·게시를 담당한다.
세 플러그인은 각각 설치해 단독으로 사용하거나 같은 초안에 함께 적용할 수 있다.

표현을 다듬을 때는 정해진 편집 범위와 구성을 따르고 사실·조건·코드·고정 양식을 보존한다.
다른 플러그인의 설치나 재호출은 Fluent 적용의 조건이 아니다. 공통 구성 원칙의 정본은 Writing에,
언어별 표현 규칙과 독립적인 보존 기준은 Fluent에 둔다.

## 원본과 생성본 관리

언어별 정본은 `sources/languages/`, 공통 경계·보존 규칙은 `sources/core/`에 있다.
수정 후 아래 명령으로 이 플러그인 안의 스킬 3개를 갱신하고 원본과 일치하는지 확인한다.

```sh
python3 plugins/fluent-languages/scripts/render-skills.py
python3 plugins/fluent-languages/scripts/render-skills.py --check
```

[조합 검증](../../evals/writing/README.md)의 결과는 자동 스킬 선택이나 원어민 선호 평가와 구분한다.

## 컴팩션 후 작업 재개

[`fluent-languages:task-continuity`](skills/task-continuity/SKILL.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를
작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고 같은 세션의 컴팩션·재개 후 실제 상태와 대조한다.
짧은 단발 작업에는 기록하지 않으며, 파일 쓰기 금지와 기존 승인 범위를 유지한다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 스킬·기록 경로만 전달한다. 설치 후 CLI의
`/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행된다. hook을 사용할 수 없으면 위 스킬을
직접 호출해 수동으로 재개할 수 있다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용한다.
[기록 형식·운영 계약](../../docs/reference/task-continuity.md)과
[검증 범위](../../evals/task-continuity/README.md)를 참고한다.
