# writing-workflow

[English](README.md) | 한국어

> 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
> 영문판을 따른다.

의미와 작성자의 목소리를 보존하면서 자연스러운 한국어, 영어, 일본어 글을 쓰고
다듬는다.

세 가지 원본 기반 스킬이 언어별 편집 워크플로를 하나씩 제공한다. 이 플러그인은
텍스트를 자동으로 번역하거나, 프로젝트 전체의 스타일 규칙을 설정하거나, 문서를
사람과 AI 중 누가 썼는지 판별하지 않는다.

## 목차

- [설치](#설치)
  - [의존성](#의존성)
- [사용법](#사용법)
  - [CLI](#cli)
  - [스킬과 범위](#스킬과-범위)
- [업스트림 출처](#업스트림-출처)
- [기여](#기여)
- [라이선스](#라이선스)

## 설치

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install writing-workflow@sonsu-marketplace
```

Codex에는 같은 패키지를 설치한다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin add writing-workflow@sonsu-marketplace
```

Claude Code에서는 다음과 같이 설치한다.

```sh
claude plugin marketplace add sonsu-lee/sonsu-marketplace
claude plugin install writing-workflow@sonsu-marketplace
```

### 의존성

- 먼저 [omp](https://github.com/can1357/oh-my-pi),
  [Codex](https://developers.openai.com/codex/cli) 또는
  [Claude Code](https://code.claude.com/docs/en/overview)를 설치한다.
- 한국어 검사에는 Python 3.10 이상이 필요하다.
- 일본어 검사에는 Python 3.10 이상과 [uv](https://docs.astral.sh/uv/)가
  필요하다. 주요 린터는 SudachiPy와 그 사전을 사용하며, 캐시 없이 처음 실행할
  때는 네트워크 접근이 필요하다. uv가 없는 환경을 위한 수동 체크리스트 방법은
  스킬에 설명되어 있다.
- 영어 스킬에는 외부 실행 파일이나 서비스가 필요하지 않다.

필수 도구는 별도로 설치한다. 글을 편집하기 위해 프로젝트의 기존 도구 설정을
변경하지 않는다.

## 사용법

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details writing-workflow
```

지원되는 클라이언트에서 자연어로 글쓰기 작업을 요청한다.

```text
Refine this Korean API guide without changing its commands, identifiers,
response codes, numbers, terminology, or level of certainty.

Write an English email from these notes. Keep the commitments and dates exact
and use the same friendly, direct tone as the supplied writing sample.

Draft a Japanese explanation from these notes, then check its readability.
Do not invent a conclusion or strengthen an unconfirmed claim.
```

요청 언어가 아니라 결과물의 언어에 맞는 스킬을 사용한다. 여러 언어가 섞인
문서에서는 편집 요청이 없는 한 다른 언어의 문단을 보존한다. 각 문단에는 편집
워크플로를 하나만 적용한다.

Codex에서는 `$writing-workflow:humanize-korean`,
`$writing-workflow:ce-noslop`, `$writing-workflow:natural-japanese`를 명시적으로
선택할 수도 있다. Claude Code에서는 `/writing-workflow:humanize-korean`,
`/writing-workflow:ce-noslop`, `/writing-workflow:natural-japanese`를 사용한다.
자연어를 통한 선택은 설치 훅이 아니라 모델의 동작이므로, 플러그인 목록에 나온다고
스킬 실행이 증명되는 것은 아니다. 모든 클라이언트는 같은 규칙, 역할, 스크립트,
에셋을 사용한다. 리소스는 대상 저장소나 추측한 캐시 경로가 아니라 실제 로드된
`SKILL.md` 디렉터리에서 찾는다. Codex는 일반 파일 경로를 사용하고 Claude Code는
디렉터리를 `Base directory for this skill`로 표시한다. omp의 `skill://`는 읽기
편의를 위한 것이다. Python과 uv에는 항상 절대 파일 시스템 경로를 전달한다.

### 스킬과 범위

- [humanize-korean](skills/humanize-korean/SKILL.md)은 기존 한국어 글을 다듬는다.
  새 글은 먼저 사용자의 메모나 허용된 출처를 바탕으로 초안을 작성한 다음 편집
  워크플로를 적용한다. README 파일, API 레퍼런스, 설계 문서, 런북, 릴리스 노트,
  기술 블로그, 코드가 포함된 문서의 산문 등 기술 문서도 대상이다. 코드, 식별자,
  명령어, URL, 숫자, 직접 인용문, 기술 용어는 보호하되 주변 산문은 편집 대상에서
  제외하지 않는다. 기본 프롬프트는 간결하게 유지한다. 심화 경로 절차와 출처
  기록은 별도 참조 자료이며 심화 경로나 각색 감사에만 읽는다.
- [ce-noslop](skills/ce-noslop/SKILL.md)은 영어 글을 쓰고 편집하거나 진단한다.
  중립적인 업무 산출물과 사용자의 고유한 목소리를 구분하고 사실과 불확실성을
  보존한다.
- [natural-japanese](skills/natural-japanese/SKILL.md)는 장르별 지침과 선택적인
  작성자 스타일 프로필을 활용해 일본어 글을 쓰고 편집하거나 진단한다. 기계적
  검사 결과에는 맥락에 따른 판단이 필요하다. 기본 프롬프트는 간결하게 유지한다.
  점수 산정 절차, 글쓰기 원칙, 문단 검토, 수정 한계, 가독성 검토, 마무리 및
  실행 환경 참고 사항, 작성자 프로필, 출처 기록은 각각 별도의 참조 자료이며
  스킬의 설명에 따라 모드, 검사 결과 또는 작업에 맞춰 불러온다.

명확한 글쓰기에 구어체가 필요한 것은 아니다. 요청된 격식, 독자, 문서 목적과
의미 있는 기술적 구조를 유지한다. 기계적 검사를 통과했다고 해서 수정본이 더
자연스럽거나 모든 의미가 보존되었다는 뜻은 아니다. 실제 결과물을 원문과 비교해
검토한다. 한국어 수치 검사는 단위 표현이 아니라 부호가 있는 값을 비교한다. 단위
보존은 여전히 원문과 결과물을 직접 비교해 검토해야 하며, 플러그인은 단위
레지스트리나 수량 변환 엔진을 추가하지 않는다.

한국어 도우미는 기술 산문의 지표 대용으로 `report`를 사용하며, 기술 문서에
맞게 보정된 전용 기준선은 없다. 수치 점수를 높이려고 정당한 용어나 구조를
수정하지 않는다. 일본어 각색본에는 업스트림의 실험적 의미 모델이나 `exp` 모드가
포함되지 않는다.

## 업스트림 출처

이는 고정된 업스트림 리비전의 로컬 각색본이며 자동 미러가 아니다. 지침은
영어로 작성되었고 한국어와 일본어 예시는 원래 언어를 유지한다. 원본 라이선스는
각 스킬에 포함되어 있다.

- **humanize-korean:** [epoko77-ai/im-not-ai][ko-source], 리비전
  `b37e0206d31fffd9149bf57168d4d62eb2086bee`. omp, Codex, Claude Code에서
  독립적으로 사용할 수 있도록 각색했으며 기술 문서를 명시적으로 포함해 모든
  한국어 산문 장르에 적용한다. 번호가 매겨진 절차 단계는 편집할 수 있으며 실제
  참조된 각주는 보호한다.
- **ce-noslop:** [EveryInc/compound-engineering-plugin][en-source], 리비전
  `2e41b4490a37f53db0beb6d4904618da9af2f559`. 이 모음에서는 영어로 범위를
  제한했으며 지원되지 않는 클라이언트 메타데이터와 설치되지 않은 다른 스킬의
  의존성을 제거했다.
- **natural-japanese:** [coji/natural-japanese][ja-source], 리비전
  `03bc944a0c4a9f0b2a66eab065b30de5c529bf08`. 이식 가능한 메타데이터, 영어
  지침, 자체 완결적인 스킬 리소스를 사용하도록 각색했다.

## 기여

[마켓플레이스 저장소](https://github.com/sonsu-lee/sonsu-marketplace/issues)에서
질문과 풀 리퀘스트를 환영한다.
[작성 및 테스트 절차](../../CONTRIBUTING.md#adding-a-plugin)를 따른다. 각색본을
업데이트할 때는 업스트림 고지와 리비전 참조를 유지한다. 별도의 임시 홈을
사용한다. omp에는 `HOME`, Codex에는 `HOME`과 `CODEX_HOME`, Claude Code에는
`HOME`과 `CLAUDE_CONFIG_DIR`을 사용한다. 실제로 사용하는 클라이언트에 테스트
플러그인을 설치하거나 실제 설정 또는 자격 증명을 복사하지 않는다. 검색, 모델
접근, 누락된 리소스 검사는 루트의
[테스트 절차](../../CONTRIBUTING.md#testing-a-plugin)를 따른다. 형식과 검색을
검사하는 것과 별도로 산문과 보호 콘텐츠의 경계를 검사한다.

마켓플레이스 루트에서 한국어와 일본어 회귀 테스트를 실행한다.

```sh
uv run --with 'sudachipy>=0.6.8' --with 'sudachidict-core>=20240409' \
  python -B -m unittest discover -s plugins/writing-workflow/tests -v
```

이 테스트 모음은 일본어 실행 환경의 기존 의존성을 사용한다. 한국어 보호 콘텐츠의
충실도와 일본어 구조 린트 및 기준선 전환을 검사한다.

## 라이선스

마켓플레이스 각색본에는 [MIT](../../LICENSE) 라이선스가 적용되며 저작권은
sonsu-lee에 있다. 업스트림 부분은 각각의 MIT 고지를 유지한다.
[epoko77-ai](skills/humanize-korean/LICENSE),
[Every](skills/ce-noslop/LICENSE), [coji](skills/natural-japanese/LICENSE).

[ko-source]: https://github.com/epoko77-ai/im-not-ai/tree/b37e0206d31fffd9149bf57168d4d62eb2086bee
[en-source]: https://github.com/EveryInc/compound-engineering-plugin/tree/2e41b4490a37f53db0beb6d4904618da9af2f559/skills/ce-noslop
[ja-source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
