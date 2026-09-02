# Quality Engineering upstream provenance

Quality Engineering은 여러 upstream의 제한된 파일을 기반으로 만든 로컬 Codex 플러그인입니다.
원본은 commit `538c9e9b8130a0f6cf56780a7700a983f77524de`에서 `upstream/` 아래에
byte-for-byte로 보존했고, 다음 customization commit에서 최종 `skills/` 경로로 이동해 수정합니다.
따라서 현재 파일은 원본과 byte-identical하지 않으며, baseline commit이 원문 비교 기준입니다.

## 기준 source

| Source | Commit | License | 확인 결과 |
| --- | --- | --- | --- |
| [`cursor/plugins`](https://github.com/cursor/plugins) `pstack` | [`efa2a531985e0a8084d36ff3cf87233be8a9f34b`](https://github.com/cursor/plugins/commit/efa2a531985e0a8084d36ff3cf87233be8a9f34b) | MIT, Copyright 2026 Lauren Tan | 2026-09-02 당시 repository `HEAD`와 동일 |
| [`cursor/plugins`](https://github.com/cursor/plugins) `thermos` | [`efa2a531985e0a8084d36ff3cf87233be8a9f34b`](https://github.com/cursor/plugins/commit/efa2a531985e0a8084d36ff3cf87233be8a9f34b) | MIT, Copyright 2026 Cursor | skills.sh canonical source와 repository 경로를 함께 확인 |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | [`2ed6c52c9d7e5e56942508591085fd45dea277d3`](https://github.com/DietrichGebert/ponytail/commit/2ed6c52c9d7e5e56942508591085fd45dea277d3) | MIT, Copyright 2026 DietrichGebert | 지정 commit 고정 |
| [`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) | [`db52e28f4d9ded852ab3942cea316258ae4ef346`](https://github.com/openai/codex-plugin-cc/commit/db52e28f4d9ded852ab3942cea316258ae4ef346) | Apache-2.0, NOTICE Copyright 2026 OpenAI | 2026-09-02 당시 repository `HEAD`와 동일 |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | [`d2c37ef6225dd8726cdd369a8030307f48592d26`](https://github.com/addyosmani/agent-skills/commit/d2c37ef6225dd8726cdd369a8030307f48592d26) | MIT, Copyright 2025 Addy Osmani | 지정 commit 고정 |
| [`mcollina/skills`](https://github.com/mcollina/skills) | [`856efd268ae85482d882f3d0bed869fd020b5c06`](https://github.com/mcollina/skills/commit/856efd268ae85482d882f3d0bed869fd020b5c06) | MIT, Copyright 2026 Matteo Collina | 지정 commit 고정 |

OpenAI 저장소의 adversarial review는 `SKILL.md`가 아니라
`plugins/codex/prompts/adversarial-review.md`가 실제 review prompt이며,
`plugins/codex/commands/adversarial-review.md`가 이를 호출하는 command입니다. failure-mode lens에는
prompt를 사용했고 command runtime은 포함하지 않았습니다.

## Baseline과 최종 mapping

아래 SHA-256은 upstream 원본과 baseline commit의 `upstream/` 경로에서 동일했고, file mode는 모두
`100644`였습니다. 최종 파일에는 로컬 정책을 적용했습니다.

| Source relative path | Baseline path | Final path | Original SHA-256 |
| --- | --- | --- | --- |
| `pstack/skills/principle-model-the-domain/SKILL.md` | `upstream/cursor-plugins/pstack/skills/principle-model-the-domain/SKILL.md` | `skills/domain-shaped-code/SKILL.md` | `6b359783c5c9be87860d0999321e864940ff17729b9f9a27f38abae449640022` |
| `pstack/skills/typescript-best-practices/SKILL.md` | `upstream/cursor-plugins/pstack/skills/typescript-best-practices/SKILL.md` | `skills/domain-shaped-code/references/typescript.md` | `b854da40f946f1cd4681785d3e802a2a592322d351f770f5057b56430edb35d0` |
| `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `upstream/cursor-plugins/thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `skills/review-maintainability/SKILL.md` | `7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f` |
| `skills/ponytail/SKILL.md` | `upstream/ponytail/skills/ponytail/SKILL.md` | `skills/simplify-code/SKILL.md` | `1316a2f3f95741d2300b116fe0c2d81ce4a9568656ed0a62643f54aaf09957f2` |
| `skills/ponytail-review/SKILL.md` | `upstream/ponytail/skills/ponytail-review/SKILL.md` | `skills/review-overengineering/SKILL.md` | `40df33b58fc6ef889b93585733feb9566b76e9586efa7f376785c1e995197ac0` |
| `skills/ponytail-audit/SKILL.md` | `upstream/ponytail/skills/ponytail-audit/SKILL.md` | `skills/audit-overengineering/SKILL.md` | `5560b8e383dbe2ddfddc873a1e2bf2e586e23e0cd7d995537482b2315331f6d1` |
| `plugins/codex/prompts/adversarial-review.md` | `upstream/codex-plugin-cc/plugins/codex/prompts/adversarial-review.md` | `skills/review-failure-modes/SKILL.md` | `f3b28a6c4c7501fd03ebab228050ac53c552a8f43c8aa517e924cb348aaefe0f` |
| `skills/observability-and-instrumentation/SKILL.md` | `upstream/agent-skills/skills/observability-and-instrumentation/SKILL.md` | `skills/review-operability/SKILL.md` | `bcec2ada212de6d07daa16886859cc0f2d954c845fc65fdbb7b23106df6aa8c0` |
| `skills/node/rules/error-handling.md` | `upstream/mcollina-skills/skills/node/rules/error-handling.md` | `skills/domain-shaped-code/references/error-handling.md` | `11a3509b3d4c0603a7432cf2005946d6c61f952b8c6ef7c6d5c22e93a4c4586c` |
| `skills/node/rules/logging.md` | `upstream/mcollina-skills/skills/node/rules/logging.md` | `skills/domain-shaped-code/references/logging.md` | `3ccf1285a5d6e1dbf6d9cf782ec4983b62bd2b378adbfb34407bb72831f89765` |

`LICENSE`와 `NOTICE`는 `openai/codex-plugin-cc/plugins/codex/`의 파일을 byte-for-byte로
가져왔습니다. SHA-256은 각각
`e591c02a0b2ea7717d99e15bd51ea05d879bbf5a4452d66d15b51a7107d3821a`와
`6728b3dff175efe673c1d6a402f5d9f548127a20960a6efdf9047dae1e36ecfb`입니다.

`skills/domain-shaped-code/references/comments.md`와 `skills/review-quality/SKILL.md`는 로컬에서
새로 작성했으며 특정 upstream 파일을 복사하지 않았습니다.

## 적용한 변환

- `domain-shaped-code`는 실제 domain contract와 trust boundary를 우선하고, domain structure가
  실제 invalid state, 반복 rule 또는 분기를 제거할 때만 별도 모델을 사용합니다.
- TypeScript 지침은 inference를 기본으로 두고 branded type, exhaustive machinery, `unknown`,
  guard, annotation과 assertion을 실제 위험과 reader cost에 따라 조건부로 사용합니다.
- Ponytail 계열에서는 persistent mode, 응답 길이 강제, 고정 최소 테스트 형식과 보조 UX를
  제거하고 구현·diff review·repository audit의 독립 lens로 분리했습니다.
- Thermo 계열에서는 고정 1,000줄 기준과 구조 변경 자체를 목표로 하는 표현을 제거하고 reader
  load, 여러 변경 이유, 중복 domain knowledge와 public surface를 실제 finding 근거로 삼습니다.
- OpenAI prompt는 도달 가능하고 영향이 있는 failure mode만 현재 entry point와 호출 경로에
  근거하여 보고하도록 제한했습니다. 최종 수정 파일에 Apache-2.0 modified-file notice를
  표시했습니다.
- Addy Osmani와 Matteo Collina 자료는 모든 production feature·endpoint에 telemetry를 요구하거나
  Pino, Fastify, OpenTelemetry, correlation ID와 모든 async `try/catch`를 강제하지 않습니다.
  오류 소유권과 실제 운영 질문을 기준으로 error handling과 logging을 통합했습니다.

Apache-2.0 source를 실질적으로 변형하므로 플러그인 전체의 배포 라이선스는 Apache-2.0입니다.
MIT 원문의 저작권과 permission notice는 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)에,
OpenAI NOTICE는 [`NOTICE`](NOTICE)에 유지합니다.

## Consulted only

다음 자료는 아이디어와 제외 규칙을 확인했지만 파일을 포함하거나 문구·코드·예시를 복사하지
않았습니다.

- `cursor/plugins@efa2a531985e0a8084d36ff3cf87233be8a9f34b`
  - `pstack/skills/principle-boundary-discipline/SKILL.md`
  - `pstack/skills/principle-minimize-reader-load/SKILL.md`
  - `pstack/skills/principle-subtract-before-you-add/SKILL.md`
  - `pstack/skills/principle-type-system-discipline/SKILL.md`
- `openai/codex-plugin-cc@db52e28f4d9ded852ab3942cea316258ae4ef346`
  - `plugins/codex/commands/adversarial-review.md`
- [TypeScript Handbook: Type Inference](https://www.typescriptlang.org/docs/handbook/type-inference.html)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- OpenTelemetry Logs Data Model, Exceptions in Logs와 General Events semantic conventions

해당 source를 나중에 직접 incorporate하면 exact commit, source path, baseline path, final path,
SHA-256과 라이선스 고지를 먼저 이 문서에 추가합니다.

## Update method

1. 각 repository의 새 exact commit을 선택하고 license·notice 변화를 확인합니다.
2. 새 원본을 별도 `upstream/` 경로에 byte-for-byte로 가져와 bytes, mode와 SHA-256을 검증합니다.
3. 새 baseline commit을 로컬 customization과 분리해 기록합니다.
4. 현재 final mapping에 upstream 변경을 적용하고 로컬 정책을 재적용합니다.
5. manifest, references, marketplace, 실제 Codex loading과 routing evidence를 다시 검증합니다.
