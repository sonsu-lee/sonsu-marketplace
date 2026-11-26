# development

Route development work, plan changes, investigate bugs, and author skills.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
  - [CLI](#cli)
  - [Codex user hook](#codex-user-hook)
  - [Local work events](#local-work-events)
  - [Declared verification](#declared-verification)
- [Contributing](#contributing)
- [License](#license)

## Install

Register the marketplace using the [root guide](../../README.md#install), then:

```sh
omp plugin install development@sonsu-marketplace
codex plugin add development@sonsu-marketplace
claude plugin install development@sonsu-marketplace
```

Install [review](../review/README.md) when independent code review is required.
A missing required review is incomplete, not a pass.

The hook scripts and declared-check runner require Python 3.9 or newer.

## Usage

### CLI

```sh
omp skill list
codex plugin list --marketplace sonsu-marketplace --json
claude plugin details development
```

Ask for a plan, implementation, bug investigation, domain interview, or skill
revision. In Codex explicitly select `$development:planning-work`; Claude Code
uses `/development:planning-work`. Skill discovery does not prove activation or
complete loading. Natural-language routing depends on the model.

The [request router](skills/working-on-tasks/SKILL.md) separates user intent
and authority. [Planning](skills/planning-work/SKILL.md),
[execution](skills/executing-work/SKILL.md),
[debugging](skills/debugging-code/SKILL.md), and
[skill authoring](skills/authoring-skills/SKILL.md) can also be used directly.
The [grill package](../grill/README.md) owns the three interview skills.
Development retains `domain-modeling` and `improving-codebase-architecture`.

Installed omp packages load the extension, which adds the router to main-session
prompts. On the checked omp CLI, `--plugin-dir` alone discovers skills but does
not load package extensions; for local testing also pass
`--extension /absolute/path/to/plugins/development/src/index.ts`.
Claude Code uses a SessionStart hook for startup, clear and compact. Codex
0.163.0 and 0.170.0 do not load hooks from this standard Agent Plugins manifest
([upstream issue](https://github.com/openai/codex/issues/47925)). The bundled
Codex hook configuration is therefore inactive on those versions even if trusted.
Hook context is guidance, not permission or a security boundary. An installed
hook does not establish automatic skill selection. Commit, publication, tracker
changes and deployment require their own authority.

The omp extension does not ask its own confirmation. Before recognized commit,
publication, deployment, destructive, remote mutation, and outside-workspace
file actions it runs the evidence gate and blocks the call when the gate reports
a block; otherwise the call continues under omp's own permission settings. If
the omp evidence gate cannot run or returns unreadable output, recognized
actions are blocked. Claude Code's PreToolUse hook asks for confirmation; its
non-interactive host may deny the call. The Claude guard hook is registered
with `onFailure: block`, so Claude Code blocks the call if the hook cannot run
or fails; its log hooks stay non-blocking. The separately registered Codex user
hook denies recognized actions because Codex does not support the PreToolUse
`ask` decision.

Shell and MCP name patterns are in `hooks/policy.json`; file-tool path rules
are in the extension and hooks. Shell indirection, unrecognized commands,
external processes, disabled hooks, and other host paths can bypass recognition.
The omp extension checks the paths in the tool call before the editor resolves
its final targets. Passing the gate does not guarantee that those targets are
identical.
MCP name matching can both block read-only tools and miss mutations.
In-workspace paths are not compared with a natural-language plan's narrower
file scope. Pattern matching also sees comments and quoted text, so harmless
commands may be asked about or denied. A Claude guard that is not loaded
cannot block a call.
This is not a security sandbox. Never infer approval from skill selection.

### Codex user hook

Codex 0.163.0 and 0.170.0 skip the packaged hook. To use it separately, first
set `DEVELOPMENT_PLUGIN_ROOT` to the absolute path of the installed or checked-out
`plugins/development` directory in the environment that launches Codex:

```sh
export DEVELOPMENT_PLUGIN_ROOT="/absolute/path/to/plugins/development"
```

Inspect [the user hook configuration](hooks/codex-user.json). If
`${CODEX_HOME:-$HOME/.codex}/hooks.json` does not exist, copy that file there;
otherwise merge its event groups into the existing file without overwriting
other hooks. This marketplace does not edit the user's configuration. Open
`/hooks` in Codex, review the definitions, and trust them. Untrusted, disabled,
or missing hooks do not run. Keep the environment variable set for every Codex
launch, including desktop or IDE launches. A missing or stale path makes the
Python command fail and can block every matched call, including read-only ones.
Update the path and inspect the scripts after upgrades: Codex trusts the hook
definition, not the script contents or the environment variable's value.
If `python3` is unavailable or a hook fails with another exit code, Codex may
continue the tool call rather than deny it.

To verify, use a disposable Git repository and ask Codex to attempt a commit
you explicitly authorize there. The recognized command should be denied; check
that HEAD did not change. Do not use a real push or publication as a smoke test.
Check `/hooks` after client upgrades and disable a duplicate source if upstream
starts loading the packaged hook as well. User hooks also apply to other Codex
workspaces; this is not scoped to the marketplace installation.

### Local work events

On macOS or Linux, opt in for a client launch by choosing a private absolute
directory. Nothing is recorded when the variable is unset:

```sh
export SONSU_WORK_LOG_DIR="$HOME/.local/state/sonsu-work-events"
```

The development extension records main-session start and shutdown in omp.
Claude Code records session, subagent and task lifecycle events and API turn
failures when its plugin hooks run. Codex records session and subagent events
and interrupts only when the separately registered and trusted user hook runs;
packaged hooks do not work on the versions noted above. This is not a complete
task history, and a stop or task-completed event is not proof of success.

`events.jsonl` contains a version, UTC time, client, event kind, and SHA-256
hashes of available session, agent, and task IDs. It does not store prompts,
commands, output, source, or project paths. Hashes are pseudonyms, not encryption;
the timing and client are still sensitive metadata. The file is created with
owner-only access and concurrent writes are locked. Existing files with broader
permissions or a different owner are rejected. Recording errors are written to
stderr without blocking work; the client may suppress hook output. There is no
remote upload or automatic deletion: inspect and remove your own log when no
longer needed.

For a handoff, ask the agent to summarize confirmed decisions, completed and
remaining work, and verification from the actual session and artifacts. Events
alone do not contain those details; label unavailable information rather than
inventing it.

### Declared verification

A project may authorize a `.workflow-checks.json` at its Git root, for example:

```json
{
  "checks": [
    {
      "id": "unit",
      "argv": ["python3", "-m", "unittest"],
      "actions": ["commit", "push"]
    }
  ]
}
```

The runner executes the declared argv without invoking a shell itself and
records a successful result only when the full tracked and unignored working
tree is unchanged during the check. To compute the tree it runs
`git add -A --sparse` and `git add --renormalize -u --sparse` against a
temporary index; Git may execute configured clean filters. Authorize both the
declared command and those repository-configured filters before use. Git must
support `git add --sparse`; absent sparse-checkout files can prevent the
snapshot and require materializing those files before the check.
When the action and target repository are identified, a missing or stale receipt
blocks a declared action and prints the exact runner command including its root.
Shell indirection, such as a subshell changing directory or `GIT_DIR` overrides,
can prevent correct target identification even for a recognized command.
Inspect the command and target before approving it.
Before committing, stage the same tree that was checked. A plain `git push`
binds to HEAD only for simple or current push defaults without configured
refspecs, mirrors, or tag following. For an identified repository, partial
commits, chained commands, shell expansions, per-command Git configuration,
explicit push arguments, and remote publication targets cannot be bound and are
blocked when the relevant action is declared. Literal text resembling shell
expansion may also be blocked.

Without a declaration, matching checks, or a Git repository, the evidence gate
is **unverified**, not passed. A recognized command that cannot be parsed is
blocked even without a declaration. The registered Codex user hook denies
recognized actions before evidence inspection; an unregistered hook enforces
nothing.
The omp extension checks the target when it receives `tool_call`. It does not
prompt or recheck if the target changes before execution. Claude Code's hook
cannot recheck after its permission dialog. Receipts capture
the declared command's exit status, declaration hash and tree, not a quality
score or test adequacy. Ignored files, uncommitted submodule contents,
dependencies, environment, external services, and Git hooks that change the
eventual target are outside the tree binding. The receipt store is writable by
the same OS user and is not
tamper-proof. The workflow owner evaluates the stage and reports its evidence.

Changing or removing an existing required check cannot silently disable it:
such a change must be handled outside this gate with explicit authorization.
The runner invalidates an old receipt before a new run; if an interrupted run
leaves a lock, an operator must inspect and remove the stale lock before retrying.

Run the deterministic guard checks from the repository root:

```sh
bun test plugins/development/tests/guard.test.ts
python3 -B -m unittest discover -s plugins/development/tests -p 'test_*.py'
```

## Contributing

Pull requests are welcome; ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Follow
[the contributor guide](../../CONTRIBUTING.md), including plugin checks.

## License

[MIT](../../LICENSE) © sonsu-lee. Third-party notices are in
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES); source revisions are in
[SOURCES.md](SOURCES.md).
