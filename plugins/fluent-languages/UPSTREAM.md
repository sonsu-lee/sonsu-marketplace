# Upstream provenance

The Korean and Japanese skills in this local Codex plugin are generation-oriented local adaptations. They are not byte-identical vendor snapshots of the referenced MIT-licensed projects.

The reusable local source is split at build time. `sources/core/` contains the shared communication and integrity contracts, while `sources/languages/` contains each entrypoint and its language guidance. `scripts/render-skills.py` combines every `sources/languages/<language>.md` file into a self-contained `skills/fluent-<language>/SKILL.md`; the core is not a separately triggered skill or runtime dependency.

This personal marketplace intentionally maintains the shared instruction source once in Korean. The language of those instructions does not select the response language; each generated skill's name, description, scope, and language-specific source do. A future externally distributed localization would require a separate equivalence review rather than independently edited core copies.

The cross-language discourse principles in `sources/core/communication.md` are local guidance derived from this marketplace's language-design review. They are not copied from or attributed to `im-not-ai`.

## `im-not-ai`

- Repository: <https://github.com/epoko77-ai/im-not-ai>
- Source commit: [`31a66d165a9cc6c26c4c1246553f95d0468d27fb`](https://github.com/epoko77-ai/im-not-ai/commit/31a66d165a9cc6c26c4c1246553f95d0468d27fb)
- Sources consulted:
  - [`docs/en/integration.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/docs/en/integration.md)
  - [`skills/humanize-korean/references/quick-rules.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md)
  - [`skills/humanize-korean/references/ai-tell-taxonomy.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/ai-tell-taxonomy.md)
- Adapted subset: genre and register preservation, double-passive avoidance, promotional buzzword restraint, unsupported emphasis restraint, repeated conclusion restraint, unnecessary metaphor restraint, and a non-numeric final repetition check.
- Excluded: workspace handling, risk scores, severity grades, change-rate calculation, file-output workflow, and the diagnostic, rewrite, and finalizer multi-call pipeline.
- Local scope: Korean explanatory prose includes implementation reports, technical answers, and technical documents. Code, commands, logs, identifiers, protected literals, structure, facts, conditions, uncertainty, and obligation levels are preserved.

## `fluent-japanese`

- Repository: <https://github.com/sonsu-lee/fluent-languages>
- Source commit: [`d53bf65057445b3556efb6d7d011d49ed8a5aac7`](https://github.com/sonsu-lee/fluent-languages/commit/d53bf65057445b3556efb6d7d011d49ed8a5aac7)
- Sources consulted:
  - [`plugins/fluent-languages/skills/fluent-japanese/SKILL.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/plugins/fluent-languages/skills/fluent-japanese/SKILL.md)
  - [`docs/research/japanese-language-characteristics.md`](https://github.com/sonsu-lee/fluent-languages/blob/d53bf65057445b3556efb6d7d011d49ed8a5aac7/docs/research/japanese-language-characteristics.md)
- Adapted subset: context-sensitive subject omission, explicit role names at actor transitions, particle and predicate-argument clarity, modifier scope, structural punctuation, register selection, terminology, and conditional review of nominalization and passive voice.
- Local changes: ambiguous before-and-after examples that invented an actor or selected an unsupported interpretation were removed. The rules now defer to the shared integrity contract and apply to both technical and non-technical Japanese explanatory prose.
- Excluded: the coding-only split, subagent-specific workflow, fixed sentence length, unconditional subject restoration, and rules that treat active voice or verb forms as universal preferences.
- Validation status: the source was a pre-native-review beta. This local adaptation remains beta until representative model outputs receive Japanese native-speaker review.

## `no-ai-slop-ja`

- Repository: <https://github.com/53able/no-ai-slop-ja>
- Source commit: [`1773df932be3a13d576bfe15cc116720e6788323`](https://github.com/53able/no-ai-slop-ja/commit/1773df932be3a13d576bfe15cc116720e6788323)
- Upstream named by that project: [`petergyang/no-ai-slop@d30eddb9e04562234f2070b5ee63ca4649d9a05e`](https://github.com/petergyang/no-ai-slop/tree/d30eddb9e04562234f2070b5ee63ca4649d9a05e)
- Sources consulted:
  - [`skills/no-ai-slop-ja/SKILL.md`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/skills/no-ai-slop-ja/SKILL.md)
  - [`NOTICE`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/NOTICE)
  - [`tests/evaluation/README.md`](https://github.com/53able/no-ai-slop-ja/blob/1773df932be3a13d576bfe15cc116720e6788323/tests/evaluation/README.md)
- Adapted subset: false-positive safeguards for passive voice, `こと`, consecutive `の`, verbal nouns, abstract katakana terms, modifier scope, silent actor changes, over-polite phrasing, and repeated endings. The final soft audit also adapts its checks for formulaic throat-clearing, unsupported self-assessment of importance, and conclusions that add no information.
- Excluded: editing and detection modes, AI-authorship judgments, mandatory change summaries, scoring, and multi-step rewrite workflow.

## `natural-japanese`

- Repository: <https://github.com/coji/natural-japanese>
- Source commit: [`0f1cc1c5a4e2aa7590598c88a15c213a60d9545a`](https://github.com/coji/natural-japanese/commit/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a)
- Sources consulted:
  - [`readability-principles.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/skills/natural-japanese/references/readability-principles.md)
  - [`writing-constitution.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/skills/natural-japanese/references/writing-constitution.md)
  - [`skill-eval-findings.md`](https://github.com/coji/natural-japanese/blob/0f1cc1c5a4e2aa7590598c88a15c213a60d9545a/corpus/reports/skill-eval-findings.md)
- Adapted subset: conditional ordering of multiple modifiers, punctuation at real syntactic boundaries, and terminology choices based on the reader and established usage.
- Excluded: conclusion-first composition, conclusion-bearing headings, fixed paragraph roles, numeric style thresholds, doctype modes, lint scores, convergence loops, and mandatory concluding prescriptions.
- Evidence boundary: this import did not independently verify the Japanese writing books cited by `natural-japanese` or their exact pages. The adapted material is therefore attributed to this repository rather than presented as independently confirmed book-level evidence.

## Consulted but not incorporated

- [`j1nn0/skills@e762558662251e48b05de5c79f518e676ab97699`](https://github.com/j1nn0/skills/tree/e762558662251e48b05de5c79f518e676ab97699/skills/writing-ja) was reviewed for its fact, inference, judgment, and voice-preservation boundaries. Those concerns were already covered by the local shared core, so no separate runtime rule was imported.
- [`devswha/patina@dd73aab0a1542db37b838cfe396b621e9ef1b928`](https://github.com/devswha/patina/tree/dd73aab0a1542db37b838cfe396b621e9ef1b928) was reviewed as a pattern and evaluation catalog. Its scoring, numeric thresholds, rewrite workflow, and bootstrap Japanese patterns were not incorporated.
- [`gonta223/humanizer-ja@a1e343696e43aa50e7218891f3319ab22cde3464`](https://github.com/gonta223/humanizer-ja/tree/a1e343696e43aa50e7218891f3319ab22cde3464) was reviewed for common Japanese humanizer patterns. Rules that could invent facts, numbers, experiences or opinions, change uncertainty, force register variation, or rewrite formatting were not incorporated.

No source text, code, examples or test fixtures from these three repositories are incorporated in this version. A later adoption must add its exact source commit, paths, adaptation scope and license notices above.

## Japanese evidence consulted

- [Agency for Cultural Affairs, `公用文作成の考え方`](https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/93657201.html)
- [Japan Translation Federation, `JTF日本語標準スタイルガイド（翻訳用）第4.0版`](https://www.jtf.jp/pdf/jtf_style_guide.pdf)
- [Walker, Iida and Cote, Japanese discourse and zero pronouns](https://aclanthology.org/J94-2003/)
- [Mori, Nomura and Nitta, zero pronouns in Japanese instruction manuals](https://aclanthology.org/W97-1302/)

These references constrain when a Japanese rule applies. They do not establish that this skill's model outputs have passed native-speaker review.

The exact copyright and license text from each incorporated source is retained in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
