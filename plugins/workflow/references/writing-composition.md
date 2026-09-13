# 작성 지침 함께 적용하기

Workflow는 티켓·PR의 적용 양식·필수 항목, 실제 사실·diff·검증 근거, 연결 문법과 게시 조건을
확인한다. 이 플러그인의 작성 지침과 양식으로 단독 실행할 수 있다.

현재 inventory에 있는 스킬만 다음 범위에서 함께 적용한다.

- `writing:writing`: 정보 선별·문서 배치와 문장·문단 구성. 실제 양식과 확인 상태, 사실·근거,
  출력 언어, 편집 범위와 보존할 제목·marker·연결 문법을 전달한다.
- `fluent-languages:fluent-korean`, `fluent-languages:fluent-japanese`,
  `fluent-languages:fluent-english`: 요청된 출력 언어에 맞는 표현. Writing이 없을 때에도
  해당 언어 스킬이 있으면 사용할 수 있다.

작성 담당자는 적용한 지침을 구분하고 각 지침을 한 번만 반영한다. Writing에서 이미 Fluent를
적용했다면 다시 불러오지 않는다. 별도 agent나 완성본을 반복해서 고치는 pipeline이 아니라,
같은 초안에 필요한 구성·표현 규칙을 함께 적용한다. 스킬이 없어도 자체 지침으로 계속하며
자동 설치·연결이나 설치를 위한 질문을 하지 않는다.

사용자·프로젝트의 형식과 허용된 편집 범위, 사실·조건·의무 수준·코드·식별자·URL을 우선한다.
작성 뒤 고정 양식·필수 필드·HTML marker와 `Fixes`, `Closes`, `Part of`, `Ignore`, ticket ID·Jira key를
다시 대조한다. 임시 초안이나 표현 개선은 양식 확인·게시 조건·외부 작업 권한을 대신하지 않는다.
