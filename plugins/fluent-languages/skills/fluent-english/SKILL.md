---
name: fluent-english
description: Use when writing or editing natural English answers, reports, explanations, or documents, including code-work results and technical documentation. Preserve code, commands, logs, identifiers, required structure and formatting, and factual meaning. Select by the requested output language.
---

# Natural English output

Write English explanatory prose that fits the requested genre, audience, voice, and format. Do not change facts, required formatting or ordered structures, certainty, or obligation while improving the wording. When a style preference conflicts with a preservation rule, preserve the source meaning and form.

## Scope

- Apply this guidance to the English portions of requested answers and documents, including implementation results, technical explanations, and technical documentation.
- Select it by the requested output language, not the language of the prompt.
- Do not translate or normalize foreign-language text, quotations, names, or established terms unless the user asks for that change.
- For code, code comments, commit messages, interface text, and other project-controlled strings, follow the user's request and the project's conventions before this guidance.
- This skill guides generated prose. It does not require a separate workspace, authorship detection, scoring, file output, or a multi-pass rewrite workflow.

## 공통 의사소통 원칙

- 사용자가 요청한 내용, 독자, 목적, 장르, 어조와 출력 형식을 따릅니다.
- 과업에 필요한 원인, 조건, 근거, 대조, 순서와 귀속 관계를 독자가 복원할 수 있게 구성합니다.
- 과업상 중요한 행위자와 대상이 문맥에서 안정적으로 복원되게 합니다.
- 관련 정보를 묶고, 독자가 필요한 정보를 찾고 사용할 수 있도록 장르와 과업에 맞는 순서를 선택합니다.
- 불필요한 추론 부담은 줄이되, 해당 언어와 장르에서 자연스러운 생략과 관습을 강제로 제거하지 않습니다.
- 문단 구분, 접속어, 반복, 주어 표현과 결론 위치는 위 목표를 실현하는 수단입니다. 항상 결론부터 쓰거나 특정 문장·문단 길이를 맞추는 고정 형식으로 강제하지 않습니다.

## 내용과 형식 보존

입력에 있거나 그대로 포함하라고 지정된 다음 항목은 철자, 대소문자, 문장부호와 값을 바꾸지 않습니다.

- fenced code block과 fence, inline code
- 명령어, option, 환경 변수, 경로와 식별자
- API endpoint, HTTP method, 함수와 API signature, JSON/YAML key
- 로그와 오류 메시지, 버전, commit SHA와 ticket ID
- 수치, 날짜, 단위, URL과 Markdown link destination
- 직접 인용문, 보호 문자열과 literal

요청되거나 입력에 주어진 제목 계층, 표의 형태와 의미, 불릿과 번호 목록의 종류와 순서를 유지합니다. 번호 절차의 단계 수와 실행 순서를 바꾸거나 합치지 않습니다. 형식 변경 요청이 없다면 표, 목록과 절차를 산문으로 바꾸지 않습니다.

사실, 주장, 귀속, 인과 관계와 영향 범위를 추가하거나 삭제하지 않습니다. 부정과 긍정, 조건, 전제, 예외와 제한 범위를 유지합니다. 추측, 가능성, 확신과 불확실성의 정도를 바꾸지 않습니다. `must`, `should`, `may`에 해당하는 의무와 허용 수준도 유지합니다. 입력으로 뒷받침되지 않는 결론, 수치, 사례, 출처나 행위자를 만들지 않습니다.

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
