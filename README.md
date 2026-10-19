# sonsu-marketplace

Personal plugin marketplace for [omp](https://github.com/can1357/oh-my-pi).

omp reads the catalog at `.omp-plugin/marketplace.json` and installs plugins
from the `plugins/` directory.

## Table of Contents

- [Install](#install)
  - [Dependencies](#dependencies)
  - [Marketplace](#marketplace)
- [Usage](#usage)
  - [CLI](#cli)
- [Available plugins](#available-plugins)
  - [git-workflow](#git-workflow)
  - [skill-workflow](#skill-workflow)
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

Install [omp](https://github.com/can1357/oh-my-pi#install) before using this
marketplace.

The `git-workflow` skills reuse the target repository's validation setup first.
When none exists, the commit fallback needs Node.js 22.12.0 or newer and npm
(`npx`), while the branch fallback needs uv (`uvx`) and Python 3.10 or newer.
The first uncached fallback run needs access to its package registry.

Publishing pull requests needs an authenticated GitHub tool. Native media
uploads use GitHub CLI's `--attach` support and require push access to the target
repository. Capturing UI evidence needs suitable capture and annotation tools.

### Marketplace

Add the marketplace:

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

List its plugins and install one:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

Add `--scope project` to install a plugin for the current project only.

## Usage

### CLI

Check which skills are available after installation:

```sh
omp skill list
```

In an omp session, `/marketplace` opens the catalog in the plugin browser.
Installed skills provide guidance for relevant requests; for example, ask omp to
name a branch or write a commit message when using `git-workflow`.
Ask to draft, create, or update a pull request to use `writing-pull-requests`.
New PRs are Draft by default.
Ask to create, revise, or simplify an agent skill to use `authoring-skills`
from `skill-workflow`.

Fetch catalog changes, then upgrade installed plugins:

```sh
omp plugin marketplace update sonsu-marketplace
omp plugin upgrade
```

## Available plugins

### git-workflow

Install with `omp plugin install git-workflow@sonsu-marketplace`.

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

Install with `omp plugin install skill-workflow@sonsu-marketplace`.

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

## Layout

```text
.omp-plugin/
  marketplace.json            # catalog: name, owner, plugins[]
plugins/
  <name>/
    plugin.json               # Agent Plugins manifest (required)
    skills/<skill>/SKILL.md   # Agent Plugins: skills
    mcp.json                  # Agent Plugins: MCP servers
    commands/<command>.md     # omp: slash commands, run as /<name>:<command>
    agents/<agent>.md         # omp: task subagents
    rules/<rule>.md           # omp: rules
    package.json              # omp: extension modules under "omp.extensions"
```

Each plugin is an [Agent Plugins](https://agent-plugins.org/) 1.0.0 package.
Skills and MCP servers follow the standard. omp-specific components sit next to
them in omp's conventional locations, and omp loads both from the same plugin.
omp does not read the standard's `extensions` field or namespaced extension
directories yet, so omp-specific components use these locations for now.
Everything except `plugin.json` is optional. The reasons for this format are in
[docs/decisions/0002-plugin-format.md](docs/decisions/0002-plugin-format.md).

## Contributing

Pull requests are welcome. Ask questions or report problems in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow the
[PR writing procedure](plugins/git-workflow/skills/writing-pull-requests/SKILL.md)
when preparing a PR. For plugin changes, follow the authoring and testing
procedures below.

### Code review

Codex review guidance lives in
[Code Review Rules](AGENTS.md#code-review-rules). Apply it when reviewing PRs
and interpreting feedback; it guides judgment rather than replacing tests,
required approvals, or branch protections.

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
  information, and exercise changed CLI examples. Use a temporary `HOME` for
  omp commands and follow the plugin test procedure for plugin changes.

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

Use [MADR](docs/decisions/0001-use-madr-for-decision-records.md) to explain
significant choices: the problem, considered alternatives, chosen approach,
and consequences. An ADR is not a chronological work log or a command reference.
One record should cover one coherent decision, including closely related
design choices.

Store records as `docs/decisions/NNNN-title-with-dashes.md`, numbered in sequence.
Start from the
[MADR 4.0.0 template](https://github.com/adr/madr/blob/4.0.0/template/adr-template.md)
with `status` and `date` in YAML front matter and the sections `Context and
Problem Statement`, `Considered Options`, and `Decision Outcome`.

- Keep a record `proposed` while it is under review. Revise and consolidate the
  same proposal within its PR instead of creating a supersession chain.
- Mark it `accepted` only after decision review. After acceptance, edit only
  errors or status; a changed decision needs a new record that supersedes it.
- Routine implementation changes, command updates, and version bumps belong in
  the relevant operational documents, not new ADRs.

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

### Adding a plugin

1. Create `plugins/<name>/plugin.json`:

   ```json
   {
     "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
     "name": "<name>"
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

   Do not add `.mcp.json` or `.claude-plugin/plugin.json`. omp loads the skills
   and MCP servers of a standard plugin only from `skills/` and `mcp.json`.

3. Add omp-specific components:
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

4. Register the plugin in `.omp-plugin/marketplace.json`:

   ```json
   {
     "name": "<name>",
     "source": "./plugins/<name>",
     "description": "What the plugin does.",
     "version": "0.1.0"
   }
   ```

   Raise `version` with every change. `omp plugin upgrade` only reinstalls
   plugins whose catalog version changed.

Use the same name in `plugin.json`, the catalog entry, and the directory. It
must be lowercase ASCII letters, digits, `-`, and `.`, start and end with a
letter or digit, contain no `--` or `..`, and be at most 64 characters.

If a plugin needs something neither the standard nor these locations provide,
such as a remote MCP server that sends a credential header, leave out
`plugin.json` for that plugin and say why in the plugin's README. omp then loads
it with its own conventions (`.mcp.json`, omp skill frontmatter) instead of the
standard.

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

omp reports skipped skills and rejected plugins only in `omp skill list`, so
install into a temporary home and check its output before pushing:

```sh
(
  export HOME="$(mktemp -d)"
  omp plugin marketplace add ./
  omp plugin install <name>@sonsu-marketplace
  omp skill list
)
```

Every skill should appear, with no `warning:` lines.

Format and discovery checks do not prove correct activation or useful output.
For instruction changes, exercise representative tasks and boundary cases in
isolated repositories without publishing fixtures to a real project. Inspect
the actions as well as the final output. Use the
[evaluation guidance](plugins/skill-workflow/skills/authoring-skills/references/evaluation.md)
for before/after or with/without comparisons; report smoke checks separately
from measured trigger rates or comparative quality results.

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
