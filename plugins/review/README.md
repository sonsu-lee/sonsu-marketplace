# Review

코드·diff·커밋·PR이 시스템의 코드 건강도를 높이는지 판정하고, 라벨로 필수·선택 지적을 구분해 보고합니다.

## 설치

```bash
codex plugin add review@sonsu-marketplace
claude plugin install review@sonsu-marketplace
omp plugin install review@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| `review-code` | 현재 코드·diff·staged 변경·commit·branch·PR을 리뷰할 때 | 판정(`Approve`·`Approve with comments`·`Request changes`)과 라벨 붙은 지적, PR이면 게시 결과 |
| `review-overengineering` | 과도한 설계·불필요한 추상화만 볼 때 | 해당 관점의 지적 |
| `review-maintainability` | 유지보수성만 볼 때 | 해당 관점의 지적 |
| `review-failure-modes` | 실패 경로만 볼 때 | 해당 관점의 지적 |
| `review-operability` | 운용 가능성만 볼 때 | 해당 관점의 지적 |
| `audit-overengineering` | 저장소 범위의 삭제 가능성을 감사할 때 | 순위화한 제거 후보 |
| `address-review` | 받은 리뷰 지적을 검증하고 대응할 때 | 수정·근거로 기각·추가 확인 필요·비차단 보고와 답글 초안 |

PR에 달린 리뷰 코멘트의 조회·수정 push·답글·대화 해결은 `git` 플러그인의 `repair-pr`이 담당합니다.

## 사용 예시

요청: “현재 diff를 리뷰해 줘.”

`review-code`가 변경 전체를 읽어 필요성과 핵심 설계를 먼저 본 뒤 나머지를 빠짐없이 검토합니다. 결과는 맨 위의 판정과, 필수 → `Optional:` → `Nit:` → `FYI:` 순서의 `path:line — 문제. 이유.` 형식 지적, 근거 있는 잘한 점입니다.

## 구성

- 리뷰어 기준: [공통 리뷰 기준](references/review-criteria.md), [코드 품질](references/code-quality.md), [JS·TS 리뷰](references/javascript-typescript-review.md). 작성자 대응은 [리뷰 지적 대응](references/responding-to-review.md)을 따릅니다.
- 실행: PR 외 리뷰와 집중 리뷰는 [리뷰 실행](references/review-execution.md), PR은 [PR 리뷰 실행과 게시](references/pr-review-execution.md)를 따릅니다. 호스트별 모델은 [Codex](references/model-profiles.md), [Claude Code](references/claude-model-profiles.md), [omp](references/omp-model-profiles.md) 프로필에 있습니다.
- omp에서 `/review`나 `/annotate code-review`를 써도, 이 플러그인을 설치하면 같은 라벨·판정·어조가 순정 reviewer에 추가로 적용됩니다. 규칙 원본은 [`omp-rules/sonsu-review-standard.md`](omp-rules/sonsu-review-standard.md)이며 omp 패키지의 `rules/`로 들어갑니다.
- `review-code`는 여기에 대상 고정, 커밋 검토, PR 게시, 여러 검토자 결과 통합을 더합니다.
- 공유 기준과 `scripts/review-package`는 `shared/`의 정본에서 생성기로 복사합니다. 생성물은 직접 고치지 않습니다.
- 라이선스와 포함 출처는 [LICENSE](LICENSE), [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0), [NOTICE](NOTICE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [UPSTREAM.md](UPSTREAM.md)에 있습니다.

## 검증

```bash
python3 scripts/render-shared-files.py --check
python3 -B -m unittest discover -s plugins/review/tests -p 'test_*.py' -v
bash plugins/review/tests/review-package.test.sh
```
