# design-workflow

Design and review interfaces and graphics with scoped evidence and an optional
omp verification harness.

## Table of contents

- [Install](#install)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [Portable skills](#portable-skills)
  - [Related skills](#related-skills)
  - [Start an omp strict run](#start-an-omp-strict-run)
  - [Report and finish](#report-and-finish)
  - [Stop or change scope](#stop-or-change-scope)
- [Evidence and trust boundaries](#evidence-and-trust-boundaries)
- [Research scope](#research-scope)
- [Contributing](#contributing)
  - [Verification](#verification)
- [License](#license)

## Install

Register this marketplace using the
[marketplace instructions](../../README.md#install), then install the same
package in the chosen client:

```sh
omp plugin install design-workflow@sonsu-marketplace
codex plugin add design-workflow@sonsu-marketplace
claude plugin install design-workflow@sonsu-marketplace
```

### Dependencies

The portable skills need no runtime extension. The optional omp harness requires
omp 18.12.6 or newer, Bun 1.4.3 or newer, and an installed Chrome or Chromium.
Set `DESIGN_WORKFLOW_CHROME` to its executable when automatic discovery does not
find it. Captures use a fresh browser profile, not your logged-in browser.
Strict command checks require a POSIX platform; Windows checks are unsupported.
`/design-report` also runs the `omp` command on `PATH` with your existing omp
login and the session's model and thinking level, so each attempt makes two
model calls: one to write the report and one to review it.

The package pins its browser transport and axe-core in `package.json` and
`bun.lock`. For explicit dependency setup, inspect `omp plugin list --json`,
enter the `design-workflow` entry's `installPath`, and run:

```sh
bun install --production --frozen-lockfile
```

Restart omp after setup. Missing browser/dependency access is a blocker, not
permission to manufacture a screenshot or silently substitute another adapter.
This package does not install a browser, configure credentials, or alter a
project's hooks. Codex and Claude Code do not run the omp extension.

## Usage

### Portable skills

- `designing-interfaces`: create or improve a digital interface, including a
  proposal that does not edit files.
- `reviewing-designs`: evaluate an existing design and report evidence-bound
  issues without changing the artifact.
- `designing-graphics`: create or refine standalone icons, illustration and
  identity assets, including their reproduction and handoff constraints.

For example:

```text
Propose a responsive checkout layout without removing payment or error states.
Review the supplied checkout screenshots without editing anything.
Design an icon family that stays legible in small monochrome reproduction.
```

Each skill keeps its conditional research inside its own directory, so an
isolated skill revision retains its support files. These are judgment guides on
all three clients, not a quality guarantee or a permission boundary.

### Related skills

These skills cover what this plugin deliberately leaves out. Install them
separately if you need them:

- Vercel's
  [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines)
  checks UI code against concrete accessibility, form and interaction rules.
- Emil Kowalski's [skills](https://github.com/emilkowalski/skills) give
  opinionated motion and component values that these skills do not prescribe.
- Anthropic's
  [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
  explores a distinctive visual direction for a new interface without an
  existing design system.

### Start an omp strict run

Strict execution gating is dormant until the operator invokes a command and
confirms its exact plan. The five controlled tools remain directly advertised,
but cannot perform scoped work without that approval. The extension never
changes the client's existing tool selection or top-level/`xd://` presentation.
Stop existing foreground and background work first. Save a JSON plan outside the
editable scope, for example `design-plan.json`:

```json
{
  "mode": "design",
  "paths": ["page.html"],
  "goal": "Make the primary action visible at the target size",
  "brief": "The checkout button is hidden below the fold on phones. Fix it.",
  "facts": [
    {
      "subject": "Checkout page",
      "approval": "not-supplied",
      "availability": "inspectable"
    }
  ],
  "captures": [
    {
      "id": "narrow",
      "kind": "file",
      "target": "page.html",
      "width": 390,
      "height": 844,
      "steps": [{ "action": "assert-visible", "selector": "button" }]
    }
  ],
  "checks": []
}
```

```text
/design-start design-plan.json
/design-status
```

Review the displayed workspace, paths, targets, scenarios and commands before
confirming. Headless sessions cannot approve a plan. A model-written approval
field has no authority. Scope cannot be extended by a tool call: stop and start
a newly approved plan instead.

`brief` is the original request. `facts` lists project facts you confirm: for
each `subject`, `approval` is `approved`, `rejected`, `pending` or
`not-supplied`, and `availability` is `inspectable` (supplied in this run),
`exists-not-supplied`, `does-not-exist` or `unknown`. Record only what you know;
a model's guess does not belong here. The final report's fact table comes from
these fields, and its prose is checked against them.

A `design`, `graphics` or `review` plan requires at least one capture, with each
viewport dimension between 1 and 4096 pixels. Command checks are optional. An
`advisory` plan is for advice without artifact work: it declares no captures or
checks, may read approved paths but not write them, and ends as `advised`,
never `completed`.

`paths` contains exact workspace-relative files, existing or new, not directory
or glob grants. File captures support HTML/SVG; include every local CSS, script,
image and font resource they load in `paths`. Unapproved or failed assets reject
the capture. Web captures accept an exact loopback HTTP(S) origin and may use
`paths: []` for an observation-only target. Remote sites and native Figma/editor
capture or writes are not supported by strict mode.
Provide an already-running disposable server outside the agent's job queue for
web targets; this extension does not manage server lifecycle.

Capture steps are declarative `click`, `fill`, `press`, `assert-visible`,
`assert-text`, `assert-accessible` or `assert-no-overflow` operations. Each has
a `selector`; `fill` also has `value`, `press` has `key`, and `assert-text` has
`text`. `assert-accessible` runs [axe-core](https://github.com/dequelabs/axe-core)
on the selected element and fails on any violation it detects; automated rules
find only part of the accessibility problems, so a pass is not conformance.
`assert-no-overflow` fails when text inside the selection extends horizontally
past the selection or past an ancestor that clips it. Text inside scrollable
containers, text truncated with an ellipsis that takes effect, and text hidden
with `clip` or `clip-path` (such as visually hidden labels) is not counted;
field values and non-text boxes are not measured. To test worst-case content,
point a `web` capture at a URL that serves that fixture. A `review` plan allows
assertions only, no writes and no command checks. `graphics` uses the same
controlled file path as `design`, typically an SVG target.

A check declares `id`, `command`, `args` and `timeoutMs`. It runs exactly that
executable and argv without a shell, with a bounded timeout and combined output
limit. Approving it authorizes real process access; it is not a read-only or
filesystem-sandboxed check. Use disposable workspaces and local servers.

### Report and finish

The agent uses `design_read`, `design_write`, `design_capture`, `design_check`
and `design_status`. Captures return actual PNG images and JSON receipts;
successful checks create receipts from real process results. When the evidence
is current, the agent stops and the extension asks you to continue:

```text
/design-report
/design-accept
```

`/design-report` writes the report body in an omp side turn that is neither
streamed nor added to the conversation, then sends it with the original
request and fact table to a fresh `omp -p` process with no tools, skills,
extensions or context files, using the session's model. A sentence asserting
an approval, sign-off requirement, artifact availability or check the facts do
not support rejects the report; the rejected sentences are shown and nothing is
recorded. Generate again or stop the run. A rejected or unreadable verdict never
falls back to publication.

`/design-accept` shows the evidence and the exact checked report. Inspect the
images, scenario results and artifact yourself before confirming. Confirmation
records your acceptance of those exact bytes, publishes them unchanged as the
official result and ends the run as `completed` (or `advised`). Any source,
evidence, fact or report change before acceptance invalidates the report.
Acceptance is your judgment, not an automated claim that the design meets every
quality requirement, and the fact review is a model judgment that can miss
errors.

When only the report and your review remain, the extension interrupts the
agent turn instead of asking the model to self-approve. If mechanical evidence
is missing, the stop hook refuses completion; a repeated unchanged refusal ends
the run as `blocked`, not success.

### Stop or change scope

```text
/design-stop Change the approved scope
/design-blocked Browser unavailable
/design-limited Native editor cannot be captured by this adapter
```

These are non-success exits. They cancel the active controlled operation,
including report generation, and release the execution gate without changing
the client's tool selection. The client's own interrupt does not cancel an
operator command such as `/design-report`; use `/design-stop`. Ordinary
operator interruption leaves the run active and does not mark it completed;
inspect status before continuing. The explicit commands above are terminal.
Start a new approved plan to resume a terminal run.

## Evidence and trust boundaries

- Source content and artifact hashes bind evidence and review to one revision.
  Changes invalidate evidence, including when a previously completed run is
  revalidated. Session restore reads the current branch only; another session
  cannot inherit approval. Unsafe restoration blocks controlled work until the
  operator stops it.
  Starting a capture/check retry removes its earlier receipt and acceptance
  before execution, including when the new attempt fails or is cancelled.
- Live loopback content is not continuously monitored. Its receipt describes the
  captured observation, not every subsequent server state. A source revision
  fingerprints only `paths`, not the server's live state or external
  dependencies. Include relevant local sources when that tracking is required;
  acceptance still cannot establish continuous server-state equivalence.
- During an active run, broad shell, Eval/browser bridges, arbitrary writes, MCP
  actions, unknown tools and subagent spawning are blocked. Native reads are
  limited to packaged skill references and this run's artifacts; source reads
  use `design_read`. Unrelated tools may remain advertised, but the execution
  hook rejects their calls while the gate is active; hiding schemas is not the
  permission boundary.
- Browser capture blocks cross-origin HTTP requests, mutation HTTP methods,
  HTTP redirects, unexpected navigation, downloads, popups and service workers.
  Use final direct resource URLs, including for same-origin assets. Same-origin
  GET requests and scripts may still have side effects: use disposable targets.
- This is an in-process cooperation boundary, not an OS sandbox. It does not
  isolate hostile extensions, concurrent external writers, manually executed
  operator commands or independently running processes. An approved check can
  modify files outside the plan. Do not grant one to untrusted code.
- The authoritative outcome is the published report and run state, not
  assistant prose. Only the report is fact-checked; the agent's ordinary
  messages, and any later paraphrase of the report, are not. A valid receipt
  proves the recorded operation and assertions, not usability, accessibility
  conformance, legal compliance or overall visual quality.

The
[proposed runtime-boundary decision](../../docs/decisions/0010-enforce-design-evidence-at-the-omp-runtime-boundary.md)
explains why portable skills and omp controls remain separate.
The guide describes the implementation; the architecture record remains
proposed until separately accepted by the decision-maker.

## Research scope

Most conditional references distill 48 contextual design observations and six
handoff workflows from the reviewed Madia material. Source links and time
intervals stay with each observation. They are not 48 universal rules or
independently measured user outcomes. The package includes no source videos,
captions, screenshots, private membership content or dependencies on the
author's local research paths. Photoshop retouching, equipment promotion and
career/business-only advice are outside these skills; mixed videos contribute
only relevant design reasoning. The worst-case data, touch web and motion
references are local adaptations of Emil Kowalski's
[skills](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9)
at `a81dbca07f2217b7103e510c0f13f8d5b017afc9`, not automatic mirrors. Keep the
upstream notice and revision reference when updating them.

## Contributing

Pull requests are welcome. Report issues in the
[marketplace issue tracker](https://github.com/sonsu-lee/sonsu-marketplace/issues).
Follow the [plugin procedure](../../README.md#adding-a-plugin), independent
skill review and [client verification](../../README.md#testing-a-plugin).

### Verification

From this package directory:

```sh
bun install --frozen-lockfile
bun run check
export DESIGN_WORKFLOW_CHROME=\
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
bun run test
```

Set the executable path for your platform. Without it, browser and SDK capture
regressions are explicitly skipped: that is not full verification. Tests
exercise real files, browser captures and commands. The SDK lifecycle tests use
the production `AgentSession`, tool wrappers and full-session fork, substituting
only operator UI choices and deterministic interruption timing. Inspect an
actual rendered capture separately; these tests do not prove visual quality.

Evaluate each skill with the repository's
[skill evaluation procedure](../../README.md#evaluating-skills), using the
cases in its `evals/` directory and `--baseline without`, since these skills
have no earlier version on `origin/main`. Review outputs as well as pass
rates. Model runs remain local, never in CI.

## License

[MIT](../../LICENSE) for marketplace content, copyright sonsu-lee. Upstream
portions retain their MIT notice, bundled with the
[interface](skills/designing-interfaces/LICENSE-emilkowalski-skills) and
[review](skills/reviewing-designs/LICENSE-emilkowalski-skills) skills.
