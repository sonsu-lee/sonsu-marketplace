# Focused re-review prompt template

controller는 [공통 리뷰 기준](../requesting-code-review/review-criteria.md)의 내용을 아래 prompt
앞에 붙여 전달한다. 모델·추론도는 현재 platform schema와 역할 기준에 따라 선택한다.

```text
원래 finding과 수정이 만든 회귀를 읽기 전용으로 검토한다. 직접 수정하거나 subagent를
위임하지 않는다.

Task brief: [BRIEF_FILE]
원래 finding: [FINDINGS]
사실 중심 검증 사본: [REPORT_FILE]
실행 범위·허용 runtime/scratch·예산: [EXECUTION_CONTEXT]
Fix base: [FIX_BASE_SHA]
Head: [HEAD_SHA]
고정 수정 diff: [DIFF_FILE]

brief, finding, 수정 diff와 검증 사본을 읽는다. diff가 없으면 지정된 Fix base..Head의
git diff --stat 및 git diff로 가져온다. 구체적인 의문이 남을 때만 관련 근거나 집중 검사를
확인한다. 기존 검증을 보고서 확인 목적으로 반복하지 않는다.

각 finding을 ADDRESSED | NOT ADDRESSED로 판정한다. 원래 지적 자체가 기본 동작이나
확인된 계약과 어긋나면 INVALID로 판정하고 근거를 제시한다. 수정 시도만으로 해결 처리하지
않는다. 범위는 원래 finding과 수정 회귀다. 새 아이디어를 찾는 전체 리뷰를 반복하지 않는다.
계약·dependency 경계가 바뀌거나 영향이 불명확하면 전체 리뷰 재개방을 요청한다.

출력:
Gate status: passed | failed | inconclusive | blocked
수정 회차: All findings addressed, no new Critical/Important breakage |
           Findings remain open | Inconclusive | Blocked
Finding 판정: 각 항목의 상태와 file:line 근거

수정이 만든 실제 회귀 또는 필수 근거 공백이 있으면 발생 조건·영향과 반환 대상을 적는다.
INVALID는 controller가 근거를 확인해 닫은 뒤 해결 목록에 반영한다. 유효한 필수 finding이
남으면 failed, 필수 근거 부족은 inconclusive, 검증 환경 부재는 blocked다.
```
