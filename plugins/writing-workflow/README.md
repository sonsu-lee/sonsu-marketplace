# writing-workflow

Write and refine natural Korean, English, and Japanese prose while preserving
meaning and author voice.

Three source-based skills provide one editorial workflow per language. This
plugin does not translate text automatically, configure project-wide style
rules, or decide whether a person or an AI wrote a document.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [CLI](#cli)
  - [Skills and scope](#skills-and-scope)
- [Upstream sources](#upstream-sources)
- [Contributing](#contributing)
- [License](#license)

## Install

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
omp plugin install writing-workflow@sonsu-marketplace
```

For Codex, install the same package:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin add writing-workflow@sonsu-marketplace
```

### Dependencies

- Install [omp](https://github.com/can1357/oh-my-pi) or
  [Codex](https://developers.openai.com/codex/cli) first.
- Korean checks require Python 3.10 or newer.
- Japanese checks use Python 3.10 or newer and
  [uv](https://docs.astral.sh/uv/). The main linter uses SudachiPy and its
  dictionary; the first uncached run needs network access. The skill documents
  a manual-checklist route for environments without uv.
- The English skill needs no external executable or service.

Install prerequisites separately. Do not change a project's existing tool
configuration merely to edit its prose.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
```

In either client, ask for the writing task naturally:

```text
Refine this Korean API guide without changing its commands, identifiers,
response codes, numbers, terminology, or level of certainty.

Write an English email from these notes. Keep the commitments and dates exact
and use the same friendly, direct tone as the supplied writing sample.

Draft a Japanese explanation from these notes, then check its readability.
Do not invent a conclusion or strengthen an unconfirmed claim.
```

Use the skill for the language of the output, not the language of the request.
For mixed-language documents, preserve other-language passages unless asked to
edit them. Apply only one editorial workflow to each passage.

Codex also supports explicit `$humanize-korean`, `$ce-noslop`, and
`$natural-japanese` selection. Natural-language selection is model behavior,
not an installation hook; listing plugins does not prove skill execution.
Both clients use the same rules, roles, scripts, and assets. Resolve resources
from the actual loaded `SKILL.md` directory, not the target repository or a
guessed cache path. Codex uses ordinary file paths; omp's `skill://` is only
a reading convenience. Python and uv always receive absolute filesystem paths.

### Skills and scope

- [humanize-korean](skills/humanize-korean/SKILL.md) refines existing Korean
  prose. For new writing, draft from the user's notes or authorized sources
  first, then apply the editing workflow. Technical documents are eligible:
  README files, API references, design documents, runbooks, release notes,
  technical blogs, and prose embedded in code-bearing documents. Protect code,
  identifiers, commands, URLs, numbers, direct quotations, and technical terms;
  do not exempt the surrounding prose from editing.
- [ce-noslop](skills/ce-noslop/SKILL.md) writes, edits, or diagnoses English
  prose. It distinguishes neutral work artifacts from the user's own voice
  and preserves factual content and uncertainty.
- [natural-japanese](skills/natural-japanese/SKILL.md) writes, edits, or
  diagnoses Japanese prose with genre-specific guidance and an optional author
  style profile. Its mechanical findings require contextual judgment.

Writing clearly does not require casual language. Preserve the requested
formality, audience, document purpose, and meaningful technical structure.
A passed mechanical check is not proof that a revision is more natural or that
all meaning has survived. Review the actual output against its source.
The Korean numerical check compares signed values, not unit expressions.
Unit preservation remains part of direct source-to-output review; the plugin
does not add a unit registry or quantity-conversion engine.

The Korean helper uses `report` as a metric proxy for technical prose; it has
no dedicated calibrated technical-document baseline. Do not edit legitimate
terminology or structure to improve a numerical score. The Japanese adaptation
does not include the upstream experimental semantic model or `exp` mode.

## Upstream sources

These are local adaptations of fixed upstream revisions, not automatic mirrors.
Instructions are in English; Korean and Japanese examples retain their original
language. Source licenses are bundled with each skill.

- **humanize-korean:** [epoko77-ai/im-not-ai][ko-source] at
  `b37e0206d31fffd9149bf57168d4d62eb2086bee`. Adapted for standalone omp and Codex
  use and all Korean prose genres, explicitly including technical documentation.
  Numbered procedure steps remain editable; actual referenced footnotes stay
  protected.
- **ce-noslop:** [EveryInc/compound-engineering-plugin][en-source] at
  `2e41b4490a37f53db0beb6d4904618da9af2f559`. Restricted to English in this
  collection; unsupported client metadata and uninstalled sibling dependencies
  are removed.
- **natural-japanese:** [coji/natural-japanese][ja-source] at
  `03bc944a0c4a9f0b2a66eab065b30de5c529bf08`. Adapted to portable metadata,
  English instructions, and self-contained skill resources.

## Contributing

Questions and pull requests are welcome in the
[marketplace repository](https://github.com/sonsu-lee/sonsu-marketplace/issues).
Follow its [authoring and testing procedures](../../README.md#adding-a-plugin).
Keep upstream notices and revision references when updating an adaptation.
Use separate temporary homes: `HOME` for omp, plus `HOME` and `CODEX_HOME` for
Codex. Never install test plugins into live clients or copy real settings or
credentials. Follow the root [test procedure](../../README.md#testing-a-plugin)
for discovery, model access, and missing-resource checks. Exercise prose and
protected-content boundaries separately from format and discovery.

Run the Korean and Japanese regression tests from the marketplace root:

```sh
uv run --with 'sudachipy>=0.6.8' --with 'sudachidict-core>=20240409' \
  python -B -m unittest discover -s plugins/writing-workflow/tests -v
```

The suite uses the Japanese runtime's existing dependencies. It covers Korean
protected-content fidelity and Japanese structural lint and baseline transitions.

## License

[MIT](../../LICENSE) for marketplace adaptations, copyright sonsu-lee.
Upstream portions retain their respective MIT notices:
[epoko77-ai](skills/humanize-korean/LICENSE),
[Every](skills/ce-noslop/LICENSE), and
[coji](skills/natural-japanese/LICENSE).

[ko-source]: https://github.com/epoko77-ai/im-not-ai/tree/b37e0206d31fffd9149bf57168d4d62eb2086bee
[en-source]: https://github.com/EveryInc/compound-engineering-plugin/tree/2e41b4490a37f53db0beb6d4904618da9af2f559/skills/ce-noslop
[ja-source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
