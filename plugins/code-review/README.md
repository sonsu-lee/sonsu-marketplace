# Code Review

Codex와 OMP 위에서 전문 review lens와 직접 호출형 PR review만 제공하는 `1.0.0` capability pack이다.
일반 구현, 디버깅, 테스트, 일반 코드 리뷰와 완료 검증은 host 기본 동작이 담당한다.

## Skills

| 요청 | Skill | Mutation |
| --- | --- | --- |
| 명시 PR의 3-reviewer 통합 review | `review-pr` | 통합 GitHub `COMMENT` 하나 |
| 도달 가능한 실패 경로 | `review-failure-modes` | 없음 |
| reader load와 변경 비용 | `review-maintainability` | 없음 |
| error ownership와 진단 가능성 | `review-operability` | 없음 |
| 선택 변경의 불필요한 구조 | `review-overengineering` | 없음 |
| repository/path 삭제 가능성 | `audit-overengineering` | 없음 |

focused lens는 현재 host의 읽기·코드 탐색으로 직접 완료한다. 특정 model, 필수 subagent,
continuity state, managed quality gate를 요구하지 않는다. 결과는 `path:line`, 실제 trigger, 영향,
근거와 최소 수정 방향을 포함한다.

`review-pr`은 자동 routing되지 않는다. Codex에서는 `$review-pr`, OMP에서는
`/skill:review-pr`로 직접 호출해야 한다. 정확히 세 fresh reviewer가 locked PR diff를 별도 clean
detached checkout에서 한 번씩 읽고 coordinator가 원인 기준으로 검증·중복 제거한다. 현재 host의
model/reasoning을 상속하며 model 이름이나 인원수를 대체하지 않는다. 세 명 모두 성공하고 head
SHA가 그대로일 때만 marker가 있는 `COMMENT` review 하나를 게시한다. 응답 불명 뒤 완전한
readback으로 동일성을 증명하지 못하면 재게시하지 않고 `fail_ambiguous`로 끝낸다.

## Verification

```bash
python3 -B -m unittest discover -s plugins/code-review/tests -p 'test_*.py' -v
```

포함 자료와 라이선스는 [UPSTREAM.md](UPSTREAM.md),
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [NOTICE](NOTICE)를 확인한다.
