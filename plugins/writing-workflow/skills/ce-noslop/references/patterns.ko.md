# 패턴 카탈로그

> 영문 정본: [patterns.md](patterns.md) (`cc7d4c5` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

규칙 번호는 고정된 id다. 규칙을 삭제하면 빈 번호가 남으며, 번호를 다시 매기지
않는다. 각 규칙은 패턴과 고치는 법을 적는다. 한 구절이 발견 사항인지는
[SKILL.md](../SKILL.md)의 검사가 판단하고, 이 카탈로그는 무엇을 찾아야 하는지와
대신 무엇을 써야 하는지를 알려 준다. 아래 영어 예시는 원문 그대로 둔다.

**오탐 하한.** 장치 하나는 선택이지 티가 아니다. 패턴이 쌓일 때만 구절을
발견 사항으로 표시하고(SKILL.md 검사 5), 다음은 절대 표시하지 않는다. 따옴표,
제목, 코드 안의 텍스트. 도메인에서 정확히 한 가지 뜻으로 쓰는 용어. 강조를 위한
의도적 반복. 범위 설명, 안전 공지, 실제 정정. 강조용 짧은 문장 하나. 편지의
제목이나 맺음말.

## 내용

- **1. 과장.** 평범한 사실에 중요성 주장을 덧붙인 것: "marks a turning
   point", "plays a vital role", "a testament to", "in today's landscape".
   주장을 지우고 사실만 남긴다.
- **2. 끝에 붙는 -ing 분석.** 의미를 설명하는 절이 문장 끝에 덧붙은 것:
   "highlighting", "ensuring", "reflecting", "showcasing", "underscoring".
   그 절을 지운다. 문장은 남는다.
- **3. 홍보성 형용사.** "Vibrant", "seamless", "robust", "groundbreaking",
   "stunning", "thoughtfully designed", "powerful yet simple". 속성을
   구체적으로 적거나 주장을 지운다.
- **4. 모호한 출처.** "Experts believe", "industry reports suggest",
   "widely regarded", "studies show". 출처를 밝히거나 주장을 뺀다. 출처를
   지어내지 않는다.
- **5. 틀에 박힌 전망.** "Despite challenges, continues to thrive"나 밝은
   미래를 이야기하는 마지막 문단. 실제 한계나 계획 하나를 담백하게 남기고,
   마지막 구체적 사실에서 끝낸다.
- **6. 설정-반전 문구.** "Ten features. Zero headaches." "Everything changed.
   Your invoice didn't." 대상이 하는 일을 적는다. 반전이 문장을 떠받치고
   있었다면 그 문장에는 내용이 없었던 것이다.
- **7. 가짜 통찰.** "The part everyone misses", "what nobody tells you",
   "the real question is", "at its core". 도입부를 잘라 내고 주장이 홀로
   서게 한다.
- **8. 메타담론.** "This matters more than it sounds", "the key point is",
   "as you can see", 불분명한 곳이 없는데 쓴 "in other words". 곁말을 지운다.
   요점이 불분명하다면 그 대신 근거를 더한다.
- **9. 아무도 꺼내지 않은 대안 배척.** "A tempting approach would be",
   "some might say", "this isn't about X". 가짜 선택지를 치우고 실제 제약을
   적는다.

## 언어

- **10. 모델 어휘.** Delve, tapestry, testament, underscore, showcase, garner,
    interplay, intricate, enduring, foster, crucial, pivotal, additionally,
    moreover, enhance, leverage, utilize, facilitate, 추상어로 쓴 landscape,
    realm, journey. 실제 주장에 맞는 평범한 단어를 쓴다.
- **11. 치장한 연결 동사.** 문장이 "이다"나 "가지고 있다"를 뜻하는데 쓴 "Acts
    as", "functions as", "serves as", "offers", "boasts", "represents". 짧은
    동사를 쓴다.
- **12. X가 아니라 Y.** "It's not just a linter, it's a system." "The question
    isn't A, it's B." 아무도 X라고 주장하지 않았다. Y를 적는다.
- **13. 억지 3항.** 자연스러운 개수가 하나나 둘인데 형용사, 예시, 박자를 셋
    채운 것. 참이고 구체적인 항목만 남긴다.
- **14. 동의어 돌려쓰기.** 한 구절에서 같은 대상을 세 가지 이름으로 부른 것.
    용어 하나를 골라 반복한다. 기술 문서에서 반복은 정확성이다.
- **15. 사실은 목록인 범위 표현.** onboarding과 billing이 어떤 범위의 양 끝이
    아니라 별개의 두 항목인데 쓴 "From onboarding to billing". 항목을
    그대로 적는다.
- **16. 군더더기.** "In order to"는 "to"다. "Due to the fact that"은
    "because"다. "It is important to note that"은 없는 것과 같다. "At this
    point in time"은 "now"다.
- **17. 겹쳐 쌓은 완곡 표현.** "Could potentially possibly"는 "may"다. 완곡
    표현은 하나만, 불확실성이 실제로 있을 때만 쓴다.
- **18. 동사 일을 대신하는 부사.** "Runs quickly"는 "finishes in 40 ms"가
    된다. "significantly improves"는 측정된 변화가 된다. 부사가 의미를
    담고 있다면 동사를 바꾸거나 숫자를 제시한다.
- **19. 명사화.** "The demotion of the grid is the change"는 "demote the
    grid"다. 동사를 선호한다.
- **20. 평범한 작업에 빌려 쓴 은유.** 코드의 평범한 동작 자리에 물리학, 전략,
    기계에서 가져온 말을 쓴 것. 메서드인 "vector", API인 "surface", 함수인
    "primitive", 변경인 "lever"나 "wedge", 목표인 "north star", 피드백
    루프인 "flywheel", 옮기는 중인 코드를 가리키는 "evacuating". 동작이나
    대상의 이름을 적는다.
- **21. 작동 방식 대신 느낌.** "Deploys feel effortless", "errors are handled
    gracefully", "the API gets out of your way". 독자가 할 수 있거나 확인할 수
    있는 것을 적는다. "a failed deploy rolls back within one minute", "a
    malformed row is skipped and logged with its line number".

## 구조

- **22. 빽빽한 문장.** 독자가 두 번 해석해야 하는 문장. 문장마다 한 가지
    생각만 담는다. 세미콜론으로 이어진 사슬은 목록으로 바꾼다.
- **23. 행위자를 숨기는 수동태.** "Queries are validated"는 누가 검증하는지
    독자가 짐작하게 한다. "the compiler validates queries"는 그렇지 않다.
    행위자를 밝혀도 얻을 것이 없을 때만 수동태를 유지한다.
- **24. 묻힌 결정.** 결론이 근거 뒤에 나온다. 결론, 이유, 배경 순으로 쓴다.
- **25. 첫 문장에서 반복한 제목.** 반복을 지우고 내용으로 시작한다.
- **26. 요약 반복 결말.** "In conclusion", "overall", 글을 그대로 반복하는
    문단. 마지막 구체적 요점이나 다음 행동에서 끝낸다.
- **27. 극적인 단문 나열.** "No priors. No nostalgia. The old rules were
    gone." 짧은 문장 하나는 요점을 찍을 수 있지만, 줄줄이 늘어놓으면 연출이다.
    문장으로 고쳐 쓴다.
- **28. 콜론 공개.** "The detail that makes it work: a separate grader."
    콜론은 목록이나 인용 앞에 쓰는 것이다. 극적 효과나 문장 중간 연결어로
    쓰지 않는다.

## 서식

- **29. 리듬 보조용 엠 대시.** 문단마다 여러 개 있거나, 틀에 박힌 "this isn't
    X — it's Y". 마침표나 쉼표를 쓰거나 문장을 나눈다. 세미콜론은 대안이
    아니다. 코드, 범위, 표 안의 대시는 그대로 둔다.
- **30. 자기 줄을 되풀이하는 굵은 라벨.** "**Performance:** performance
    improved." 산문으로 바꾼다. 굵은 머리말은 뒤따르는 문장이 라벨에 없던
    내용을 말할 때만 남긴다.
- **31. 강조용으로 뿌린 굵은 글씨.** 모든 고유명사나 약어를 굵게 쓴 것. 독자가
    찾아야 하는 것만 굵게 쓴다.
- **32. Title Case 제목.** 문장형 대소문자(Sentence case)를 쓴다.
- **33. 장식용 이모지.** 제목과 글머리 기호에 쓴 이모지. 호출자의 계약이 고정한
    경우가 아니면 제거한다.
- **34. 두 문장짜리 산문이 더 읽기 좋은 곳의 글머리 기호.** 두 문장짜리 절 위의
    제목, 짧은 문서의 모든 절 사이에 넣은 가로선. 서식은 내용을 따른다.
- **35. 섞인 곡선 따옴표.** 직선 따옴표와 곡선 따옴표가 섞인 것. 기술 문서에는
    직선 따옴표를 쓴다.

## 챗봇 흔적

- **36. 챗봇식 시작과 맺음.** "Certainly", "Great question", "Happy to help",
    "Let me know if you need anything else", "Want me to". 지우고 내용을
    적는다.
- **37. 아첨.** 답 앞에 붙은 "You're absolutely right". 답한다.
- **38. 다음 요점 예고.** "Let's dive in", "here's what you need to know",
    "without further ado". 요점을 적는다.
- **39. 보고서 속 과정 서술.** 독자의 다음 행동을 바꾸지 않는 에이전트의 작업
    단계. 배제된 원인이나 실패한 수정은 발견 사항으로 적어 남기고, 에이전트가
    시간을 어떻게 썼는지에 대한 설명은 뺀다.
- **40. 지식 한계 면책과 빈틈 메우기.** "While details are limited, it
    likely..." 원문이 보여 주지 않는 것을 적거나 문장을 뺀다. 추측을 사실처럼
    제시하지 않는다.
- **41. 꾸며낸 철저함.** 단순한 개수("resolved 11 threads"), 점수표, 확인한 것을
    전부 나열한 목록. 무엇을 결정했고 이유가 무엇인지 적는다. 일상적이지 않은
    결정이 없었다면 아무 말도 하지 않는다.
