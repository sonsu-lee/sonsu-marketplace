# Execution workflow

1. 산출물 범위와 모드를 고정한다.
2. 대상 저장소의 instruction, 제품 token/component, route, state/data boundary, test/browser harness를 읽는다.
3. 사용자·맥락·primary question·오판 비용을 포함한 Design Decision Contract를 작성하고 검증한다.
4. 과업마다 must-know 정보, 표현 이유, 상태, 환경, metric target을 연결한다.
5. 재설계면 현재 동작 inventory와 change contract를 먼저 완성한다.
6. 대상 제품의 디자인 시스템을 semantic role에 매핑해 구현하거나 Figma에 제작한다.
7. 현재 scope의 DQ gate를 독립 평가하고, implementation/live는 실제 browser receipt를 수집한다.
8. live에서만 위험도에 맞는 사용자·production·domain safety 근거로 DQ8을 평가한다.

```bash
python3 <plugin-root>/scripts/validate_contracts.py screen-contract <contract.json>
python3 <plugin-root>/scripts/validate_contracts.py quality-report <report.json> <contract.json>
```

validator 실패는 가장 가까운 책임 단계로 돌린다. 계약·추적 오류는 3–5단계, 시각·정보 문제는
4–6단계, runtime 누락은 7단계, outcome 근거 부족은 8단계의 책임이다. 같은 논리 작업의 자동
수정·재검증은 기존 작업 기록을 포함해 누적 최대 5회이며, 새 근거나 다른 전략 없이 반복하지 않는다.

감사 모드는 file/DOM/rendered visual 읽기와 비파괴 navigation만 허용한다. submit, create,
update, delete, persisted toggle, test-data 생성이나 파일 편집을 하지 않는다.
