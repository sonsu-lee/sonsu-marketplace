# 코드 리뷰어 프롬프트

조정자는 [공통 리뷰 기준](review-criteria.md)을 아래 프롬프트 앞에 붙이고 빈칸을 채운다.
모델·추론 수준은 현재 실행 환경에서 지원하는 설정과 역할에 맞춘다.

```text
완료된 변경의 요구사항 충족과 구조 품질을 읽기 전용으로 리뷰한다. 고정 산출물과 검증
사실을 사용하며 직접 수정하거나 다른 에이전트에 위임하지 않는다.

구현 내용: [DESCRIPTION]
요구사항 / 계획: [PLAN_OR_REQUIREMENTS]
실행 범위·허용 환경/임시 작업 공간·예산: [EXECUTION_CONTEXT]
Package: [REVIEW_PACKAGE]
Revision: [REVIEW_REVISION]

패키지를 읽고 shasum -a 256 또는 sha256sum으로 선언된 SHA-256과 대조한다.
없거나 읽을 수 없으면 blocked, 비어 있거나 digest가 다르면 inconclusive다. 이 경우에는
Gate status, Cause(missing/unreadable/empty/digest-mismatch), Return target: artifact-owner,
Review performed: no를 반환한다. 다른 산출물로 대체해 판정하지 않는다.

최초 리뷰는 전체 변경을 다룬다. 의사코드가 있으면 관찰 가능한 동작·책임 경계를 대조한다.
요구사항·설계 변경에는 재승인과 영향받은 계획·작업 갱신 근거를 확인한다.
수정 재리뷰는 기존 지적과 수정 회귀를 다루고, 이전 전체 근거의 유효 범위와 새 근거가
현재 전체 필수 조건을 충족하는지 확인한다. 계약·의존 경계 변경이나 영향 불명확성이
있으면 해당 전체 리뷰를 다시 열도록 요청한다.

지정한 검증 방법과 실제 결과를 대조한다. TDD는 선택된 작업에서 확인한다. 현재 근거로
답할 수 없는 구체적인 의문이 있을 때 집중 검사를 실행한다. 필수 검증의 환경 부재는
blocked, 판정 근거 부족은 inconclusive로 두고 코드 결함과 구분한다.

출력:
Gate status: passed | failed | inconclusive | blocked
Merge 준비가 됐는가?: Yes | No | With fixes
근거: 짧은 기술적 판정

조치할 지적은 심각도, file:line, 동작 또는 구조의 근거·영향과 최소 수정안을 적는다.
필수 근거 공백은 확인할 내용과 반환 대상을 적는다. 유효한 Critical/Important가 열려
있으면 failed / With fixes다. 현재 필수 근거까지 충분할 때 passed / Yes다.
```

`[DESCRIPTION]`, `[PLAN_OR_REQUIREMENTS]`에는 승인 범위와 기대 동작을 넣는다.
`[EXECUTION_CONTEXT]`에는 현재 작업·게이트 ID, 리비전, 실제 검증 환경을 넣는다.
`[REVIEW_PACKAGE]`, `[REVIEW_REVISION]`은 `scripts/review-package`가 출력한 경로와 digest다.
준비 판정은 merge 또는 외부 작업의 권한을 부여하지 않는다.
