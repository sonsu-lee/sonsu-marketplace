# Upstream source

- Repository: <https://github.com/coji/natural-japanese>
- Commit: `9a78a42964096da509b8f3e011f0085a5f080151`
- Main HEAD verified: 2026-09-25
- Skill: `natural-japanese`
- License: [MIT](THIRD_PARTY_NOTICES.md)

The source material is copied from the pinned upstream commit. The package manifest, README, and license notice are local packaging material. The installed public skill ID is `fluent-japanese:fluent-japanese`; `natural-japanese` remains the upstream skill name.

The installed skill bundle is under `skills/fluent-japanese/`.

Local changes in `SKILL.md` rename the skill, restructure the upstream workflow into procedure, result, example, boundary, and reference sections, clarify installed script paths, and include everyday messages and technical explanations. Technical document structure and Markdown formatting remain outside its scope. Short chat replies without a document use visual checks; the upstream lint process still applies to document writing, editing, and scoring. Numeric scoring uses an existing document and retains the upstream under-100-character cutoff. The upstream `argument-hint` frontmatter field was removed for the Agent Skills schema; its modes remain documented in the body.

Local supporting changes:

- `skills/fluent-japanese/scripts/score.py` and the package-level `tests/test_score.py` compute the score formula from `references/diagnose.md`; the reference documents the command and output fields.
- `skills/fluent-japanese/scripts/calibrate.py` is not packaged because it requires the upstream research corpus, which is not distributed.
- `references/revision-guide.md`, `references/manual-checklist.md`, `scripts/lint.py` comments, and fixture headers describe current behavior; calibration history remains in the pinned upstream commit.
- Four supporting files have an extra blank line at EOF removed for the repository diff check.
