# Engineering

Codex에서 설계·구현·디버깅·코드 품질·독립 리뷰를 수행하는 플러그인입니다. Quality Engineering의
8개 품질 스킬을 통합하고 PR 리뷰의 워크트리 실행·결과 게시를 제공하는 2.2.0이며, 일반 코드 리뷰도 `engineering:review-quality`로 진입합니다.
기존 `quality-engineering:` 별칭과 별도 패키지는 제공하지 않습니다.

## 실행 경계

- 기계적 변경은 결정론적 변환·소비 검사로 처리합니다.
- 동작 변경은 필요한 검사와 Luna xhigh 5개 독립 리뷰를 적용합니다.
- 고위험 설계·상태·권한·복구 경계는 별도 Astra high red-team을 추가합니다.
- 일반 리뷰 요청도 5개 새 문맥이 기본이며 전체 개발 계획·소스 수정을 요구하지 않습니다.
  관점 하나의 집중 리뷰와 국소 수정 재검토는 Luna xhigh 1개가 기본입니다.

root가 위험과 작업 경계를 판단하고 필요한 수만큼 작업자를 할당합니다. 직접 실행과 위임은
같은 수명주기를 사용합니다. 병렬 작성은 별도 worktree, 통합은 순차 실행입니다. worker는
추가 할당을 root에 요청합니다. Codex의 기본 실행·세션·spawn/wait/resume를 재사용합니다.

## 진입점

| 작업 | 스킬 |
| --- | --- |
| 범위와 설계 | `brainstorming` |
| 의존성과 검증 계획 | `writing-plans` |
| 직접/위임 실행 | `executing-plans`, `subagent-driven-development` |
| 원인 진단 | `systematic-debugging` |
| 일반 코드 리뷰 | `review-quality` |
| PR 심층·다중 리뷰 | `review-pr` (Luna xhigh 5명 + Astra xhigh 1명) |
| 독립 리뷰 실행 | `requesting-code-review` |
| 도메인을 타입·상태에 반영 | `domain-shaped-code` |
| 현재 코드 단순화 | `simplify-code` |
| 복잡성·유지보수·실패·운영성 리뷰 | `review-overengineering`, `review-maintainability`, `review-failure-modes`, `review-operability` |
| 넓은 삭제 가능성 감사 | `audit-overengineering` |
| 피드백 검증·완료 | `receiving-code-review`, `verification-before-completion` |

스킬의 [공통 코드 품질](references/code-quality.md)은 일반 구현과 작업자 brief에도 적용합니다.
확정한 도메인 타입으로 불가능한 경로를 제거하고 실제 신뢰 경계에서 검증합니다. 이미 보장한
내부 경로의 중복 가드와 현재 요구 없는 fallback/추상화를 추가하지 않습니다.

PR URL이나 번호를 대상으로 한 일반 리뷰 요청은 `review-quality`가 담당합니다. 명시적인 PR 심층·다중 리뷰는
`review-pr`가 담당합니다. 두 경로 모두 같은 전체 diff를 별도 세션·워크트리에서 병렬 검토하고
중복 제거한 결과를 PR의 `COMMENT` 리뷰로 게시·재조회합니다. 일반 리뷰는 Luna xhigh 5명,
심층 리뷰는 Luna xhigh 5명 + Astra xhigh 1명이 기본입니다. 직접 스킬 지정과 모델·인원 지정,
로컬 전용·게시 금지 요청은 우선합니다. 개발 완료 게이트·소스 수정·merge는 포함하지 않습니다.

`Selected model is at capacity`는 원인 미상의 Codex 일시 실행 오류로 기록하고 같은 설정으로
재시도합니다. 이 문자열만으로 로컬 슬롯·계정 한도·모델 미지원이나 실제 서버 전체 장애를
확정하지 않습니다. [PR 실행·게시 계약](references/pr-review-execution.md)에 재시도 상한,
SHA 변경·불명확한 게시 응답·기존 댓글 중복 처리와 실행 한계를 정리했습니다.

## 실행 정책과 프로그램 제어

[품질 게이트](skills/using-engineering-skills/references/quality-gates.md)는 위험·측정·반환을,
[실행 계약](skills/using-engineering-skills/references/agent-execution.md)은 작업자·문맥·통합을,
[모델 프로필](references/model-profiles.md)은 정확한 model+effort를 정의합니다.
모델 표는 운영 기본값이며 사용자 지정을 우선합니다. 프로필 출처·날짜·평가 상태를 보존합니다.

[관리형 게이트 CLI](skills/using-engineering-skills/references/evidence-gates.md)는 등록한 DAG의
진입·완료, 검사·리뷰 근거 최신성과 의존성을 검사합니다. `Stop` hook은 관찰만 합니다.
임의 도구 호출 전체를 차단하거나 리뷰 의미의 정확성을 증명하지 않습니다.
설계/계획은 고정 문서 패키지, 구현/통합은 전체 workspace snapshot을 사용합니다.

공유 정책 원본은 `shared/agent-policy`, 연속성 원본은 `shared/task-continuity`입니다.
각 패키지에 필요한 사본을 생성하므로 Engineering 단독 설치로 동작합니다. 실행 시 다른
플러그인 파일 경로나 설치를 전제하지 않습니다. 변경과 [전달 권한](references/delivery-authority.md)은
별개이며 Git 작업·PR 생성과 제목/본문 작성은 요청한 범위에서 Workflow와 연결합니다.
기존 PR의 통합 리뷰 게시·재조회는 Engineering의 PR 리뷰 계약이 소유합니다.

## 검증

```bash
python3 scripts/render-agent-policy.py --check
python3 scripts/render-continuity.py --check
python3 -m unittest discover -s plugins/engineering/tests -p 'test_*.py'
python3 -m unittest discover -s evals/task-continuity -p 'test_*.py'
python3 -m unittest discover -s evals/plugin-compat -p 'test_*.py'
```

실제 모델 동작과 native 스킬 선택은 [marketplace-v2 평가](../../evals/marketplace-v2/README.md)에
별도로 기록합니다. 기존 v1 evidence와 ADR은 이력으로 보존하며 새 정책의 통과로 자동 이관하지 않습니다.
설치 캐시·사용자 설정을 소스 변경만으로 갱신하지 않습니다.

라이선스와 포함 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md)를 확인하세요.
