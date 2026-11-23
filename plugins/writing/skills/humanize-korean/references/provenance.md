# Provenance and adaptation record

Read when auditing, updating, or explaining this adaptation of
[im-not-ai][upstream] at commit `b37e0206d31fffd9149bf57168d4d62eb2086bee`,
under the bundled [MIT license](../LICENSE). It is not needed to edit prose.

The portable workflow comes from `codex/skills/humanize-korean/SKILL.md` and its
roles; actual helpers come from root `scripts/`, not Codex wrapper scripts.

Adaptations: English instructions with Korean examples; all Korean prose is
eligible, including technical documents; exact span and terminology protections;
caller-owned temporary runs; installed-relative runtime imports. The complete
85-pattern diagnostic index and its operational taxonomy conditions are
consolidated in `diagnosis-rules.md`; quick rules retain the upstream selected
subset. Research history, release/build tooling, client configuration, web
service specifications, and development experiments are not runtime resources.

The adaptation also distinguishes numbered procedures from referenced `N)` and
`[N]` footnote definitions in preparation and fidelity checks, so runbook steps
remain editable. Fidelity retains signed numeric values and attribution for
all supported quote delimiters. Summary exclusion is shared by the gates and
limited to complete terminal metadata outside code examples. Unit expressions
remain part of direct semantic review rather than a new unit-parsing subsystem.

[upstream]: https://github.com/epoko77-ai/im-not-ai/tree/b37e0206d31fffd9149bf57168d4d62eb2086bee
