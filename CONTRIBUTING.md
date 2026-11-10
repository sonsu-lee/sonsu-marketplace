# Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow the
[PR writing procedure](plugins/git-workflow/skills/writing-pull-requests/SKILL.md)
when preparing a PR. For plugin changes, follow the authoring and testing
procedures below.

## Table of Contents

- [Layout](#layout)
- [Code review](#code-review)
- [Writing documentation](#writing-documentation)
  - [Document ownership](#document-ownership)
  - [Translations](#translations)
- [Decision records](#decision-records)
- [Adding a plugin](#adding-a-plugin)
- [Testing a plugin](#testing-a-plugin)
  - [Evaluating skills](#evaluating-skills)
  - [Manual scenario checks](#manual-scenario-checks)
  - [Running checks in CI](#running-checks-in-ci)

## Layout

```text
.omp-plugin/
  marketplace.json            # catalog: name, owner, plugins[]
.agents/plugins/
  marketplace.json            # Codex catalog: same package roots
.claude-plugin/
  marketplace.json            # Claude Code catalog: same package roots
.github/
  actions/setup-clients/      # installs the CI toolchain and locked clients
  ci-clients/                 # omp, Codex, Claude Code versions and bun.lock
  workflows/checks.yml        # model-free checks on every pull request
  workflows/pr-title.yml      # PR title against the commit rules
plugins/
  <name>/
    plugin.json               # shared identity, version, standard metadata
    README.md                 # user guide: install, usage, limits
    skills/<skill>/SKILL.md   # Agent Plugins: skills
    skills/<skill>/evals/     # Agent Skills evals: evals.json,
                              #   eval_queries.json, files/
    mcp.json                  # Agent Plugins: MCP servers
    commands/<command>.md     # omp: slash commands, run as /<name>:<command>
    agents/<agent>.md         # omp: task subagents
    rules/<rule>.md           # omp: rules
    package.json              # omp: extension modules under "omp.extensions"
    .claude-plugin/plugin.json  # Claude Code: only to exclude omp agents
scripts/
  check_plugins.py            # model-free checks for omp, Codex, Claude Code
  check_version_bumps.py      # changed plugins raised their version
  tests/                      # model-free tests for check_plugins and
                              #   evaluating-skills
```

Each plugin is an [Agent Plugins](https://agent-plugins.org/) 1.0.0 package.
All three catalogs point to the same `plugins/<name>` directories, relative to
the repository root. Standard metadata, skills, scripts, and assets are shared;
omp agents and client-specific execution references remain separate.
omp-specific components use omp's conventional locations because omp does not
yet read the standard's `extensions` field or namespaced extension directories.
Claude Code takes its manifest from the catalog entry or a package's
`.claude-plugin/plugin.json`, not from the root `plugin.json` or `mcp.json`.
Claude Code `2.1.296` still records the root `version` at installation, so
keep every declared version equal.
Everything except `plugin.json` and `README.md` is optional. Do not duplicate
package trees, add `.codex-plugin` overlays, symlinks, or empty MCP files for
these packages.
The packaging rationale remains [ADR-0002](docs/decisions/0002-plugin-format.md);
the proposed cross-client design is
[ADR-0005](docs/decisions/0005-share-plugins-across-clients.md).

## Code review

Apply [Code Review Rules](AGENTS.md#code-review-rules) when reviewing changes
and interpreting feedback. Requested plugin reviews use the
[reviewing-code procedure](plugins/review-workflow/skills/reviewing-code/SKILL.md)
and the matching [omp execution reference](plugins/review-workflow/skills/reviewing-code/references/omp.md),
[Codex execution reference](plugins/review-workflow/skills/reviewing-code/references/codex.md),
or [Claude Code execution reference](plugins/review-workflow/skills/reviewing-code/references/claude-code.md).
omp dispatches native and focused reviewers, plus `skill-workflow-reviewer` when
the change touches a skill; Codex and Claude Code dispatch independent custom
general and focused reviewers. Explicit native-only requests retain `/review`,
`codex review`, or `/code-review`, without plugin
orchestration. Preserve native output and priority contracts only when using a
native reviewer; custom controllers use the common skill's report contract.
Results stay local unless publication is explicitly requested; a draft is not
permission to post. These procedures do not replace required approvals or
branch protections.

When responding to review:

1. Evaluate the observation, whether it needs a change in this PR, and the
   proposed solution separately. A valid observation does not automatically
   justify the suggested implementation or a new rule.
2. Address in-scope defects with the smallest sufficient change. Explain
   declined or deferred feedback in the existing discussion; do not turn
   non-blocking advice into required work or silently expand the PR's purpose.
3. On re-review, check the agreed correction and its effects against the
   original requirement. New consequential defects remain reportable; a
   different preference alone is not a reason to reopen a settled choice.

The local policy draws on [Codex customization][codex-review],
[Google's review standard][review-standard], and
[Conventional Comments][review-comments]. Comment intent labels do not override
Codex's supported output or priority filtering. Refine the guidance against
actual review results, narrowing or removing rules that produce noise.

[codex-review]: https://learn.chatgpt.com/docs/third-party/github#customize-what-codex-reviews
[review-standard]: https://google.github.io/eng-practices/review/reviewer/standard.html
[review-comments]: https://conventionalcomments.org/

## Writing documentation

Write documentation in English, except the Korean translations described in
[Translations](#translations), and follow the
[Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
when creating or updating README files, as recorded in
[ADR-0003](docs/decisions/0003-use-standard-readme.md).

Adapt [Ponytail's smallest-complete-change principle][ponytail] to documentation:
start with what the reader needs to understand or do. Update an existing
document or link to its authoritative procedure before creating a new guide.
Keep each rule in its owning procedure; a link must make clear when the reader
needs it. Omit repeated explanations and examples that resolve no ambiguity.
When shortening text, preserve prerequisites, approval boundaries, exceptions,
and verification steps. Judge the result by whether the reader can still
complete the task, not by its length.

[ponytail]: https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md

For root and plugin READMEs:

- Use the project name as the title and a short description under 120
  characters, consistent with package and repository metadata where applicable.
- Include `Install`, `Usage`, `Contributing`, and a final `License` section in
  that order. The license section identifies the license and its owner.
- Include a table of contents for documents of 100 lines or more and keep its
  links synchronized with headings.
- Show installation and common usage in code blocks. Put manually installed
  prerequisites under `Install` / `Dependencies` and CLI examples under
  `Usage` / `CLI` where applicable.
- Put marketplace-specific sections after `Usage`. In `Contributing`, state
  where to ask questions and whether pull requests are accepted, and link to
  this guide instead of repeating repository procedures. A plugin README may
  add checks specific to its package.
- Omit optional sections that add no value. Keep decision rationale in ADRs.
- Inspect rendered navigation and code blocks, check links and license
  information, and exercise changed CLI examples. Use isolated client homes
  and follow the plugin test procedure below, including Codex's `CODEX_HOME`
  and Claude Code's `CLAUDE_CONFIG_DIR`.

Repository Markdown files follow the lint policy in
[ADR-0004](docs/decisions/0004-require-markdown-lint.md), including READMEs, ADRs,
agent instructions, skills, commands, and rules. Before pushing, use Node.js 22
or newer and npm to check the files added or modified by your change, using the
pinned CLI's default rules:

```sh
npx --yes markdownlint-cli@0.49.1 README.md
```

Append the paths of any other Markdown files added or modified by your change,
including ADRs. Fix all reported lint errors, then check links and the rendered
Markdown; lint does not verify Standard Readme compliance or visual layout.
Untouched documents do not need a repository-wide reformat. This is a validation
step, not automatic formatting; the `checks` workflow runs the same command on
the Markdown files a pull request adds or modifies.

This file-lint policy and its line-length rule do not apply to PR bodies, even
when saved to a temporary `.md` file for `--body-file`. Follow the
[PR writing procedure](plugins/git-workflow/skills/writing-pull-requests/SKILL.md#write-the-body):
keep each prose paragraph on one source line, with blank lines between
paragraphs and structural newlines for lists, tables, and code blocks. GitHub
renders single newlines in PR bodies as visible line breaks, unlike repository
`.md` files.

### Document ownership

Keep responsibilities separate so readers need not reconstruct current rules
from decision history:

- **Root `README.md`:** Choosing a plugin, and installing, invoking, and
  updating plugins in each client.
- **`plugins/<name>/README.md`:** One plugin's prerequisites, usage, limits,
  and skill links, plus checks specific to that package.
- **`CONTRIBUTING.md`:** Repository-wide procedures for authoring, review,
  documentation, decision records, testing, and CI.
- **Skills:** Task instructions and their precedence rules, which travel with
  each plugin.
- **Configuration files:** Executable rules and values.
- **`docs/`:** Supporting records, currently the ADRs in `docs/decisions/`:
  rationale, alternatives, tradeoffs, and links to current instructions.
- **`AGENTS.md`:** Agent obligations and links to the procedures above.

When adding or changing a requirement, update its operational source and ensure
`AGENTS.md` identifies when it applies and which procedure to follow. Add or
adjust that routing in the same change if needed. Do not leave an active
requirement only in an ADR. ADRs should link to current instructions rather
than duplicate commands or rule values. Git and PR history retain intermediate
revisions.

### Translations

Skill documents may have a Korean translation for human readers, stored next to
the English source as `<name>.ko.md`, for example `SKILL.ko.md` or
`references/craft.ko.md`. Translations cover only files inside a skill
directory, `plugins/<plugin>/skills/<skill>/`: its `SKILL.md`, `references/`,
and `agents/` files. Never translate plugin-level component directories such
as `plugins/<plugin>/agents/`, which omp loads as task agents, `assets/`
templates that skills copy into output, or `evals/` files.

- The English file is authoritative. Clients discover and load only the
  English files; a translation never adds or changes instructions.
- Omit frontmatter so no loader can mistake a translation for a skill. Start
  with the translated title, then this notice naming the source file and the
  last commit that changed it:

  ```markdown
  > 영문 정본: [SKILL.md](SKILL.md) (`5b362ef` 기준 번역).
  > 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.
  ```

- Translate prose only. Keep code, commands, paths, identifiers, and example
  text whose language matters unchanged. Links into other files keep their
  English targets; a link to a heading in the same file uses the translated
  heading's anchor.
- Updating a translation when its source changes is optional. Compare the
  noted commit with `git log -1 --format=%h -- <source>` to see whether a
  translation is behind, and refresh the notice whenever you update one.
  Renaming or deleting a source renames or deletes its translation in the same
  change.
- Translations follow the same Markdown lint as other files.

The root `README.md` and each plugin's `plugins/<plugin>/README.md` may also
have a Korean translation, `README.ko.md`, in the same directory; no other
README or document is translated. The rules above apply with these
differences:

- Start with the title, then the language line, then this notice without a
  commit: same-change updates keep the files in step, and squash merges would
  invalidate a recorded hash:

  ```markdown
  > 영문 정본: [README.md](README.md). 사람이 읽기 위한 번역본이며 내용이 다르면
  > 영문판을 따른다.
  ```

- Both files link to each other with a language line under the title.
- Updating the translation is required: a change to a translated `README.md`
  updates its `README.ko.md` in the same pull request, because outdated
  installation steps mislead users.

## Decision records

Follow [Martin Fowler's ADR writing and lifecycle guidance][adr-fowler].
Use the [ADR writing procedure][adr-skill] and the
[lightweight template][adr-template], adapted from [Evolu][adr-evolu-template].
The repository's scope below deliberately narrows the broader ADR practice;
Fowler does not prescribe this template or our selection threshold.

Write an ADR only for a coherent choice that sets the marketplace's or a
plugin's direction or consequential design constraints: purpose and supported
scope, fundamental structure, public contracts, security boundaries, or key
quality attributes. Explain the continuing constraint or substantial reversal
cost. Affecting many files or future tasks is not enough.

- Packaging portability versus client-specific capabilities is an ADR topic.
  Applying the selected packaging format is not.
- Routine features and fixes, document formats, lint commands, version bumps,
  and review procedures belong in code, configuration, the
  [owning document](#document-ownership), or skills.
  Record one only if it actually changes the direction or design constraints
  above, not merely because it is a shared rule.
- An ADR explains a decision, not implementation steps, a work log, or a
  command reference. Search existing records before starting another.

Store records as `docs/decisions/NNNN-title-with-dashes.md`, numbered in sequence.
Use a title stating the decision, `Date` and `Status` metadata, and the template's
`Context`, `Decision`, `Rejected alternatives`, and `Consequences` sections.
State the choice and why in a few sentences; describe real alternatives rather
than inventing options to fill the template. Use the space needed to explain
the decision and tradeoffs, and link supporting evidence instead of duplicating
it. Record uncertainty or revisit conditions when they matter.

- Keep a record `proposed` while it is under review. Consolidate revisions of
  the same proposal in that record instead of creating a supersession chain.
- Mark it `accepted` only when the decision-maker has accepted the choice;
  finishing implementation or passing checks is not acceptance.
- When an accepted decision changes, write a replacement and link both records.
  Mark the old one `superseded` only after the replacement is accepted.
  Reconsideration that leaves the decision unchanged needs no new ADR.
- Preserve accepted records in their historical format, including records
  that would not meet today's narrower scope. Change only errors, links, or
  status, not their original decision and rationale.

The rationale is in
[ADR-0001](docs/decisions/0001-use-lightweight-directional-decision-records.md).
During initial setup on 2026-10-20, the maintainer authorized a one-time
consolidation of ADR-0001 rather than a separate supersession chain, and
reformatting ADR-0002 through ADR-0004 without changing their choices,
decision dates, or rationale. Git retains the earlier MADR policy and document
forms. This exception is limited to that initialization cleanup; it does not
authorize further rewrites or resets. Subsequent decisions follow the lifecycle
above.

On 2026-10-23 the maintainer separately authorized one correction to
ADR-0004: its Decision ended with "Do not add … a new CI integration", an
operational constraint that, under the scope above, belongs in the contributor
procedures rather than a decision record. The clause was removed, so
[Writing documentation](#writing-documentation) now owns
where the lint runs, including the `checks` workflow. The choice to require the
pinned lint and its rationale are unchanged. This does not authorize other
rewrites.

Document responsibilities, including what ADRs own, are in
[Document ownership](#document-ownership).

[adr-fowler]: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[adr-skill]: plugins/decision-workflow/skills/writing-adrs/SKILL.md
[adr-template]: plugins/decision-workflow/skills/writing-adrs/assets/adr.md
[adr-evolu-template]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/template.md

## Adding a plugin

1. Create `plugins/<name>/plugin.json`:

   ```json
   {
     "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
     "name": "<name>",
     "version": "0.1.0"
   }
   ```

   Use only the fields the standard defines: `$schema`, `name`, `version`,
   `description`, `author`, `homepage`, `repository`, `license`, `keywords`,
   and `extensions`. omp rejects the whole plugin if a defined field is
   invalid, for example an uppercase `name`.

   Also add `plugins/<name>/README.md`, the plugin's user guide, following
   [Writing documentation](#writing-documentation).

2. Add the standard components:
   - **Skills**: `skills/<skill>/SKILL.md` following the
     [Agent Skills specification](https://agentskills.io/specification). The
     frontmatter may contain only `name`, `description`, `license`,
     `compatibility`, `metadata`, and `allowed-tools`, and `name` must match
     the directory name. omp skips a skill with any other field, such as omp's
     `hide` or Claude Code's `argument-hint`.

     When creating, revising, or reviewing a skill, follow the
     [skill-authoring procedure](plugins/skill-workflow/skills/authoring-skills/SKILL.md),
     grounded in the [creator best practices][skill-practices]. Keep judgment
     and the minimum workflow in the skill, delegate mechanical work to existing
     tools, and say when supporting files should be read. Use its
     [evaluation guidance](plugins/skill-workflow/skills/authoring-skills/references/evaluation.md)
     when selecting checks; the packaging and execution procedures below remain
     the source for this marketplace's validation commands. Keep each skill's
     evaluation files in `skills/<skill>/evals/` as
     [Evaluating skills](#evaluating-skills) describes.

   - **MCP servers**: `mcp.json` with the
     `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` `$schema` and an
     `mcpServers` object. Each server sets `type` (`stdio`, `streamable-http`,
     or `sse`). A `stdio` `command` is a bare executable name or a `./` path.
     Use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in `args`, `env`, and `cwd`; omp
     expands nothing else. Keep secrets out of `mcp.json`. A `stdio` server
     receives omp's environment and can read credentials from it.

   Keep one standard package root for all clients; do not add `.mcp.json` or
   `.codex-plugin/plugin.json` overlays. Shared skills and MCP servers live in
   `skills/` and `mcp.json`. Claude Code reads MCP servers from `.mcp.json` or
   manifest `mcpServers`, not `mcp.json`; before adding MCP servers, decide and
   verify how Claude Code receives them or disclose that they are unavailable.

3. Add omp-specific components only when needed:
   - **Commands**: `commands/<command>.md` with a `description`. Use a command
     for a workflow that runs only when the user asks for it, since a standard
     skill cannot set `hide`. Claude Code also loads `commands/` as plugin
     commands, and omp may read a Claude Code manifest's `commands` field; no
     package ships a command yet, so verify both before adding one.

   - **Agents**: `agents/<agent>.md` with `name` and `description`. Claude Code
     also loads `agents/` as its own plugin subagents and cannot exclude them
     from a catalog entry. A package with omp agents therefore adds
     `.claude-plugin/plugin.json` with `"agents": []` and its Claude Code
     metadata, as `review-workflow` does. omp still loads `agents/`, but reads
     that manifest's `version` before the root `plugin.json`.

   - **Rules**: `rules/<rule>.md` with a `description`. Use a rule for guidance
     tied to file patterns (`globs`) or that always applies (`alwaysApply`),
     since a standard skill cannot set these fields.

   - **Code** (tools, event handlers, commands with logic): extension modules
     listed in `package.json` under `omp.extensions`. See
     [Extensions](https://github.com/can1357/oh-my-pi/blob/main/docs/extensions.md).

   Keep client execution differences in conditional skill references.
   Do not copy omp agents into Codex host configuration or Claude Code agent
   definitions.

   When adding another client, retain one source package per plugin and share
   common workflow requirements, scripts, and assets. Separate only necessary
   client metadata, components, and execution procedures. Use supported client
   capabilities; disclose unavailable requirements rather than silently weaken
   the workflow. A different model alone does not require a package fork.
   Document the new client's actual support scope and verify its installation,
   discovery, and representative execution before claiming compatibility;
   the current omp, Codex, and Claude Code checks do not establish support for
   other clients.

4. Register the plugin in `.omp-plugin/marketplace.json`:

   ```json
   {
     "name": "<name>",
     "source": "./plugins/<name>",
     "description": "What the plugin does.",
     "version": "0.1.0"
   }
   ```

   Also register it in `.agents/plugins/marketplace.json`:

   ```json
   {
     "name": "<name>",
     "source": {"source": "local", "path": "./plugins/<name>"},
     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
     "category": "Productivity"
   }
   ```

   Also register it in `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "<name>",
     "source": "./plugins/<name>",
     "description": "What the plugin does.",
     "version": "0.1.0"
   }
   ```

   Claude Code uses this entry as the manifest when the package has no
   `.claude-plugin/plugin.json`. With that manifest, the entry contains only
   `name` and `source`; the manifest carries `version`, `description`, and
   `author`, because a version in both places is a validation warning.

   All paths are relative to the repository root, not the catalog directory.
   Keep catalog names, order, and package sets aligned. The explicit Codex
   policy follows its catalog format; these skill-only packages add neither
   authentication dependencies nor automatic installation.

   Raise `version` in the root manifest, the omp catalog, and the Claude Code
   catalog entry or manifest together on every plugin change, except a change
   limited to the plugin's own `README.md` and `README.ko.md`: clients do not
   load them, so a reinstall changes no behavior.
   `omp plugin upgrade` and `claude plugin update` only reinstall changed
   versions. Codex uses package metadata; do not duplicate versions, omp
   `owner`, or marketplace `metadata` in its catalog.

Use the same name in `plugin.json`, every catalog entry, any Claude Code
manifest, and the directory. It must be lowercase ASCII letters, digits, `-`,
and `.`, start and end with a letter or digit, contain no `--` or `..`, and be
at most 64 characters.

If a future plugin needs a capability the standard cannot express, document
the client limitation before changing packaging or claiming shared support.
An unsupported client release is a prerequisite failure, not permission to
silently switch these shared packages to a legacy format.

## Testing a plugin

Run the model-free checks from the marketplace root after every plugin change.
They need Python 3.11 or newer, uv, network access on the first run, and the
omp, Codex, and Claude Code CLIs on `PATH`:

```sh
python3 scripts/check_plugins.py
```

The script installs the catalog into fresh temporary homes for each client and
runs every client command from a temporary directory with a minimal
environment, so clients never read live settings or credentials. Only the
`format` check runs uv with your normal environment and cache. The script
prints one line per check:

- `catalogs`: all three catalogs list the same packages in the same order,
  each source exists, and the root manifest, omp catalog, and Claude Code entry
  or manifest declare one version.
- `format`: each skill passes the pinned [reference validator][skills-ref],
  which checks frontmatter and naming, not task quality.
- `size`: each `SKILL.md` fits Codex's 8,000-byte plugin-skill limit.
- `validate`: `claude plugin validate --strict` accepts the catalog, any
  Claude Code manifest, and each package's skills.
- `install`: every package installs, and Codex lists each one as enabled.
- `discovery`: every skill appears exactly once, in omp's `skill list` without
  `warning:` lines, in Codex `skills/list` from installed paths without errors,
  and in Claude Code's `init` event without this marketplace's agents.
- `loading`: invoking each skill sends its complete `SKILL.md` body to a local
  receiver that records and rejects model requests, and Codex reports no
  truncation. The omp check waits for the invocation request rather than
  stopping on an earlier routing-hint request.

Skills come from `skills/*/SKILL.md` in each catalog package, so a new skill
needs no script change. Any `FAIL` line names the client and check and makes
the exit status nonzero. A missing CLI is a failure, not a skip;
`--clients omp,codex` limits a run while iterating, but report the full run.
`--root` checks another marketplace copy. The Claude Code check installs from
a local path, which loads packages in place; to inspect the cached copies a
Git-backed marketplace installs, add a committed clone over Git instead.

For `design-workflow` runtime changes, also follow its
[runtime verification procedure](plugins/design-workflow/README.md#verification):
exercise actual browser and process execution and SDK lifecycle gates. Discovery
and prompt loading do not establish that extension behavior works.

### Evaluating skills

The model-free checks above do not show whether a skill helps or when it
triggers. That takes the two Agent Skills loops:
[output quality][eval-outputs] and [description triggering][eval-descriptions].
Every skill keeps their files in its own `evals/` directory, in the
[formats](plugins/skill-workflow/skills/evaluating-skills/references/formats.md)
that skill-creator also reads. Behavior that one skill shows belongs in that
skill's evals; behavior across plugins, client settings, or installation
belongs in the [manual scenario checks](#manual-scenario-checks).

```mermaid
flowchart LR
  F["Skill evals/<br/>evals.json<br/>eval_queries.json<br/>files/"]
  C["evaluating-skills scripts<br/>run_evals, grade,<br/>aggregate, run_trigger_eval"]
  W["omp workspace<br/>runs, grading, timing"]
  V["benchmark.json<br/>review viewer and feedback"]
  F --> C --> W --> V
```

Follow the Agent Skills guides for case counts and repetitions; this
repository adds only the client, the model, and what a pull request reports.

**1. When to evaluate.**

- A change to a skill's behavior: run the output loop against the previous
  version from `origin/main` (or without the skill, for a new skill). Start
  with two or three cases that exercise the changed behavior, including one
  boundary case, and run each once per configuration. Keep earlier cases and
  add cases for a revised behavior or a gap the results reveal. Before
  claiming a delta that rests on one assertion in one run, repeat the
  evaluation in a new iteration with `--runs 3`.
- A change to a description: run each query in `eval_queries.json` three
  times; the full set must pass no fewer queries than before.
- Formatting-only edits need no evaluation.

**2. Client and model.** Evaluate in omp with the
[`evaluating-skills`](plugins/skill-workflow/skills/evaluating-skills/SKILL.md)
skill and the model most users run, `anthropic/claude-opus-5-5` with effort
`high`. Update the model when that changes.

**3. Prepare the evaluation home once.** Log in with a separate test account
and install nothing from this marketplace, since an installed skill also loads
in the baseline runs. Never copy a live home or its credentials:

```sh
HOMES="${XDG_CACHE_HOME:-$HOME/.cache}/sonsu-marketplace/client-homes"
mkdir -p "$HOMES/omp-home"
HOME="$HOMES/omp-home" omp login
```

**4. Run** from the marketplace root. This example compares `writing-adrs`
with its version on `origin/main`:

```sh
HOMES="${XDG_CACHE_HOME:-$HOME/.cache}/sonsu-marketplace/client-homes"
EVAL=plugins/skill-workflow/skills/evaluating-skills
SKILL=plugins/decision-workflow/skills/writing-adrs
WS="${XDG_CACHE_HOME:-$HOME/.cache}/skill-evals/writing-adrs-workspace"
IT="$WS/omp/iteration-1"
RUN=(--skill-path "$SKILL" --client omp --model anthropic/claude-opus-5-5
  --effort high --home "$HOMES/omp-home")

rm -rf "$WS/skill-snapshot" && mkdir -p "$WS/skill-snapshot"
git archive origin/main "$SKILL" |
  tar -x --strip-components=4 -C "$WS/skill-snapshot"

python3 "$EVAL/scripts/run_evals.py" "${RUN[@]}" --iteration 1 --baseline old
python3 "$EVAL/scripts/grade.py" "$IT"
python3 "$EVAL/scripts/aggregate_benchmark.py" "$IT" --skill-name writing-adrs
python3 "$EVAL/eval-viewer/generate_review.py" "$IT" \
  --skill-name writing-adrs --benchmark "$IT/benchmark.json"

python3 "$EVAL/scripts/run_trigger_eval.py" "${RUN[@]}"
python3 "$EVAL/scripts/run_trigger_eval.py" "${RUN[@]}" \
  --description "<previous description>"
```

**5. Report** in the pull request: model and effort, runs per configuration,
pass rates with the skill and the baseline and their delta, time and tokens,
trigger pass counts, runs not measured, and the gist of the review feedback.
Do not commit workspaces.

**6. Regression tests.** After changing the `evaluating-skills` scripts or any
skill's `evals/` files, run the model-free tests, which also check every
skill's evaluation files:

```sh
python3 -B -m unittest discover -s scripts/tests -v
```

### Manual scenario checks

Behavior that spans plugins, client settings, or installation cannot be
expressed as one skill's evals. Check it by hand when a change affects it.

- **omp:** use the evaluation home. **Claude Code:** use a test home with a
  saved token, created once as below. In both, load the working tree's plugins
  only for that session with `--plugin-dir "$REPO/plugins/<name>"`, repeated
  as needed, and do not install them into the homes.

  ```sh
  C="$HOMES/claude-home"
  mkdir -p "$C"
  HOME="$C" CLAUDE_CONFIG_DIR="$C/.claude" claude setup-token
  (umask 077; read -rs t; printf "%s" "$t" > "$C/oauth-token")
  ```

- **Codex:** use a separate scenario home, `$HOMES/codex-scenario-home`,
  because Codex has no per-session plugin loading. Log in once with
  `HOME="$HOMES/codex-scenario-home"
  CODEX_HOME="$HOMES/codex-scenario-home/.codex" codex login --device-auth`
  and register the marketplace once with
  `codex plugin marketplace add "$REPO" --json`. Before every round, run
  `codex plugin remove <plugin>@sonsu-marketplace` (ignore a not-installed
  error) and `codex plugin add <plugin>@sonsu-marketplace --json` for each
  plugin the scenario uses, so the installation matches the working tree. Run
  these commands from an empty temporary directory with the same variables.

```sh
REPO="$(git rev-parse --show-toplevel)"
HOMES="${XDG_CACHE_HOME:-$HOME/.cache}/sonsu-marketplace/client-homes"
WORK="$(mktemp -d)"
TARGET="$WORK/target"
mkdir -p "$TARGET"

(cd "$TARGET" && HOME="$HOMES/omp-home" omp -p --mode json \
  --plugin-dir "$REPO/plugins/review-workflow" \
  "Review the working changes in this repository.")

HOME="$HOMES/codex-scenario-home" \
  CODEX_HOME="$HOMES/codex-scenario-home/.codex" \
  codex --no-daemon exec --json --sandbox workspace-write \
  --add-dir "$WORK" -C "$TARGET" \
  '$review-workflow:reviewing-code Review working changes locally.'

(
  cd "$TARGET"
  HOME="$HOMES/claude-home" CLAUDE_CONFIG_DIR="$HOMES/claude-home/.claude" \
    CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOMES/claude-home/oauth-token")" \
    claude -p '/review-workflow:reviewing-code Review working changes.' \
    --output-format stream-json --verbose --add-dir "$WORK" \
    --plugin-dir "$REPO/plugins/review-workflow" \
    --permission-mode bypassPermissions
)
```

Codex uses `--no-daemon` to avoid attaching to the live client daemon. For
Claude Code, `CLAUDE_CONFIG_DIR` holds no login; supply the saved token
through `CLAUDE_CODE_OAUTH_TOKEN` in the process environment, and do not copy
the live configuration directory. Print mode cannot answer permission
prompts, and the default mode denies the snapshot, helper, and validator
commands these workflows run. For disposable targets only, grant them with
`--permission-mode bypassPermissions` and report that choice.

The stream records the controller's Agent calls and each subagent's tool calls
with a `parent_tool_use_id`; inspect them rather than only the final report.

Use remote-free disposable Git targets with normal behavior and a known
regression spanning staged, unstaged, and untracked changes. Observe independent
general/focused workers on the same frozen target, full completion results,
deduplicated findings, and controller-only runtime checks in another disposable
copy. Confirm original source, index, and untracked content remain unchanged.
omp must retain native `reviewer` plus a focused worker:
`review-workflow-focused`, or `skill-workflow-reviewer` for a skill-only
change. Codex must
not call native review or a recursive CLI; Claude Code must start non-fork
`general-purpose` subagents without `/code-review`, `/security-review`,
ultrareview, or a nested CLI. Check a clean baseline, implicit skill selection,
explicit native-only review, comment-only drafting, and unavailable subagents
(`-c agents.enabled=false` in Codex, `--disallowedTools Agent` in Claude Code).
Missing or failed workers must remain incomplete, not a sequential or
native-only fallback.

For skill reviews, use a disposable target whose skill change moves a safety
instruction into a reference without a loading condition. In omp with both
`review-workflow` and `skill-workflow` loaded, the review batch must include
`skill-workflow-reviewer`, and a code-only change must not. Creating or
changing a behavioral skill must also obtain this review. For standalone
Codex and Claude Code reviews, the extra worker remains user opt-in. An
implementation controller's skill-review assignment also triggers it without
another approval; the worker must read the loaded `authoring-skills`.

For execution, copy the contents of
`plugins/planning-workflow/skills/executing-work/evals/files/executing-csv/`
into a disposable Git target with one initial commit, load `planning-workflow`
and `review-workflow`, and send the prompt of eval 1 in that skill's
`evals/evals.json`. The client must load `executing-work`, change and test the
exporter, then load `reviewing-code` and complete its general and focused
workers on the final revision before reporting completion, without
committing, pushing, or publishing. Run omp with `--approval-mode yolo` only
in such disposable targets, as `run_evals.py` does, and report that choice.

Exercise the writing-workflow helpers from the directory each client loaded
them from, preserving identifiers, numbers, URLs, and fenced code. Then remove
one helper from a disposable copy (a copy of `plugins/writing-workflow` passed
to `--plugin-dir` in omp and Claude Code, or the installed copy in the Codex
scenario home, restored afterwards with `codex plugin remove` and
`codex plugin add`) and verify an explicit missing-resource result, not a
guessed cache path or false pass. Do not change the working tree's helpers.

Run each model scenario once by default from a fresh target, and repeat it
when results are inconsistent. Use the model in
[Evaluating skills](#evaluating-skills) for omp, `gpt-6-astra` for Codex, and
`claude-opus-5-5` for Claude Code, each with effort `high` passed explicitly
(`--model` and `--thinking` in omp, `-m` and `-c model_reasoning_effort` in
Codex, `--model` and `--effort` in Claude Code), and
report every run's outcome rather than only the best one. Report actual CLI
versions, discovery, execution traces, runtime evidence,
and precise blockers separately. Without authorized model access, complete
non-model checks but mark all unexecuted model scenarios unverified. Installation
does not prove review quality, automatic selection, or app/IDE behavior.

### Running checks in CI

When changing a workflow, pin what it runs, as
[ADR-0007](docs/decisions/0007-pin-ci-dependencies-to-immutable-content.md)
explains: reference each action by full commit SHA with its release tag in a
comment, and install CLI tools from `.github/ci-clients` with the frozen
lockfile rather than `npm install -g` or `bun install -g`. Node.js stays on
the latest 24.x patch through `check-latest`.

The `checks` workflow runs on every pull request and push to `main`, needs no
secrets, and enforces the agreed rules a machine can check:

- `plugins`: `scripts/check_plugins.py`, with the clients in
  `.github/ci-clients`. Its `package.json` names the
  [checked versions](README.md#dependencies),
  and `bun.lock` pins every dependency by integrity hash; CI installs them with
  `bun install --frozen-lockfile`, which skips dependency install scripts.
  After changing a version, run `bun install` there with the Bun version set in
  `.github/actions/setup-clients` and commit the new lockfile.
- `markdown`: the pinned Markdown lint command above on added or modified
  Markdown files.
- `versions`: `scripts/check_version_bumps.py <base>` fails when files under a
  plugin, other than its own `README.md` and `README.ko.md`, changed but its
  `plugin.json` version did not; the `catalogs` check keeps the catalogs equal
  to that version.
- `writing-workflow-tests` and `git-workflow-tests`: the behavior tests below,
  when files under those plugins change.
- `script-tests`: the model-free tests in `scripts/tests`, when files under
  `plugins/` or `scripts/` change. They cover the `evaluating-skills` runner,
  every skill's evaluation files, and the plugin-loading receiver.
- `design-workflow-tests`: the plugin's TypeScript check and model-free engine,
  real Chromium/process and SDK lifecycle regressions when its package changes.
  TypeScript and the browser installation CLI are locked in `.github/ci-clients`;
  the pinned browser package selects its Chromium revision. Operator UI choices
  in the SDK regression are simulated; visual quality is still human judgment.

The `pr-title` workflow checks the pull request title, which becomes the squash
commit subject, with the
[writing-commits defaults](plugins/git-workflow/skills/writing-commits/SKILL.md),
since this repository has no commitlint configuration of its own. The rule
checks compare against the pull request's merge base or the pushed range, and
skip on manual runs.

Model runs stay out of this repository's CI, as
[ADR-0006](docs/decisions/0006-keep-model-evaluations-local.md) explains: its
workflow logs are public, and an agent under test can read the credentials it
runs with. Run the [skill evaluations](#evaluating-skills) locally in the
dedicated test homes and report the models and results in the pull request.

For changes to `writing-workflow` runtime helpers, also run its behavior tests:

```sh
uv run --with 'sudachipy>=0.6.8' --with 'sudachidict-core>=20240409' \
  python -B -m unittest discover -s plugins/writing-workflow/tests -v
```

The tests cover Korean protected-content fidelity and Japanese structural lint
and baseline transitions, using the Japanese runtime's existing dependencies.

For changes to `git-workflow` validation, also run its behavior tests:

```sh
node --test plugins/git-workflow/tests/commitlint.test.mjs \
  plugins/git-workflow/tests/branch-validation.test.mjs
```

The tests run the pinned commitlint and commit-check CLIs through `npx` and
`uvx` in temporary Git repositories. After installing the plugin into a
temporary `HOME`, also exercise both skills' validation procedures from a
separate repository using their installed assets and reference guides. Verify
repository-owned executables, versions, and configuration remain in use when
present, and failures are not bypassed with a fallback.

[skill-practices]: https://agentskills.io/skill-creation/best-practices
[skills-ref]: https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref
[eval-outputs]: https://agentskills.io/skill-creation/evaluating-skills
[eval-descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
