# Commit validation

Select the execution setup and configuration independently. Run from the target
repository's root, not from the installed skill directory.

## Reuse the repository's execution setup

Inspect contributor instructions, package scripts, dependency declarations and
lockfiles, and relevant hook or CI configuration. Use the documented validator
and version, even if it is not commitlint. Do not invoke a hook wholesale when
it performs unrelated work; run its documented message check with the proposed
message as input.

A declared dependency or managed tool that is not installed is an existing
setup needing its documented installation procedure, not an absent setup.
If it cannot run, report the blocker. Do not upgrade it or switch to the pinned
fallback after a failure. A configuration file alone does not establish a runner
or a version; the fallback may load that file if no execution setup exists.

Save the exact complete message in a temporary UTF-8 file and set `message_file`
to its absolute path. Read it back to verify the nonempty header and intended
body and footers: commitlint can skip empty files. Use the input mechanism the
repository's validator supports, and verify it checks this message rather than
an earlier commit. A hook that has not run is not proof of validation.

For a repository with a directly installed commitlint binary and no wrapper
command, for example:

```sh
./node_modules/.bin/commitlint --verbose --edit "$message_file"
```

Use the repository's package-manager command instead when appropriate, such as
for Yarn Plug'n'Play. Preserve its flags and warning policy; do not blindly add
`--strict` to an existing command.

## Use npx only without an existing execution setup

The fallback requires Node.js 22.12.0 or newer and npm. Its first run requires
npm registry access. It does not add a dependency to the target repository.

When a repository commitlint configuration exists, preserve it:

```sh
npx --yes --package @commitlint/cli@21.2.4 commitlint \
  --verbose --edit "$message_file"
```

Honor an explicitly selected config path with `--config`. Preserve its required
presets and plugins and follow their documented setup. A missing explicitly
selected config, invalid config, or incompatible dependency is a blocker; do
not replace it with the bundled defaults. Do not use `--default-config` to hide
configuration problems.

## Select defaults only when configuration is absent

Only if no repository commitlint configuration is established, set `skill_dir`
to the absolute directory containing the loaded `SKILL.md` and use its
`assets/commitlint.config.mjs`. Do not guess an omp cache path or copy the asset
into the repository.

With an existing commitlint installation, keep that executable and add
`--config "$skill_dir/assets/commitlint.config.mjs" --strict` to its supported
message-check invocation. Do not replace its version just to load this asset;
report incompatibility if it cannot load it. For a different validator, keep
its documented behavior and review skill defaults it does not check manually.

With neither an execution setup nor configuration:

```sh
npx --yes --package @commitlint/cli@21.2.4 commitlint \
  --config "$skill_dir/assets/commitlint.config.mjs" \
  --strict --verbose --edit "$message_file"
```

The bundled configuration is self-contained ESM with no external presets or
imports. It accepts `!`, a breaking-change footer, or both. It does not determine
whether the message accurately describes the change.

## Finish the check

Require a successful exit and evidence that the intended message was checked.
Respect existing repository warning levels; the bundled defaults require no
errors or warnings. Do not treat a failed execution as validation success or
silently fall back to a different tool. Recheck after every message edit and
remove the temporary message file afterward.

Do not install a new project manifest, configuration, hook, or CI job just to
run the fallback. Tool installation and configuration changes are separate from
writing a commit message.
