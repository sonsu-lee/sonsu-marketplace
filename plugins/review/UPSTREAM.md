# Review upstream provenance

Review의 집중 관점 리뷰 스킬은 여러 upstream의 제한된 파일을 기반으로 합니다. 원본은
commit `538c9e9b8130a0f6cf56780a7700a983f77524de`에서 당시 Quality Engineering의 `upstream/`
아래에 byte-for-byte로 보존했고, 다음 customization commit에서 최종 `skills/` 경로로 이동해
수정했습니다. 현재 파일은 원본과 byte-identical하지 않으며, baseline commit이 원문 비교 기준입니다.

로컬 작성 자료의 MIT 저작권과 permission notice는 [LICENSE](LICENSE)에 있습니다. 아래 mapping의
자료는 [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0), [NOTICE](NOTICE)와
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)의 조건을 따릅니다.

## 기준 source

| Source | Commit | License | 확인 결과 |
| --- | --- | --- | --- |
| [`cursor/plugins`](https://github.com/cursor/plugins) `thermos` | [`efa2a531985e0a8084d36ff3cf87233be8a9f34b`](https://github.com/cursor/plugins/commit/efa2a531985e0a8084d36ff3cf87233be8a9f34b) | MIT, Copyright 2026 Cursor | skills.sh canonical source와 repository 경로를 함께 확인 |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | [`2ed6c52c9d7e5e56942508591085fd45dea277d3`](https://github.com/DietrichGebert/ponytail/commit/2ed6c52c9d7e5e56942508591085fd45dea277d3) | MIT, Copyright 2026 DietrichGebert | 지정 commit 고정 |
| [`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) | [`db52e28f4d9ded852ab3942cea316258ae4ef346`](https://github.com/openai/codex-plugin-cc/commit/db52e28f4d9ded852ab3942cea316258ae4ef346) | Apache-2.0, NOTICE Copyright 2026 OpenAI | 2026-09-02 당시 repository `HEAD`와 동일 |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | [`d2c37ef6225dd8726cdd369a8030307f48592d26`](https://github.com/addyosmani/agent-skills/commit/d2c37ef6225dd8726cdd369a8030307f48592d26) | MIT, Copyright 2025 Addy Osmani | 지정 commit 고정 |

OpenAI 저장소의 adversarial review는 `SKILL.md`가 아니라
`plugins/codex/prompts/adversarial-review.md`가 실제 review prompt이며,
`plugins/codex/commands/adversarial-review.md`가 이를 호출하는 command입니다. failure-mode lens에는
prompt를 사용했고 command runtime은 포함하지 않았습니다.

## Baseline과 최종 mapping

아래 SHA-256은 upstream 원본과 baseline commit의 `upstream/` 경로에서 동일했고, file mode는 모두
`100644`였습니다. 최종 파일에는 로컬 정책을 적용했습니다.

| Source relative path | Baseline path | Final path | Original SHA-256 |
| --- | --- | --- | --- |
| `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `upstream/cursor-plugins/thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `skills/review-maintainability/SKILL.md` | `7faca08b51b643b2ddd0836f92af15574444024685dcc1e677dbbb39ae8c9e8f` |
| `skills/ponytail-review/SKILL.md` | `upstream/ponytail/skills/ponytail-review/SKILL.md` | `skills/review-overengineering/SKILL.md` | `40df33b58fc6ef889b93585733feb9566b76e9586efa7f376785c1e995197ac0` |
| `skills/ponytail-audit/SKILL.md` | `upstream/ponytail/skills/ponytail-audit/SKILL.md` | `skills/audit-overengineering/SKILL.md` | `5560b8e383dbe2ddfddc873a1e2bf2e586e23e0cd7d995537482b2315331f6d1` |
| `plugins/codex/prompts/adversarial-review.md` | `upstream/codex-plugin-cc/plugins/codex/prompts/adversarial-review.md` | `skills/review-failure-modes/SKILL.md` | `f3b28a6c4c7501fd03ebab228050ac53c552a8f43c8aa517e924cb348aaefe0f` |
| `skills/observability-and-instrumentation/SKILL.md` | `upstream/agent-skills/skills/observability-and-instrumentation/SKILL.md` | `skills/review-operability/SKILL.md` | `bcec2ada212de6d07daa16886859cc0f2d954c845fc65fdbb7b23106df6aa8c0` |

`LICENSE-APACHE-2.0`과 `NOTICE`는 `openai/codex-plugin-cc/plugins/codex/`의 `LICENSE`와 `NOTICE`를 byte-for-byte로
가져왔습니다. SHA-256은 각각
`e591c02a0b2ea7717d99e15bd51ea05d879bbf5a4452d66d15b51a7107d3821a`와
`6728b3dff175efe673c1d6a402f5d9f548127a20960a6efdf9047dae1e36ecfb`입니다.

로컬 작성: `skills/review-code/SKILL.md`, `shared/review-core/javascript-typescript-review.md`는 로컬에서
새로 작성했으며 특정 upstream 파일을 복사하지 않았습니다.

## 적용한 변환

- Ponytail 계열에서는 persistent mode, 응답 길이 강제, 고정 최소 테스트 형식과 보조 UX를
  제거하고 diff review·repository audit의 독립 lens로 분리했습니다.
- Thermo 계열에서는 고정 1,000줄 기준과 구조 변경 자체를 목표로 하는 표현을 제거하고 reader
  load, 여러 변경 이유, 중복 domain knowledge와 public surface를 실제 finding 근거로 삼습니다.
- OpenAI prompt는 도달 가능하고 영향이 있는 failure mode만 현재 entry point와 호출 경로에
  근거하여 보고하도록 제한했습니다. 최종 수정 파일에 Apache-2.0 modified-file notice를
  표시했습니다.
- Addy Osmani 자료는 모든 production feature·endpoint에 telemetry를 요구하지 않습니다. 실제 운영
  질문을 기준으로 운용 가능성을 검토합니다.

Review는 로컬 MIT 자료와 Apache-2.0·MIT 품질 자료를 함께 배포합니다. Apache-2.0 source를
실질적으로 변형한 파일에는 [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0)이 적용됩니다. 포함한 MIT 원문의
저작권과 permission notice는 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)에, OpenAI NOTICE는
[`NOTICE`](NOTICE)에 유지합니다.

## Conventional Commits 인용

`references/conventional-commits.md`는 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
명세의 Summary 구조와 Specification 1–16을 원문 그대로 싣습니다. 명세 본문의 라이선스는
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)이며 이 저장소 코드의 MIT와 구분합니다.

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
- MDN의 nullish coalescing, optional chaining, `Map#get`, `JSON.stringify`, default parameters와
  `Promise.all` reference
- [typescript-eslint rules](https://typescript-eslint.io/rules/)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)

해당 source를 나중에 직접 incorporate하면 exact commit, source path, baseline path, final path,
SHA-256과 라이선스 고지를 먼저 이 문서에 추가합니다.

## Update method

1. 각 repository의 새 exact commit을 선택하고 license·notice 변화를 확인합니다.
2. 새 원본을 별도 `upstream/` 경로에 byte-for-byte로 가져와 bytes, mode와 SHA-256을 검증합니다.
3. 새 baseline commit을 로컬 customization과 분리해 기록합니다.
4. 현재 final mapping에 upstream 변경을 적용하고 로컬 정책을 재적용합니다.
5. manifest, references, marketplace, 실제 Codex loading과 routing evidence를 다시 검증합니다.

## 2026-09-15 독립 스킬 확장 참고

- 외부 설계 참고: [kdy1/kdy1-scripts](https://github.com/kdy1/kdy1-scripts/tree/92a8fbe9a57bce5064ed7dba3a8f87f331930dc6/skills), commit `92a8fbe9a57bce5064ed7dba3a8f87f331930dc6`.
- 참고 경로: `review-full/SKILL.md`.
- 원문 절차를 조사한 뒤 사용자와 합의한 계약에 맞춰 새로 작성했다. 원문 문구·helper 스크립트를 복제하지 않았다. 해당 snapshot에서 별도 LICENSE 파일을 확인하지 못했으며 설치 안내를 재배포 라이선스로 해석하지 않는다.
- 채택: 고정 리비전, 독립 리뷰와 원인별 중복 제거.
- 제외: 새 지적 없이 3회 연속까지 무제한 반복, 고정 CLI 의존, 자동 리뷰 게시.

2026-09-16 사용자 요청으로 PR 실행 계약을 수정했다. 일반·심층 PR 리뷰는 리뷰어별 별도
세션·워크트리에서 병렬 실행하고, 중복을 통합한 `COMMENT` 리뷰 게시까지 완료한다.
로컬 전용·게시 금지 요청은 우선한다. 불투명한 Codex 일시 실행 오류는 원인을 단정하지 않고
같은 모델·추론 설정으로 제한된 재시도를 수행한다. 이는 위 외부 snapshot에서 가져온 규칙이 아니다.
