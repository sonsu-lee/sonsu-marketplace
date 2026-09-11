---
name: fluent-english
description: Use when writing or editing natural English answers, reports, explanations, or documents, including code-work results and technical documentation. Preserve code, commands, logs, identifiers, required structure and formatting, and factual meaning. Select by the requested output language.
---

# Natural English output

Write English explanatory prose that fits the requested genre, audience, voice, and format. Do not change facts, required formatting or procedural order, certainty, or obligation while improving the wording. When a style preference conflicts with a preservation rule, preserve the source meaning and form.

## Scope

- Apply this guidance to the English portions of requested answers and documents, including implementation results, technical explanations, and technical documentation.
- Select it by the requested output language, not the language of the prompt.
- Do not translate or normalize foreign-language text, quotations, names, or established terms unless the user asks for that change.
- For code, code comments, commit messages, interface text, and other project-controlled strings, follow the user's request and the project's conventions before this guidance.
- This skill guides generated prose. It does not require a separate workspace, authorship detection, scoring, file output, or a multi-pass rewrite workflow.

## 작업 연속성 / Task continuity / 作業の継続

장문·여러 문서의 편집을 여러 단계로 진행하는 메인 controller는 같은 플러그인의
[task-continuity](../task-continuity/SKILL.md)를 적용한다. 다른 작업의 출력 문체 적용과 짧은 번역에는
별도 기록을 만들지 않는다. 파일 쓰기가 금지되면 checkpoint와 Git exclude도 변경하지 않는다.

## 표현 지침의 범위

요청된 언어의 어순·어휘·어조와 자연스러운 생략을 다룹니다. 문서 전체의 정보 순서와 장르별
양식은 사용자 또는 현재 작업을 맡은 스킬이 정한 구성을 따릅니다. 표현을 다듬기 위해 전체 문서를
다시 설계하거나 다른 스킬을 호출하는 단계를 만들지 않습니다.

Writing이나 Workflow와 함께 적용할 때에도 같은 초안에 필요한 지침을 한 번씩 반영합니다.
구성을 맡은 쪽으로 다시 호출을 돌리거나 언어별 재작성 작업을 별도로 만들지 않습니다.
단독으로 사용해도 요청 범위에서 작성·편집하며 다른 플러그인의 설치를 요구하지 않습니다.

## 내용과 형식 보존

입력에 있거나 그대로 포함하라고 지정된 다음 항목은 철자, 대소문자, 문장부호와 값을 바꾸지 않습니다.

- fenced code block과 fence, inline code
- 명령어, option, 환경 변수, 경로와 식별자
- API endpoint, HTTP method, 함수와 API signature, JSON/YAML key
- 로그와 오류 메시지, 버전, commit SHA와 ticket ID
- 수치, 날짜, 단위, URL과 Markdown link destination
- 직접 인용문, 보호 문자열과 literal

부분 수정이나 표현만 다듬는 요청에서는 지정 범위 밖의 제목·표·목록 순서를 유지합니다.
사용자가 자유 초안의 전체 재작성이나 형식 변경을 요청했고 Writing 등 현재 작성 담당이 그 범위에서
구성을 정했다면, 정해진 새 구성을 기준으로 표현을 다듬습니다. 이전 초안의 구조로 되돌리지 않습니다.
단독으로도 명시된 구조 변경 범위를 따르되, 고정 양식·필수 필드·HTML marker와 번호 절차의
실행 순서·조건은 문체 개선만으로 바꾸지 않습니다. 보호할 구조인지 불명확하면 유지합니다.
`Fixes`, `Closes`, `Part of`, `Ignore`와 ticket ID·Jira key·연결 URL은 실제 동작에 영향을 줄 수 있으므로
명시된 관계·문법·위치를 번역·치환·이동하거나 새로 만들지 않습니다.

