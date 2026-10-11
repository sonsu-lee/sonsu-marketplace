# 커밋 메시지 규칙

`git:commit`의 메시지, `git:write-pr`의 PR 제목, `review:review-code`의 커밋 검토가 함께 쓰는 규칙이다.
저장소가 commitlint 설정·CONTRIBUTING 등으로 자체 커밋 규칙을 문서화했으면 그 규칙을 따른다. 없으면 아래를 따른다.

## Conventional Commits 1.0.0

출처: https://www.conventionalcommits.org/en/v1.0.0/ (CC BY 3.0, https://creativecommons.org/licenses/by/3.0/). 아래 구조와 명세 1–16은 원문 그대로다.

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

1. Commits MUST be prefixed with a type, which consists of a noun, `feat`, `fix`, etc., followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED terminal colon and space.
2. The type `feat` MUST be used when a commit adds a new feature to your application or library.
3. The type `fix` MUST be used when a commit represents a bug fix for your application.
4. A scope MAY be provided after a type. A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):`
5. A description MUST immediately follow the colon and space after the type/scope prefix. The description is a short summary of the code changes, e.g., *fix: array parsing issue when multiple spaces were contained in string*.
6. A longer commit body MAY be provided after the short description, providing additional contextual information about the code changes. The body MUST begin one blank line after the description.
7. A commit body is free-form and MAY consist of any number of newline separated paragraphs.
8. One or more footers MAY be provided one blank line after the body. Each footer MUST consist of a word token, followed by either a `:<space>` or `<space>#` separator, followed by a string value (this is inspired by the [git trailer convention](https://git-scm.com/docs/git-interpret-trailers)).
9. A footer’s token MUST use `-` in place of whitespace characters, e.g., `Acked-by` (this helps differentiate the footer section from a multi-paragraph body). An exception is made for `BREAKING CHANGE`, which MAY also be used as a token.
10. A footer’s value MAY contain spaces and newlines, and parsing MUST terminate when the next valid footer token/separator pair is observed.
11. Breaking changes MUST be indicated in the type/scope prefix of a commit, or as an entry in the footer.
12. If included as a footer, a breaking change MUST consist of the uppercase text BREAKING CHANGE, followed by a colon, space, and description, e.g., *BREAKING CHANGE: environment variables now take precedence over config files*.
13. If included in the type/scope prefix, breaking changes MUST be indicated by a `!` immediately before the `:`. If `!` is used, `BREAKING CHANGE:` MAY be omitted from the footer section, and the commit description SHALL be used to describe the breaking change.
14. Types other than `feat` and `fix` MAY be used in your commit messages, e.g., *docs: update ref docs.*
15. The units of information that make up Conventional Commits MUST NOT be treated as case-sensitive by implementors, with the exception of BREAKING CHANGE which MUST be uppercase.
16. BREAKING-CHANGE MUST be synonymous with BREAKING CHANGE, when used as a token in a footer.

## 확장 규칙

명세 FAQ가 팀별 확장을 권장하므로, 아래 규칙이 명세보다 우선한다.

- **E1** type은 아래 목록으로 고정한다. 이 밖의 type은 쓰지 않는다.
  - `feat`: 새 기능·동작 추가, 변경, 제거
  - `fix`: 잘못된 동작 수정
  - `refactor`: 동작을 바꾸지 않는 구조 변경
  - `perf`: 성능 개선
  - `docs`: 문서만 변경
  - `test`: 테스트만 추가·수정
  - `build`: 빌드 시스템, 의존성
  - `ci`: CI 설정
  - `chore`: 그 밖의 유지 관리(설정, 생성물)
  - `revert`: 되돌림. footer에 `Refs: <SHA>`를 쓴다.
- **E2** 헤더는 `<type>[(<scope>)][!]: <description>`이다.
  - type은 소문자다. scope는 선택이며 코드베이스 영역을 가리키는 소문자 명사다.
  - description은 명령형으로 쓴다. 영어는 소문자로 시작하고 마침표를 붙이지 않는다. 한국어·일본어는 명사형으로 끝낸다(예: `fix(session): 만료 시각 경계 판정 수정`).
  - 헤더 전체는 72자 이하다.
- **E3** 본문에 변경 이유를 쓴다. 헤더만으로 이유가 자명한 오타·포맷·생성물 갱신만 본문을 생략한다.
- **E4** breaking change는 `!`와 `BREAKING CHANGE: <설명>` footer를 둘 다 쓴다. 쓸 때는 `BREAKING CHANGE`만 쓰고, `BREAKING-CHANGE`는 읽을 때만 같은 뜻으로 인정한다.
- **E5** 커밋 하나에 type 하나다. 여러 type에 해당하면 커밋을 나눈다.
- **E6** 티켓은 footer의 `Refs: <ID>`로만 참조한다. 헤더와 브랜치 이름에는 넣지 않는다. GitHub 이슈를 닫는 키워드는 PR 본문에 쓴다.

## 언어를 정한다

다음 순서로 처음 근거가 있는 단계의 언어를 쓴다. type과 footer token은 언어와 관계없이 영어로 둔다.

1. 사용자 지정
2. 저장소가 명시한 규칙: `CONTRIBUTING*`, `commitlint.config.*`·`.commitlintrc*`, `AGENTS.md`·`CLAUDE.md`, `.github/` 안내
3. 영어

과거 커밋의 언어는 근거로 쓰지 않는다. 대화 언어도 근거가 아니다.

## 본문

E3에 따라 변경 이유를 쓴다. 특히 다음은 빠뜨리지 않는다.

- 자명하지 않은 결정
- 버그의 원인
- 버린 대안
- 호환성·마이그레이션 영향

순서는 지금 코드의 문제(현재형) → 이 방식을 택한 이유 → 버린 대안 → 부작용이다. 72자에서 줄을 바꾼다.

파일 목록, diff를 문장으로 옮긴 설명, 테스트 개수, 작업 경위는 쓰지 않는다.

## AI 사용 표기

[문장 형식 기준](tracker-prose.md#ai-사용-표기)을 따른다.

## 예시

다음은 이 저장소의 기준을 설명하려고 만든 로컬 예시다.

```text
feat(config)!: replace timeoutMs with timeout in seconds

Every caller passed whole seconds and multiplied by 1000, and two
callers passed seconds where milliseconds were expected.

BREAKING CHANGE: `timeoutMs` is removed; set `timeout` in seconds.
Refs: ENG-7
```

```text
revert: restore the previous retry interval

The 5s interval doubled the load on the upstream service during the
2026-10-02 incident.

Refs: 676104e
```

결정된 언어가 한국어면 헤더를 `fix(session): 만료 시각 경계 판정 수정`처럼 명사형으로 끝낸다.

나쁜 예:

```text
update hook files
```

무엇이 달라지는지 알 수 없고, 형식과 이유가 모두 빠졌다.
