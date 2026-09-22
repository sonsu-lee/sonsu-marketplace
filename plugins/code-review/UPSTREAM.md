# Code Review provenance

이 package는 기존 Engineering package의 focused review 자료 중 실제 배포하는 부분만 옮겼다.
현재 파일은 upstream 원문과 byte-identical하지 않으며 아래 고정 commit과 source/final mapping이
비교 기준이다. Apache-2.0 자료는 [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0)과 [NOTICE](NOTICE),
MIT 자료는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)의 고지를 따른다.

## Included or adapted material

| Source | Commit | License | Final path |
| --- | --- | --- | --- |
| [`cursor/plugins` thermos](https://github.com/cursor/plugins) | `efa2a531985e0a8084d36ff3cf87233be8a9f34b` | MIT, Copyright 2026 Cursor | `skills/review-maintainability/SKILL.md` |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | MIT, Copyright 2026 DietrichGebert | `skills/review-overengineering/SKILL.md`, `skills/audit-overengineering/SKILL.md` |
| [`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) | `db52e28f4d9ded852ab3942cea316258ae4ef346` | Apache-2.0, NOTICE Copyright 2026 OpenAI | `skills/review-failure-modes/SKILL.md` |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | `d2c37ef6225dd8726cdd369a8030307f48592d26` | MIT, Copyright 2025 Addy Osmani | `skills/review-operability/SKILL.md` |

OpenAI source는 `plugins/codex/prompts/adversarial-review.md`이며 command runtime은 포함하지 않았다.
원본 SHA-256은 `f3b28a6c4c7501fd03ebab228050ac53c552a8f43c8aa517e924cb348aaefe0f`이다.
`LICENSE-APACHE-2.0`과 `NOTICE`의 원본 SHA-256은 각각
`e591c02a0b2ea7717d99e15bd51ea05d879bbf5a4452d66d15b51a7107d3821a`,
`6728b3dff175efe673c1d6a402f5d9f548127a20960a6efdf9047dae1e36ecfb`이다.

`references/review-criteria.md`, `references/code-quality.md`,
`references/javascript-typescript-review.md`, `references/pr-review-execution.md`, `review-pr` workflow와
protocol helper는 이 저장소에서 작성했다. focused lens는 고정 threshold, vendor 강제,
미확정 미래 요구와 unreachable failure를 finding으로 만들지 않도록 수정했다.

## Consulted only

- `kdy1/kdy1-scripts@92a8fbe9a57bce5064ed7dba3a8f87f331930dc6`의
  `review-full/SKILL.md`: 고정 revision, 독립 review와 원인별 중복 제거 구조만 참고했다. 확인한
  snapshot에는 root license가 없어 문구, 코드, helper와 template을 복사하지 않았다.
- `ggombee/code-forge@1779c8ac9638c755d341b16e708f7e44aaf15b75`: optional capability와
  lazy-loading 경계만 참고했다. setup, routing, state, hook, logger와 generator를 포함하지 않았다.

새 source를 incorporate할 때 exact commit, source path, final path와 license/notice를 먼저 기록한다.
