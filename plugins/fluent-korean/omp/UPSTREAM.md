# Upstream source

- Repository: <https://github.com/epoko77-ai/im-not-ai>
- Commit: `92b2936956d65d62ff4b19b75cccad8e3429bf43`
- Main HEAD verified: 2026-09-25
- Skill: `humanize-korean`
- License: [MIT](THIRD_PARTY_NOTICES.md)

The source material is copied from the pinned upstream commit. The package manifest, README, and license notice are local packaging material. The installed public skill ID is `fluent-korean:fluent-korean`; `humanize-korean` remains the upstream skill name.

For Codex, `codex/skills/fluent-korean` contains the upstream single-call skill with references copied as regular files (the Codex plugin cache does not retain the upstream symlink). The canonical references live in `skills/fluent-korean/references`; regenerate `quick-rules.md` there with `scripts/build_quick_rules.py` and copy changed shared references into the Codex root. For Claude Code, `skills/fluent-korean` and the three runtime agent definitions provide the upstream multistep path. The upstream `scripts/` directory is bundled for that path, except the promotional image generators (`build_social_preview_v2.py`, `build_social_preview_v2_3.py`, `make_thumbnail.py`), the commit-ko helpers (`check_commit_lexicon_ids.py`, `commit_msg_lint.py`), and `eval_baseline.py`, whose fixtures and test harness are not part of this package.

Local changes in the two `SKILL.md` entrypoints rename the skill, restructure them as procedure, result, and example sections, and allow requested AI-style editing or diagnosis of existing everyday messages and technical prose. New Korean drafts apply local drafting rules; general chat answers, spelling correction, and translation remain outside its automatic scope. Short local edits can return in chat; requested file-based quantitative editing retains the upstream pipeline, whose Claude steps are kept in the local `references/file-workflow.md`. The Claude path allocates run directories through `prepare_monolith_input.py --text --session-tag`. Shared preservation rules from both entrypoints are consolidated in `quick-rules.header.md`, and the version history preamble of `ai-tell-taxonomy.md` is removed. The Claude frontmatter moves upstream `version` into `metadata.version` for the Agent Skills schema. Script and reference path literals were updated to the renamed directory. Two copies of `rewriting-playbook.md` have one trailing space removed for the repository diff check; other supporting rules and evaluation logic are copied from upstream.

- 새 글 생성 규칙 references/drafting-rules.md와 Claude 파일 윤문 절차 references/file-workflow.md는 로컬 추가이며 upstream에 없다.

For omp, scripts/render-omp-compat.py projects the Codex single-call skill and its references into an independent package. Only host guidance in the skill and quick-rules files is adapted; language patterns and preservation rules remain intact. The existing verify_change_rate.py and console.py domain validator scripts are copied without modification, with their metrics dependencies from the Codex references. The package uses the current host model and provides no Claude multistep or strict execution path.
