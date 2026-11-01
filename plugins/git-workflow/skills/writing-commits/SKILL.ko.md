# 커밋 작성하기

> 영문 정본: [SKILL.md](SKILL.md) (`4d5fb44` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

저장소의 커밋 메시지 규칙을 확인하고 따른다. 여기에는 commitlint 설정도
포함한다. 저장소에 규칙이 없는 부분에는 아래 기본값을 사용한다.

## 메시지 규칙

실제 변경 내용을 바탕으로 메시지를 쓴다. Conventional Commits를 사용한다.

```text
<type>(<scope>): <subject>

<body>

<footers>
```

* **Type:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`,
  `chore`, `style`, `revert` 중 하나.
* **Scope:** 선택 사항. 변경되는 부분의 이름을 소문자로 쓴다.
* **Subject:** 구체적인 변경을 명령형으로 설명한다. 소문자로 시작하고 끝에
  마침표를 붙이지 않는다. 첫 줄 전체를 72자 이내로 하고, 그 줄만으로도 의미가
  통하게 한다.
* **Body:** 변경이 왜 필요한지, 그리고 diff만으로는 드러나지 않는 중요한 맥락이나
  제약을 설명한다. subject만으로 충분하면 생략한다. 변경으로 확인되지 않는
  이유를 지어내지 않는다.
* **Body와 footer:** 앞 섹션과 빈 줄로 구분하고 72열에서 줄바꿈한다.
* **호환성을 깨는 변경:** 콜론 앞에 `!`를 붙이거나 `BREAKING-CHANGE:` footer를
  추가하거나 둘 다 쓴다. 무엇이 깨지는지, 호출하는 쪽이 어떻게 적응해야 하는지
  설명한다.

## 필수 검증

커밋을 만들거나 수정하기 전, 또는 메시지를 완성본으로 제시하기 전에 제안하는
메시지 전체를 검증한다. 메시지를 수정할 때마다 검증을 다시 실행한다.
[검증 절차](references/validation.md)에 따라 실행기와 설정을 각각 독립적으로
선택한다.

1. 저장소에 이미 있는 검증 명령, 도구, 버전을 먼저 사용한다. commitlint가 아닌
   검증기도 마찬가지다. 의존성이 없으면 문서화된 설치 방법을 따른다. 설정된
   도구를 사용할 수 없거나 실패한다고 해서 검증기를 바꿔도 되는 것은 아니다.
2. 실행 환경이 정해져 있지 않은 경우에만 버전을 고정한 commitlint CLI를 `npx`로
   실행한다. 저장소 설정이 있으면 유지한다.
3. 설정이 정해져 있지 않은 경우에만 commitlint와 함께
   [번들 ESM 기본값](assets/commitlint.config.mjs)을 사용한다. 다른 검증기의
   설정을 이 파일로 대체하지 않는다.

의도적인 경고 수준을 포함해 저장소의 통과 기준을 따른다. 대체 수단을 도입하려고
실패한 검사를 우회하거나 hook, CI job, 프로젝트 의존성을 설치하지 않는다.
검증이 통과했다고 주장하지 말고 막힌 점을 보고한다. 이미 있는 hook은 실행되기
전에는 초안을 검증하지 않는다.

번들 기본값은 type, 소문자 scope, subject 형식, 빈 줄 구분, 72자 제한을
검사한다. 정확성, 이유 설명, 명령형 표현, 첫 글자 소문자, 호환성을 깨는 변경에
대한 설명은 별도로 검토한다. body 길이 규칙은 URL이 포함된 줄을 예외로 하므로 그런
줄은 직접 확인한다. 저장소 검증기가 검사하지 않는 스킬 기본값도, 저장소의 명시적
규칙을 덮어쓰지 않는 범위에서 검토한다.

## 예시

```text
feat(api)!: return timestamps in UTC

Responses used server-local time without an offset, so clients could
interpret the same timestamp differently. Return ISO 8601 timestamps
with an explicit UTC offset instead.

BREAKING-CHANGE: created_at and updated_at now include a UTC offset.
Replace parsers that expect the previous offset-free format.
```
