# Upstream source

- Repository: <https://github.com/epoko77-ai/im-not-ai>
- Commit: `92b2936956d65d62ff4b19b75cccad8e3429bf43`
- Main HEAD verified: 2026-09-25
- Skill: `humanize-korean`
- License: [MIT](THIRD_PARTY_NOTICES.md)

The source material is copied from the pinned upstream commit. The package manifest, README, and license notice are local packaging material. The installed public skill ID is `fluent-korean:fluent-korean`; `humanize-korean` remains the upstream skill name.

For Codex, `codex/skills/fluent-korean` contains the upstream single-call skill with references copied as regular files (the Codex plugin cache does not retain the upstream symlink). For Claude Code, `skills/fluent-korean` and the three runtime agent definitions provide the upstream multistep path. The upstream `scripts/` directory is bundled for that path.

Local changes in the two `SKILL.md` entrypoints rename the skill and allow requested AI-style editing or diagnosis of existing everyday messages and technical prose. New Korean drafts apply local drafting rules; general chat answers, spelling correction, and translation remain outside its automatic scope. Short local edits can return in chat; requested file-based quantitative editing retains the upstream pipeline. The Claude frontmatter moves upstream `version` into `metadata.version` for the Agent Skills schema. Script and reference path literals were updated to the renamed directory. Two copies of `rewriting-playbook.md` have one trailing space removed for the repository diff check; supporting rules and evaluation logic are otherwise copied from upstream.

- 새 글 생성 규칙 references/drafting-rules.md는 로컬 추가이며 upstream에 없다.

For omp, scripts/render-omp-compat.py projects the Codex single-call skill and its references into an independent package. Only host guidance in the skill and quick-rules files is adapted; language patterns and preservation rules remain intact. The existing verify_change_rate.py and console.py domain validator scripts are copied without modification, with their metrics dependencies from the Codex references. The package uses the current host model and provides no Claude multistep or strict execution path.
