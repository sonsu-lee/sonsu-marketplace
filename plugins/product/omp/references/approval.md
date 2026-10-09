# 승인 기준

Product 스킬이 승인 상태를 기록하거나 판정할 때 읽는다.

## 승인 요건

- 문서의 존재, 추천, 회의 참석과 배포 상태를 승인으로 간주하지 않는다.
- 승인 상태에는 승인한 주체, 권한 근거, 승인한 범위, 현재 리비전, 확인 시점과 승인 근거가
  필요하다.
- 현재 리비전이 바뀌면 이전 승인을 새 리비전의 승인으로 재사용하지 않는다.
- 숫자, 날짜, 담당자와 결정 이력을 추정하지 않는다.

## 상태 어휘

축마다 어휘가 다르다. 한 축의 값을 다른 축에 쓰지 않는다.

| 축 | 값 | 쓰는 곳 |
| --- | --- | --- |
| 제품 합의 | `discovery-needed` / `conditional` / `approved` | 탐색 결과, PRD 준비 상태 표의 제품 합의 행 |
| PRD 변환 가능성 | `ready` / `partial` / `blocked` | `to-prd`와 `product-discovery`의 변환 판정 |
| frontmatter `workflow_status` | `conditional` / `approved` | PRD 문서 metadata |
