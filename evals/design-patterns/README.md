# Design Patterns 평가

[`cases.json`](cases.json)은 패턴 선택, 패턴 불필요 판정, 근거 부족, 분산 시스템 보장과 읽기 전용
검토의 행동 시나리오입니다. 스킬 파일의 특정 문구가 아니라 결과의 결정과 금지 동작을 평가합니다.

## 실행

1. 서로 독립된 임시 workspace에 case의 최소 코드·설계 evidence를 구성합니다.
2. 평가 agent에는 대상 스킬, `request`, `evidence`와 fixture root만 제공합니다. `expected`,
   `forbidden`과 이전 판정은 전달하지 않습니다.
3. `select` case는 Decision, baseline, candidate 수, selected pattern, guarantee와 verification을 확인합니다.
4. `review` case는 파일이 바뀌지 않았는지 확인하고 finding의 실제 trigger와 guarantee를 대조합니다.
5. `routing` case는 스킬이 없는 대조 실행과 비교해 일반 구현을 가로채지 않는지 확인합니다.

각 case는 `supported`, `invalidated`, `inconclusive`, `invalid`, `not-run` 중 하나로 기록합니다.
모델 설정, 실제 입력, 산출물, 파일 hash와 관찰한 제약을 함께 보존합니다. 정적 manifest·frontmatter
검증이나 `allow_implicit_invocation` 로딩은 실제 모델의 라우팅·판단 품질 통과를 뜻하지 않습니다.
