# 스킬 라우팅 평가

`cases.json`은 Superpowers와 Workflow를 함께 또는 각각 설치했을 때의 기대 라우팅을 정의합니다.
직접 산출물 요청, 비슷하지만 다른 요청, 순차 조합과 단독 설치 사례를 포함합니다.

이 평가는 실제 skill selection 결과를 대상으로 합니다. JSON 파싱이나 description 문자열 비교는
평가 실행을 대신하지 않습니다. 모델 기반 실행은 격리된 읽기 전용 fixture에서 수행하고 원격
push, ticket 게시와 PR 생성은 허용하지 않습니다. 결과는 `pass`, `fail`, `not_run`,
`inconclusive`로 구분하며, 선택 attribution을 확인할 수 없으면 `pass`로 판정하지 않습니다.
