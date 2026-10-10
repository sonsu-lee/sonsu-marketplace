# Upstream source

- Repository: <https://github.com/forjd/better-writing>
- Commit: `e8fcfeb4220291b619c651b2fd83bf814ba0890e`
- Main HEAD verified: 2026-09-25
- Skill: `better-writing`
- License: [MIT](THIRD_PARTY_NOTICES.md)

The source material is copied from the pinned upstream commit. The package manifest, README, and license notice are local packaging material. The installed public skill ID is `fluent-english:fluent-english`; `better-writing` remains the upstream skill name.

The installed skill bundle is under `skills/fluent-english/`. Local packaging changes rename the skill, include everyday messages and technical prose, organise `SKILL.md` around procedure/result/example/boundaries, place preservation and strict-pass rules in `references/voice-and-context.md`, and add the read-only `scripts/voice_profile.py` and `scripts/validate_preservation.py` tools.

The `cursor/plugins` attribution in `references/sources.md` for voiceless prose as a tell refers to the `pstack/skills/unslop` “Adding soul” section before PR #329.