표현 수정만으로 사실, 주장, 귀속, 인과 관계와 영향 범위를 추가하거나 삭제하지 않습니다.
요약을 명시적으로 요청받았다면 목적에 불필요한 정보를 생략할 수 있지만, 남긴 주장의 진위를
바꾸는 조건·예외·확실성은 보존합니다. 구성 담당이 정한 요약 범위를 임의로 되돌리거나 넓히지 않습니다. 부정과 긍정, 조건, 전제, 예외와 제한 범위를 유지합니다. 추측, 가능성, 확신과 불확실성의 정도를 바꾸지 않습니다. `must`, `should`, `may`에 해당하는 의무와 허용 수준도 유지합니다. 입력으로 뒷받침되지 않는 결론, 수치, 사례, 출처나 행위자를 만들지 않습니다.

## Actors and reference

- Keep an important actor, action, and target close enough that responsibility, permission, safety, and data flow are clear on one reading.
- Distinguish the reader from software and other users. When roles change or a pronoun could refer to more than one actor, use the verified role or component name. Keep a natural pronoun when its antecedent is clear.
- Use an imperative when the reader performs an instruction. Do not add `you` to headings, labels, status text, or every procedural sentence merely to state the implied subject.
- If the available information does not identify an actor or resolve a reference, do not invent one or present one possible interpretation as established fact.

## Voice, verbs, and modifiers

- Use active voice and a direct verb when they expose a verified actor or make responsibility clearer. Keep passive voice when the result or state is the topic, or when the actor is unknown, irrelevant, or intentionally de-emphasized.
- Replace a nominalized or weak verb phrase only when the direct form preserves the same technical meaning and makes the action easier to identify. Keep established concepts such as `authentication`, `configuration`, and `error handling` when they name the actual subject.
- Unpack a noun or modifier string only when its internal relationships have more than one plausible reading. Keep established compounds, official names, interface labels, and technical terms intact.
- When the intended scope is established, place limiting modifiers such as `only`, `just`, and `even` next to the phrase they govern if another position would change or obscure the claim. If the source does not establish the scope, do not choose one interpretation and present it as fact.

## Variety, register, and terminology

- Follow the requested or existing variety of English, including spelling, punctuation, formality, contractions, person, headings, and list conventions. Do not normalize American, British, or another regional convention without a reason grounded in the document.
- Prefer a direct, familiar word when it is equally precise. Keep an expert term, qualifier, or longer construction when it carries a necessary distinction, condition, rationale, risk, or uncertainty.
- Use connected sentences for explanatory body prose. Allow natural fragments in headings, interface labels, tables, lists, and short status text where the format supplies the missing relationship.
- Use one established project term for one concept. Do not rotate among near-synonyms for variety when readers could infer different components or states. Preserve exact product names and interface labels.
- For an international audience or content intended for localization, avoid adding culture-specific idioms, slang, unexplained abbreviations, or ambiguous date expressions. Do not apply this as a blanket ban on natural English, contractions, or established phrasal verbs such as `log in`, `sign in`, and `set up`.

## Final check

After drafting, adjust a passage only when one or more of these patterns are conspicuous and make the result less clear or less faithful to the requested voice:

- an empty preamble delays the requested point;
- an unsupported importance claim, sales phrase, or vague attribution substitutes for evidence;
- synonym cycling makes one project concept appear to be several;
- a formulaic contrast, unraised objection, or unused alternative adds no real distinction;
- a closing paragraph repeats the result without adding a constraint, consequence, or next action;
- repeated sentence openings, shapes, or clipped fragments draw more attention than the content.

Do not treat a single word, transition, dash, colon, fragment, or passive construction as evidence of a problem. Keep real alternatives and objections, deliberate repetition, useful setup, safety language, and distinctive voice. Do not add a fact, source, example, number, opinion, or personal experience to make the prose seem more human. If an adjustment would weaken precision, attribution, polarity, certainty, obligation, terminology, or required formatting, leave the original expression in place.
