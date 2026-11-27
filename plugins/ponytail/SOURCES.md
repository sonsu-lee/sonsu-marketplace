# Ponytail sources

[DietrichGebert/ponytail][upstream], commit
`96608e078b2d5ea607c5c3b8b5a54d1c1fba6846`, supplies all six [skill
directories][skills] and the [agentic benchmark report][benchmark]. Its [MIT
license](THIRD-PARTY-LICENSES) is included verbatim.

The marketplace package uses the upstream skill names and decision ladder. It
drops client-specific frontmatter, hooks and settings, documents invocation for
the three local hosts, and keeps project authorization and test requirements in
force. Reviews count only identifiable proposed cuts. The report is bundled in
the gain skill with its reproduction link pointed upstream; none of its numbers
measure this adaptation.

`skills/ponytail/references/judgment.md` and `judgment-react.md` are this
marketplace's own guidance, not upstream Ponytail text. They draw on
[Toss Frontend Fundamentals][toss] and React's [You Might Not Need an
Effect][effect]; no text is copied from either.

[upstream]: https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846
[skills]: https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/skills
[benchmark]: https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/benchmarks/results/2026-10-07-agentic.md
[toss]: https://frontend-fundamentals.com/code-quality/code/
[effect]: https://react.dev/learn/you-might-not-need-an-effect
