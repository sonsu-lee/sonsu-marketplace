# Engineering

Codex와 Claude Code에서 설계·계획·구현·디버깅·코드 품질·독립 리뷰를 현재 리비전의 검증 근거와 연결해 수행합니다.

## 설치

```bash
codex plugin add engineering@sonsu-marketplace
claude plugin install engineering@sonsu-marketplace
```

omp 기본 구성에서는 개발 실행·task·todo·session·review를 omp 순정 기능이 맡습니다. Engineering을 직접 설치한 omp 호출자는 [omp 모델 프로필](references/omp-model-profiles.md)과 [실행 참고](references/omp-tools.md)를 사용하며, 관리형 gate는 관측한 native session-ID 증거가 있을 때만 명시적으로 선택합니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `brainstorming` | 구현 전에 범위와 설계 경계를 정할 때 | 작업 경로·설계 선택·문서 영향 |
| `plan` | 여러 흐름·파일·검증을 조정할 때 | 의사코드·대응표·작업·검증 계획 |
| `execute-plan` | 승인된 계획을 직접 또는 위임으로 실행할 때 | 현재 근거로 닫은 unit과 전체 작업 |
| `test-driven-development` | 동작 변경이나 자동 검사 추가 전에 검증 방식을 정할 때 | `verification_mode`와 RED·GREEN 결과 |
| `debug` | 실패·오류의 원인을 찾을 때 | 원인·수정·회귀 검증 |
| `review` | 코드·diff·PR을 일반·심층·다중 리뷰할 때 | 근거 있는 finding과 PR 게시 결과 |
| `review-overengineering`, `review-maintainability`, `review-failure-modes`, `review-operability` | 한 관점의 집중 리뷰를 요청할 때 | 해당 관점의 finding |
| `audit-overengineering` | 저장소 범위의 삭제 가능성을 감사할 때 | 순위화한 제거 후보 |
| `domain-shaped-code` | 도메인 계약을 타입·상태에 반영할 때 | 신뢰 경계 검증과 좁은 도메인 표현 |
| `simplify-code` | 현재 코드를 단순화할 때 | 보장을 유지한 단순화 |
| `address-review` | 받은 리뷰 지적을 검증·처리할 때 | 수정·기각·비차단·확인 필요 상태 |
| `worktree`, `finish-branch` | 작업 공간을 준비하거나 브랜치를 마무리할 때 | 격리 공간 또는 통합·보존 결과 |
| `write-skill` | 스킬을 작성·수정하고 검증할 때 | 수정된 계약과 확인 상태 |

PR URL이나 번호를 대상으로 한 리뷰는 `review`가 맡고, 심층·다중 리뷰는 같은 스킬의 요청 옵션입니다. [공통 코드 품질](references/code-quality.md)은 일반 구현과 작업자 brief에도 적용합니다.

## 사용 예시

요청: “`feature/export` 변경을 리뷰해 줘. PR은 아직 없어.”

`review`가 `scripts/review-package range <base> <head>`로 입력을 고정하고 현재 호스트의 `general_review` 새 검토자 5명 결과를 통합합니다. 결과는 위치·근거·조건과 영향·최소 수정이 연결된 finding 목록이며, 확인 범위와 실행하지 못한 검토를 함께 보고합니다.

## 구성

| 영역 | 정본 |
| --- | --- |
| 위험·측정·반환 | [품질 게이트](references/quality-gates.md) |
| 작업자·문맥·통합 | [실행 계약](references/agent-execution.md), [위임](references/delegation.md) |
| 일반·집중 독립 리뷰 | [독립 리뷰 실행](references/independent-review.md), [공통 리뷰 기준](references/review-criteria.md) |
| PR 리뷰 실행·게시 | [PR 실행·게시 계약](references/pr-review-execution.md) |
| 호스트별 모델·effort | [Codex](references/model-profiles.md), [Claude Code](references/claude-model-profiles.md), [omp](references/omp-model-profiles.md) |
| DAG 진입·완료·근거 최신성 | [관리형 게이트 CLI](references/evidence-gates.md) |
| 완료 근거·연속성·전달 권한 | [완료 근거](references/verification.md), [연속성](references/continuity.md), [전달 권한](references/delivery-authority.md) |

`Stop` hook은 관찰만 합니다. 공유 정책 원본은 `shared/agent-policy`, 연속성 원본은 `shared/task-continuity`이며 패키지 사본은 생성기로 만들어 Engineering 단독 설치로 동작합니다. Git 작업·PR 생성과 본문 작성은 Workflow가, 기존 PR의 통합 리뷰 게시·재조회는 Engineering의 PR 리뷰 계약이 맡습니다.

Codex 기본 모델은 marketplace 소스 저장소에서 다음 명령으로 6개 역할(`implementation`, `complex_design`, `senior_review`, `adjudication`, `complex_adjudication`, `red_team`)을 한 번에 전환합니다. 선택값은 `shared/agent-policy/profiles.json`에 저장되며 나머지 역할 설정과 Claude Code·omp 정책은 유지됩니다. `--check`는 읽기 전용이며 전환 옵션과 함께 쓰지 않습니다.

```bash
python3 scripts/render-agent-policy.py --codex-primary-model gpt-6.1-sol
```

정본은 생성물 갱신이 모두 끝난 뒤 원자적으로 교체됩니다. 릴리스할 때 정책 version·확인 날짜와 Engineering·Prompting 패키지 버전을 갱신하고 호환 메타데이터를 재생성합니다. 이 명령은 배포·설치 캐시·현재 root의 모델 설정을 바꾸지 않습니다.

## 검증

```bash
python3 scripts/render-agent-policy.py --check
python3 scripts/render-claude-compat.py --check
python3 scripts/render-omp-compat.py --check
python3 scripts/render-continuity.py --check
python3 -B -m unittest discover -s plugins/engineering/tests -p 'test_*.py'
bash plugins/engineering/tests/review-package.test.sh
python3 -B -m unittest discover -s evals/task-continuity -p 'test_*.py'
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py'
```

실제 모델 동작과 native 스킬 선택은 [marketplace-v2 평가](../../evals/marketplace-v2/README.md)에 기록합니다. 라이선스와 포함 출처는 [LICENSE](LICENSE), [UPSTREAM.md](UPSTREAM.md)를 확인하세요.
