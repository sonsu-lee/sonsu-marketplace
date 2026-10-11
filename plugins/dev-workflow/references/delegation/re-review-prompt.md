# 집중 재리뷰 프롬프트

조정자는 [공통 리뷰 기준](../review-criteria.md)의 내용과 현재 실행 계약을 함께 전달한다. 링크만으로 전달을 대신하지 않는다. 매 회차 새 문맥의 검토자를 사용한다.

```text
원래 지적과 수정이 만든 회귀를 읽기 전용으로 검토한다. 수정·추가 하위 에이전트 위임은
조정자가 담당한다.

작업 brief: [작업 요약 파일]
원래 finding: [기존 지적]
사실 중심 검증 사본: [보고서 파일]
실행 범위·실행 환경/임시 공간·예산: [실행 계약]
수정 base: [수정 시작 커밋 SHA]
Head: [종료 커밋 SHA]
고정 수정 diff: [변경 패키지 파일]

작업 요약·지적·수정 차이·검증 사본을 읽는다. 차이가 없으면 정확한 수정 base..Head의
git diff --stat와 git diff --binary --no-ext-diff -U10으로 확인한다. 남은 구체적인 의문에
필요한 근거나 집중 검사만 추가한다. 사본 확인을 위해 기존 검증을 반복하지 않는다.

추가 자료는 수정 리비전과의 관계·적용 이유를 확인한다. 공통 기준으로 중복·추측·불필요한
절차 요구를 걸러내며 조건·예외·불확실성을 보존한다. 관찰 도구 등록은 조정자의 책임이다.

각 지적을 ADDRESSED | NOT ADDRESSED로 판정한다. 원래 지적이 실제 기본 동작·확인된 계약과
어긋나면 INVALID로 제안하고 근거를 제시한다. 수정 시도만으로 해결 처리하지 않는다.
새 지적은 수정이 만든 Critical/Important 회귀만 포함한다. 계약·의존성 경계가 바뀌거나
영향이 불명확하면 전체 리뷰 재개방을 요청한다.

출력:
Gate status: passed | failed | inconclusive | blocked
수정 회차: All findings addressed, no new Critical/Important breakage |
           Findings remain open | Inconclusive | Blocked
Finding 판정: [각 항목의 상태와 file:line 근거]

실제 회귀·필수 근거 공백에는 발생 조건·영향·반환 대상을 적는다. INVALID는 조정자가 근거를
확인해 닫은 뒤 해결 목록에 반영한다. 유효한 필수 지적은 failed, 필수 근거 부족은 inconclusive,
검증 환경 부재는 blocked다.
```
