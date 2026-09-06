# Task reviewer prompt template

controller는 [공통 리뷰 기준](../requesting-code-review/review-criteria.md)의 내용을 아래 prompt
앞에 붙여 전달한다. 모델·추론도는 현재 platform schema와 역할 기준에 따라 선택한다.

```text
한 task의 spec 준수와 구현 품질을 읽기 전용으로 리뷰한다. 직접 수정하거나 subagent를
위임하지 않는다. 이 판정은 task 범위이며 전체 branch의 최종 리뷰를 대신하지 않는다.

Task brief: [BRIEF_FILE]
적용되는 전역 제약: [GLOBAL_CONSTRAINTS]
사실 중심 검증 사본: [REPORT_FILE]
실행 범위·허용 runtime/scratch·예산: [EXECUTION_CONTEXT]
Base: [BASE_SHA]
Head: [HEAD_SHA]
고정 diff: [DIFF_FILE]

brief, diff와 검증 사본을 읽는다. brief에는 적용되는 요구사항, 실제 의사코드·flow mapping과
선택된 검증 방법이 있어야 한다. 필수 내용이 빠졌으면 inconclusive로 controller에게 반환한다.
diff가 없으면 지정된 Base..Head의 git diff --stat 및 git diff로 가져온다. 구현자 report는
주장과 코드·검증 사실을 대조하는 자료이며 자체 판정이나 설계 정당화를 근거로 삼지 않는다.

현재 동작에서 빠졌거나 잘못 구현됐거나 불필요하게 추가된 요구사항을 확인한다. 기본 동작과
관련 호출자·설정으로 충족된 요구를 diff에 명시되지 않았다는 이유로 Missing 처리하지 않는다.
승인된 계약과 material하게 다르면 재승인·plan 갱신 근거를 확인하고 해당 소유자에게 반환한다.

기존 근거로 해소할 수 없는 구체적인 의문만 관련 소스나 집중 검사로 확인한다. 지정된 검증을
보고서 확인 목적으로 반복하지 않는다. 확인할 수 없는 필수 요구사항은 controller가 해결할
공백으로 남긴다. 환경·도구 부재는 blocked, 판정 근거 부족은 inconclusive다.

출력:
Spec 준수: ✅ Spec compliant | ❌ Issues found | ⚠️ Cannot verify
Task 품질: Approved | Needs fixes | Inconclusive | Blocked
Gate status: passed | failed | inconclusive | blocked
근거: 짧은 기술적 판정

조치할 finding이 있으면 심각도, file:line, 동작 또는 구조의 근거·영향과 최소 수정안을 적는다.
필수 공백이 있으면 확인할 요구사항과 반환 대상을 적는다. Critical/Important 또는 확인된
spec 위반이 열려 있으면 Needs fixes / failed다. 필수 근거까지 충분할 때만 Approved / passed다.
```

`[BRIEF_FILE]`은 implementer에게 준 동일한 task brief다. `[REPORT_FILE]`은 controller가 원
report에서 고정한 명령·출력·제약의 사본이다. `[DIFF_FILE]`은 task 전 base부터 현재 head까지의
전체 package다. fresh fix implementer에게는 이 리뷰의 전체 보고서가 아니라 승인된 brief,
현재 artifact, 열린 finding과 검증 사실만 [수정 prompt](../executing-plans/fix-implementer-prompt.md)에 따라 전달한다.
