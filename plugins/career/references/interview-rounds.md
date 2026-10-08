# 면접 라운드 기준

`write-career-documents`, `prepare-interview`, `mock-interview`, `interview-retro`가 함께 읽는다.
여기에 적은 흐름은 일반적인 패턴이다. 초대 메일이나 채용 담당자가 알려 준 실제 라운드 정보가 있으면
항상 그 정보가 우선한다. round 값은 [작업 공간 계약](workspace.md)의 고정 어휘를 쓴다.

## 서류 심사 단계

면접 전에 서류 심사가 있다.

- 서류는 대개 HR이 본다. HR은 개발팀에서 받은 요구사항 체크리스트와 서류 문구가 일치하는지로
  통과를 정한다.
- 1차 기술 면접관은 면접 직전이나 면접 중에 서류를 펼쳐 질문을 고른다.
- 이 흐름이 `write-career-documents`의 두 독자 규칙과 `prepare-interview`의 제출 서류 심층 질문의
  근거다.

## US 라운드

출처: [Tech Interview Handbook interview guide](https://www.techinterviewhandbook.org/software-engineering-interview-guide/),
career-ops(`24745c5f8a6b2ee56d7c25176d05c4dfe97c5b3b`)의 라운드별 평가자 구분. 관점만 참고해 요약한다.

- `recruiter`(recruiter screen): 15~30분이다. 동기, 일정, 연봉, 취업 자격을 확인한다. 평가자는
  채용 담당자다.
- technical phone screen: 공유 에디터에서 코딩한다. 프론트엔드는 JS, DOM, UI 컴포넌트 구현이
  나온다. 이 플러그인은 말로 풀이 과정을 설명하는 연습만 지원하고, 코드를 실행하거나 채점하지 않는다.
- take-home: 드물다.
- `onsite`(onsite/virtual loop): 여러 세션을 하루나 며칠에 걸쳐 본다.
  - coding
  - `system-design`: mid/senior 프론트엔드는 FE system design이 나온다.
    [프론트엔드 시스템 설계](frontend-system-design.md)를 따른다.
  - `behavioral`: 과거 행동을 STAR+R로 묻는다.
  - `hiring-manager`: why this role/now, 맡을 범위, 첫 90일을 묻는다. 평가자는 채용 매니저다.
- `technical`: 경험 심층 라운드다. 현직 엔지니어가 서류와 경험을 펼쳐 놓고 왜, 어떻게 측정했나,
  대안과 트레이드오프를 연쇄로 묻는다.

## JP 라운드

아래는 일반적 패턴이다. 결과물에 쓸 때는 `[일반적 흐름]`으로 표시하고, 실제 초대 정보가 우선한다.

- `casual`(カジュアル面談): 평가가 없다고 안내되더라도 평가가 없지 않다. 지원 동기와 이직 사유의
  윤곽, 조건이 기록된다.
- `first`(一次): 현장 엔지니어나 매니저가 본다. 기술과 경험을 깊이 묻는다.
- `second`(二次): 부장이나 인사가 본다. 지향과 문화 적합성을 본다.
- `final`(最終): 임원이 본다. 입사 의사와 장기 지향을 확인한다.

### JP 단골 질문

- 自己紹介
- 転職理由
- 志望動機
- 転職軸
- 強み・弱み
- なぜ 심층: 답마다 「なぜですか」를 반복해 판단의 근거를 확인한다.
- 逆質問

## 페르소나

`mock-interview`는 round에 맞는 평가자를 연기한다.

- US: recruiter는 채용 담당자, hiring-manager는 채용 매니저, technical·system-design·behavioral은
  현직 엔지니어다.
- JP: 라운드 정보가 없으면 現場リーダー / 人事 / 役員 페르소나를 대신 쓴다. 이 순서가 실제 순서라고
  주장하지 않는다.

## HR 기본 질문 6종

자기소개, 이직 사유, 지원 동기, 강점, 약점, 실패 경험. HR은 어느 단계에서든 이 질문을 한다. 답변
형식은 [답변 형식](answer-shapes.md)을 따른다.

## round 고정 확인 항목

면접관도 체크리스트로 합격 여부를 정한다. 아래 항목은 면접관 체크리스트의 `필수: yes` 기본값이다.

|round|고정 확인 항목|
|---|---|
|recruiter·casual|지원 동기 명확성, 이직 사유의 일관성과 재발 위험, 조건 일치(연봉·시기·근무 형태·취업 자격), 커뮤니케이션|
|hiring-manager|why this role/now, 맡을 범위와 경험의 적합성, 프로덕트 이해와 개선 관점, 첫 90일|
|technical·first|JD 기술 항목의 깊이, 판단 이유, 문제 해결·대응, 제출 서류와 말의 일관성|
|system-design|요구사항 명확화, 구조와 데이터 흐름, 트레이드오프 설명|
|behavioral|STAR+R 완결성, 부정적 사건의 해결·대응, 협업|
|second·final|지향과 문화 적합성, 장기 커리어와 회사 방향의 일치, 입사 의사|

`onsite`는 그 loop를 이루는 round의 항목을 합쳐 쓴다.
