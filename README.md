# sonsu-marketplace

Personal plugin marketplace for omp and Codex.

[omp](https://github.com/can1357/oh-my-pi) reads `.omp-plugin/marketplace.json`;
[Codex](https://developers.openai.com/codex/cli) reads
`.agents/plugins/marketplace.json`. Both install the same `plugins/` packages.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
  - [Marketplace](#marketplace)
- [Usage](#usage)
  - [CLI](#cli)
- [Available plugins](#available-plugins)
  - [git-workflow](#git-workflow)
  - [skill-workflow](#skill-workflow)
  - [ticket-workflow](#ticket-workflow)
  - [decision-workflow](#decision-workflow)
  - [writing-workflow](#writing-workflow)
  - [review-workflow](#review-workflow)
- [Layout](#layout)
- [Contributing](#contributing)
  - [Code review](#code-review)
  - [Writing documentation](#writing-documentation)
  - [Decision records](#decision-records)
  - [Adding a plugin](#adding-a-plugin)
  - [Testing a plugin](#testing-a-plugin)
- [License](#license)

## Install

### Dependencies

Install [omp](https://github.com/can1357/oh-my-pi#install) or
[Codex CLI](https://developers.openai.com/codex/cli) before using this marketplace.
Codex must provide the plugin marketplace and subagent interfaces described
below; older clients without them do not meet the prerequisites.
Local catalog installation and installed-skill discovery were checked with
Codex CLI `0.163.0` and omp `18.12.3`. These are checked baselines, not promises
for every older release or evidence of authenticated model execution.

The `git-workflow` skills reuse the target repository's validation setup first.
When none exists, the commit fallback needs Node.js 22.12.0 or newer and npm
(`npx`), while the branch fallback needs uv (`uvx`) and Python 3.10 or newer.
The first uncached fallback run needs access to its package registry.

Publishing pull requests needs an authenticated GitHub tool. Native media
uploads use GitHub CLI's `--attach` support and require push access to the target
repository. Capturing UI evidence needs suitable capture and annotation tools.

Publishing tickets needs authenticated tooling for the selected GitHub repository
or Linear workspace. `ticket-workflow` does not bundle credentials or configure
tracker integrations.

The `writing-workflow` plugin includes Python-based Korean and Japanese checks.
See its [dependencies and source notices](plugins/writing-workflow/README.md)
before use. Its English skill has no external runtime dependency.

### Marketplace

For omp, add the marketplace:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

List its plugins and install one:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

Add `--scope project` to install a plugin for the current project only.

For Codex:

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace
codex plugin list --marketplace sonsu-marketplace --available --json
codex plugin add git-workflow@sonsu-marketplace
```

Use `codex plugin add <name>@sonsu-marketplace` for another package. This is a
repository marketplace, not a submission to the public plugin directory.
The common local marketplace format also applies to supporting app and IDE
surfaces; their availability varies, and CLI checks do not verify those UIs.

## Usage

### CLI

In omp, check available skills after installation:

```sh
omp skill list
```

In Codex, check catalog and installed state:

```sh
codex plugin list --marketplace sonsu-marketplace --json
```

Listing proves catalog or installation state, not skill execution. In a Codex
session, `$skill-name` explicitly selects a skill, for example
`$writing-commits`. Natural-language selection is model behavior, not an
installation hook or guaranteed trigger.
Codex discovery qualifies plugin skills as `<plugin>:<skill>`, for example
`git-workflow:writing-commits`; retain that identity when matching discovery
results or selecting among same-named skills.

In an omp session, `/marketplace` opens the catalog in the plugin browser.
Installed skills provide guidance for relevant requests; for example, ask omp to
name a branch or write a commit message when using `git-workflow`.
Ask to draft, create, or update a pull request to use `writing-pull-requests`.
New PRs are Draft by default.
Ask to create, revise, or simplify an agent skill to use `authoring-skills`
from `skill-workflow`.
Ask to draft, create, update, or split GitHub Issues or Linear tickets to use
`writing-tickets` from `ticket-workflow`. Draft requests do not publish issues.
Ask whether a design choice warrants an ADR, or ask to draft, review, or
supersede one, to use `writing-adrs` from `decision-workflow`. It does not
create a decision record for every implementation change.

Ask to write or refine Korean, English, or Japanese prose to use
`writing-workflow`. Korean technical documentation is included; protected code,
identifiers, quotations, numbers, and terminology remain unchanged.

Ask to review code, a diff, a branch, or a PR to use `reviewing-code` from
`review-workflow`. omp pairs a native reviewer with focused custom workers;
Codex uses independent custom general and focused subagents. Explicit
native-only requests retain `/review` or `codex review` without orchestration.
Reviews stay local unless you request publication; a comment draft is not posted.

For omp, fetch catalog changes, then upgrade installed plugins:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

For Codex, refresh a Git-backed marketplace:

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

An absolute local marketplace path is used directly and cannot be refreshed
with `marketplace upgrade`; that command requires a configured Git source.

## Available plugins

### git-workflow

Install with `omp plugin install git-workflow@sonsu-marketplace` or
`codex plugin add git-workflow@sonsu-marketplace`.

- **`writing-commits`** writes Conventional Commit messages and validates them
  before use. It reuses repository commands, tools, versions, and configuration.
  Only without an existing execution setup does it run pinned commitlint through
  `npx`; only without configuration does it use bundled ESM defaults. See the
  [skill's validation procedure](plugins/git-workflow/skills/writing-commits/SKILL.md#required-validation).
- **`naming-branches`** names and validates branches with Conventional Branch
  1.1.0, reusing repository validation first. Without an execution setup it runs
  pinned `commit-check` through `uvx`; repository configuration still takes
  precedence over bundled defaults. This is a Python CLI, not an npm package.
  The skill's default prefixes are `feature/` (not `feat/`), `fix/` (not
  `bugfix/`), `hotfix/`, `release/`, and `chore/`. See the
  [skill's validation procedure](plugins/git-workflow/skills/naming-branches/SKILL.md#required-validation).
- **`writing-pull-requests`** writes repository-aware PR titles and descriptions,
  records author checks, labels AI assistance, and prepares UI review evidence.
  New PRs are Draft by default. See the
  [PR writing procedure](plugins/git-workflow/skills/writing-pull-requests/SKILL.md).

Branch prefixes do not change commit types: a `feature/` branch can contain
`feat`, `fix`, and other commits. A missing dependency or failed configured
validator is not an absent setup and must not trigger a fallback. These skills
provide agent workflow instructions, not Git hooks or CI enforcement.

### skill-workflow

Install with `omp plugin install skill-workflow@sonsu-marketplace` or
`codex plugin add skill-workflow@sonsu-marketplace`.

- **`authoring-skills`** creates, revises, and reviews focused agent skills
  using common Agent Skills principles, without a default client. It identifies
  the intended consumer from the request and project context, then loads only
  the relevant omp, Claude, or Codex considerations. It keeps judgment in the
  skill, delegates mechanical work to existing tools, and loads evaluation
  guidance when choosing checks. See the
  [skill-authoring procedure](plugins/skill-workflow/skills/authoring-skills/SKILL.md).

This plugin does not install skills, configure projects, or provide an
evaluation runner. Plugin packaging and marketplace checks remain in the
contributor procedures below.

### ticket-workflow

Install with `omp plugin install ticket-workflow@sonsu-marketplace` or
`codex plugin add ticket-workflow@sonsu-marketplace`.

- **`writing-tickets`** writes small, outcome-centered GitHub and Linear tickets.
  It follows applicable project templates first, using a bundled Problem,
  Desired outcome, and optional Context body when no template applies.
  Outcomes make completion judgeable without prescribing the implementation
  or requiring a separate acceptance checklist. It also reviews labels,
  assignment, priority, estimates, and milestones, proposing grounded metadata
  separately from the body using the tracker's actual fields and conventions.
  Optional unknowns remain unset rather than guessed. See the
  [ticket-writing procedure](plugins/ticket-workflow/skills/writing-tickets/SKILL.md)
  and [fallback template](plugins/ticket-workflow/skills/writing-tickets/assets/ticket-body.md).

Use ticket, then work, then PR as the normal development flow. Tickets and PRs
need not be one-to-one; partial work should not close the whole ticket.
Install `git-workflow` for downstream branch naming and PR preparation; it is not
needed to draft tickets. The ticket plugin respects existing tracker sync and
templates but does not configure them, publish duplicate issues to both trackers,
or enforce ticket-first work through hooks.

### decision-workflow

Install with `omp plugin install decision-workflow@sonsu-marketplace` or
`codex plugin add decision-workflow@sonsu-marketplace`.

- **`writing-adrs`** selects decisions worth recording and writes short ADRs
  with context, a decision and its rationale, rejected alternatives, and
  consequences. It follows the target project's scope, template, and lifecycle
  first; without those, it uses direction-setting and consequential design
  choices as its boundary. See the
  [ADR writing procedure](plugins/decision-workflow/skills/writing-adrs/SKILL.md)
  and [default template](plugins/decision-workflow/skills/writing-adrs/assets/adr.md).

The principles follow Martin Fowler's ADR guidance, and the default template
is adapted from Evolu. Drafts remain proposed until the decision-maker accepts
them; changing an accepted decision requires a linked replacement. This plugin
does not install hooks, impose a format on existing repositories, or turn
routine work into ADRs.

### writing-workflow

Install with `omp plugin install writing-workflow@sonsu-marketplace` or
`codex plugin add writing-workflow@sonsu-marketplace`.

- **`humanize-korean`** adapts `epoko77-ai/im-not-ai` for natural Korean
  editing across genres, including technical documentation, README files,
  API references, runbooks, and prose around code. For new writing, compose a
  draft from the supplied material first, then refine it with the skill.
- **`ce-noslop`** adapts Every's English writing, editing, and diagnostic
  guidance for clear prose, preserving facts and the requested register.
- **`natural-japanese`** adapts coji's Japanese drafting, editing, and
  diagnostic workflow, including document-specific guidance and author voice.

Use one editorial skill for the language being written; do not run competing
humanizers over the same text. These are writing workflows, not translation
services or reliable AI-authorship detectors. Read the
[plugin guide](plugins/writing-workflow/README.md) for examples, dependencies,
upstream revisions, and licenses. Mechanical checks do not establish naturalness
or complete semantic preservation.

### review-workflow

Install with `omp plugin install review-workflow@sonsu-marketplace` or
`codex plugin add review-workflow@sonsu-marketplace`.

Evidence-driven code review with independent general and focused reviewers and
local-first reporting.

- **`reviewing-code`** reviews intent, flow, failures, architecture, and internal
  implementation. omp uses a native `reviewer` plus `review-workflow-focused`;
  Codex uses fresh generic subagents assigned general and focused roles. They
  inspect the same frozen target independently, without sharing initial
  conclusions. Models follow effective client settings, not a fixed provider
  pair. Runtime verification and high-risk red-team challenges are separate,
  bounded work rather than repeated full reviews.
- Reviews report locally by default. Comment drafting and explicit publication
  use [review-comment guidance](plugins/review-workflow/skills/reviewing-code/references/review-comments.md)
  that preserves evidence, uncertainty, and the difference between fixes and
  optional suggestions.

Read the [plugin guide](plugins/review-workflow/README.md) for model access,
workspace isolation, runtime verification, and cost boundaries. The plugin does
not install hooks, automatically fix code, or configure credentials.

## Layout

```text
.omp-plugin/
  marketplace.json            # catalog: name, owner, plugins[]
.agents/plugins/
  marketplace.json            # Codex catalog: same package roots
plugins/
  <name>/
    plugin.json               # shared identity, version, standard metadata
    skills/<skill>/SKILL.md   # Agent Plugins: skills
    mcp.json                  # Agent Plugins: MCP servers
    commands/<command>.md     # omp: slash commands, run as /<name>:<command>
    agents/<agent>.md         # omp: task subagents
    rules/<rule>.md           # omp: rules
    package.json              # omp: extension modules under "omp.extensions"
```

Each plugin is an [Agent Plugins](https://agent-plugins.org/) 1.0.0 package.
Both catalogs point to the same `plugins/<name>` directories, relative to the
repository root. Standard metadata, skills, scripts, and assets are shared;
omp agents and client-specific execution references remain separate.
omp-specific components use omp's conventional locations because omp does not
yet read the standard's `extensions` field or namespaced extension directories.
Everything except `plugin.json` is optional. Do not duplicate package trees,
add `.codex-plugin` overlays, symlinks, or empty MCP files for these packages.
The packaging rationale remains [ADR-0002](docs/decisions/0002-plugin-format.md);
the proposed cross-client design is
[ADR-0005](docs/decisions/0005-share-plugins-across-clients.md).

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow the
[PR writing procedure](plugins/git-workflow/skills/writing-pull-requests/SKILL.md)
when preparing a PR. For plugin changes, follow the authoring and testing
procedures below.

### Code review

Apply [Code Review Rules](AGENTS.md#code-review-rules) when reviewing changes
and interpreting feedback. Requested plugin reviews use the
[reviewing-code procedure](plugins/review-workflow/skills/reviewing-code/SKILL.md)
and the matching [omp execution reference](plugins/review-workflow/skills/reviewing-code/references/omp.md)
or [Codex execution reference](plugins/review-workflow/skills/reviewing-code/references/codex.md).
omp dispatches native and focused reviewers; Codex dispatches independent
custom general and focused reviewers. Explicit native-only requests retain
`/review` or `codex review`, without plugin orchestration. Preserve native
output and priority contracts only when using a native reviewer; custom
controllers use the common skill's report contract. Results stay local unless
publication is explicitly requested; a draft is not permission to post.
These procedures do not replace required approvals or branch protections.

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

### Writing documentation

Write documentation in English and follow the
[Standard Readme specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
when creating or updating README files, as recorded in
[ADR-0003](docs/decisions/0003-use-standard-readme.md).

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
- Put marketplace-specific sections after `Usage`, and authoring and testing
  procedures under `Contributing`. State where to ask questions and whether
  pull requests are accepted.
- Omit optional sections that add no value. Keep decision rationale in ADRs.
- Inspect rendered navigation and code blocks, check links and license
  information, and exercise changed CLI examples. Use isolated client homes
  and follow the plugin test procedure below, including Codex's `CODEX_HOME`.

All Markdown documents follow the lint policy in
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
step, not automatic formatting or CI integration.

### Decision records

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
  and review procedures belong in code, configuration, README, or skills.
  Record one only if it actually changes the direction or design constraints
  above, not merely because it is a shared rule.
- An ADR explains a decision, not implementation steps, a work log, or a
  command reference. Search existing records before starting another.

Store records as `docs/decisions/NNNN-title-with-dashes.md`, numbered in sequence.
Use a title stating the decision, `Date` and `Status` metadata, and the template's
`Context`, `Decision`, `Rejected alternatives`, and `Consequences` sections.
State the choice and why in a few sentences; describe real alternatives rather
than inventing options to fill the template. Aim for one page and link supporting
evidence instead of duplicating it. Record uncertainty or revisit conditions
when they matter.

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

Keep responsibilities separate so readers need not reconstruct current rules
from decision history:

| Document | Responsibility |
| --- | --- |
| `AGENTS.md` | Agent obligations and links to current contributor procedures |
| README and skills | Current setup, workflow, precedence, and manual checks |
| Configuration files | Executable rules and values |
| ADRs | Rationale, alternatives, tradeoffs, and links to current instructions |

When adding or changing a requirement, update its operational source and ensure
`AGENTS.md` identifies when it applies and which procedure to follow. Add or
adjust that routing in the same change if needed. Do not leave an active
requirement only in an ADR. ADRs should link to current instructions rather
than duplicate commands or rule values. Git and PR history retain intermediate
revisions.

[adr-fowler]: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[adr-skill]: plugins/decision-workflow/skills/writing-adrs/SKILL.md
[adr-template]: plugins/decision-workflow/skills/writing-adrs/assets/adr.md
[adr-evolu-template]: https://github.com/evoluhq/evolu/blob/bb2644275dd99ff6dce4744db578967699045ea3/docs/adr/template.md

### Adding a plugin

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
     the source for this marketplace's validation commands.

   - **MCP servers**: `mcp.json` with the
     `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json` `$schema` and an
     `mcpServers` object. Each server sets `type` (`stdio`, `streamable-http`,
     or `sse`). A `stdio` `command` is a bare executable name or a `./` path.
     Use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in `args`, `env`, and `cwd`; omp
     expands nothing else. Keep secrets out of `mcp.json`. A `stdio` server
     receives omp's environment and can read credentials from it.

   Keep one standard package root for both clients; do not add `.mcp.json`,
   `.claude-plugin/plugin.json`, or `.codex-plugin/plugin.json` overlays.
   Shared skills and MCP servers live in `skills/` and `mcp.json`.

3. Add omp-specific components only when needed:
   - **Commands**: `commands/<command>.md` with a `description`. Use a command
     for a workflow that runs only when the user asks for it, since a standard
     skill cannot set `hide`.

   - **Agents**: `agents/<agent>.md` with `name` and `description`.

   - **Rules**: `rules/<rule>.md` with a `description`. Use a rule for guidance
     tied to file patterns (`globs`) or that always applies (`alwaysApply`),
     since a standard skill cannot set these fields.

   - **Code** (tools, event handlers, commands with logic): extension modules
     listed in `package.json` under `omp.extensions`. See
     [Extensions](https://github.com/can1357/oh-my-pi/blob/main/docs/extensions.md).

   Keep client execution differences in conditional skill references.
   Do not copy omp agents into Codex host configuration.

   When adding another client, retain one source package per plugin and share
   common workflow requirements, scripts, and assets. Separate only necessary
   client metadata, components, and execution procedures. Use supported client
   capabilities; disclose unavailable requirements rather than silently weaken
   the workflow. A different model alone does not require a package fork.
   Document the new client's actual support scope and verify its installation,
   discovery, and representative execution before claiming compatibility;
   the current omp and Codex checks do not establish support for other clients.

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

   Both paths are relative to the repository root, not the catalog directory.
   Keep catalog names, order, and package sets aligned. The explicit Codex
   policy follows its catalog format; these skill-only packages add neither
   authentication dependencies nor automatic installation.

   Raise `version` in the root manifest and omp catalog together on every
   plugin change. `omp plugin upgrade` only reinstalls changed catalog versions.
   Codex uses package metadata; do not duplicate versions, omp `owner`, or
   marketplace `metadata` in its catalog.

Use the same name in `plugin.json`, both catalog entries, and the directory. It
must be lowercase ASCII letters, digits, `-`, and `.`, start and end with a
letter or digit, contain no `--` or `..`, and be at most 64 characters.

If a future plugin needs a capability the standard cannot express, document
the client limitation before changing packaging or claiming shared support.
An unsupported client release is a prerequisite failure, not permission to
silently switch these shared packages to a legacy format.

### Testing a plugin

For skill changes, check the format with the official reference validator.
This authoring check needs uv, Python 3.11 or newer, and network access on the
first run. Pin the reference source independently of plugin runtime tools:

```sh
skills_ref_repo=https://github.com/agentskills/agentskills.git
skills_ref_rev=69ef37e9424c0a7ea9dd2293b559e43ec8176379
skills_ref="git+$skills_ref_repo@$skills_ref_rev#subdirectory=skills-ref"
for skill in plugins/*/skills/*; do
  uvx --from "$skills_ref" skills-ref validate "$skill"
done
```

The [reference validator][skills-ref] checks frontmatter and naming, not task
quality. It is an authoring aid, not a production dependency. The loop covers
all plugins; select individual skill directories for a focused check.

Use independent temporary homes outside the checkout. Do not install test
plugins into live clients or copy real settings or credentials into the test
environment. Begin at the marketplace root:

```sh
REPO="$PWD"
TMP="$(mktemp -d)"
OMP_HOME="$TMP/omp-home"
CX_HOME="$TMP/codex-home"
CX_CODEX_HOME="$CX_HOME/.codex"
TARGET="$TMP/target"
mkdir -p "$OMP_HOME" "$CX_CODEX_HOME" "$TARGET"
```

omp reports skipped skills and rejected plugins in `omp skill list`:

```sh
HOME="$OMP_HOME" omp plugin marketplace add "$REPO"
for name in git-workflow skill-workflow ticket-workflow decision-workflow \
  writing-workflow review-workflow; do
  HOME="$OMP_HOME" omp plugin install "$name@sonsu-marketplace"
done
HOME="$OMP_HOME" omp skill list
```

For Codex, run from the separate target directory, not the marketplace source.
Apply both temporary environment variables to every invocation:

```sh
(
  cd "$TARGET"
  export HOME="$CX_HOME" CODEX_HOME="$CX_CODEX_HOME"
  codex plugin marketplace add "$REPO" --json
  codex plugin list --marketplace sonsu-marketplace --available --json
  for name in git-workflow skill-workflow ticket-workflow decision-workflow \
    writing-workflow review-workflow; do
    codex plugin add "$name@sonsu-marketplace" --json
  done
  codex plugin list --marketplace sonsu-marketplace --json
)
```

Require all six entries to parse and all six packages to install and enable.
Do not hide catalog errors or count skipped entries as success. Check actual
Codex skill discovery through a fresh `codex app-server` stdio subprocess in
the same isolated environment. Following the
[initialization and skills API](https://learn.chatgpt.com/docs/app-server),
send `initialize`, wait for its response, send `initialized`, then `skills/list`:

```json
{"id":1,"method":"initialize","params":{"clientInfo":{"name":"sonsu_marketplace_smoke","version":"0.1.0"}}}
{"method":"initialized","params":{}}
{"id":2,"method":"skills/list","params":{"cwds":["<absolute disposable target>"],"forceReload":true}}
```

Inspect `result.data[].errors`, each skill's `enabled`, name, and actual path.
Paths must resolve to installed packages, not direct source discovery; do not
use extra user roots to bypass installation. Terminate the owned subprocess.
Use a throwaway driver, not a new repository framework.

In each client, require these ten skills exactly once (unrelated built-ins
are allowed), without omp `warning:` lines or Codex loading errors:
Codex reports `<plugin>:<skill>` names; match the plugin ID and skill suffix
against this table without renaming the shared skill or counting built-ins.

| Plugin | Expected skills |
| --- | --- |
| git-workflow | naming-branches, writing-commits, writing-pull-requests |
| skill-workflow | authoring-skills |
| ticket-workflow | writing-tickets |
| decision-workflow | writing-adrs |
| writing-workflow | humanize-korean, ce-noslop, natural-japanese |
| review-workflow | reviewing-code |

Also compare both catalogs' package names, source paths and existence, and
root-manifest/omp-catalog versions with a throwaway check.

Format and discovery checks do not prove correct activation or useful output.
For instruction changes, exercise representative tasks and boundary cases in
isolated repositories without publishing fixtures to a real project. Inspect
the actions as well as the final output. Use the
[evaluation guidance](plugins/skill-workflow/skills/authoring-skills/references/evaluation.md)
for before/after or with/without comparisons; report smoke checks separately
from measured trigger rates or comparative quality results.

Model runs require separately authorized authentication in the temporary
environment. Do not implicitly reuse live credentials. For Codex model smoke
runs, use `--no-daemon` to avoid attaching to the live client daemon:

```sh
HOME="$CX_HOME" CODEX_HOME="$CX_CODEX_HOME" \
  codex --no-daemon exec --json --sandbox workspace-write \
  --add-dir "$TMP" -C "$TARGET" '$reviewing-code Review working changes locally.'
```

Use remote-free disposable Git targets with normal behavior and a known
regression spanning staged, unstaged, and untracked changes. Observe independent
general/focused workers on the same frozen target, full completion results,
deduplicated findings, and controller-only runtime checks in another disposable
copy. Confirm original source, index, and untracked content remain unchanged.
omp must retain native `reviewer` plus `review-workflow-focused`; Codex must
not call native review or a recursive CLI. Check a clean baseline, implicit
skill selection, explicit native-only review, comment-only drafting, and
unavailable subagents (`-c agents.enabled=false` in Codex). Missing or failed
workers must remain incomplete, not a sequential or native-only fallback.

Exercise writing helpers from discovered installed paths in both clients,
preserving identifiers, numbers, URLs, and fenced code. Verify commit and branch
candidates with installed validators without committing or creating branches;
draft PRs and tickets without publication; reject an unnecessary ADR; design a
Codex skill without loading omp authoring guidance; preserve dates and promises
in an English edit. In a separate disposable installation, remove one helper
and verify an explicit missing-resource result, not a guessed cache path or
false pass. Do not change the successful installation or source helpers.

Report actual CLI versions, discovery, execution traces, runtime evidence,
and precise blockers separately. Without authorized model access, complete
non-model checks but mark all unexecuted model scenarios unverified. Installation
does not prove review quality, automatic selection, or app/IDE behavior.

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

## License

[MIT](LICENSE) © sonsu-lee

[skill-practices]: https://agentskills.io/skill-creation/best-practices
[skills-ref]: https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref
