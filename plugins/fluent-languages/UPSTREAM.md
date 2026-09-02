# Upstream provenance

The Korean skill in this local Codex plugin is a generation-oriented adapted subset of an MIT-licensed project. It is not a byte-identical vendor snapshot of the upstream repository.

The reusable local source is split at build time. `sources/core/` contains the shared communication and integrity contracts, while `sources/languages/korean.md` contains the Korean entrypoint and language guidance. `scripts/render-skills.py` combines every `sources/languages/<language>.md` file into a self-contained `skills/fluent-<language>/SKILL.md`; the core is not a separately triggered skill or runtime dependency.

This personal marketplace intentionally maintains the shared instruction source once in Korean. The language of those instructions does not select the response language; each generated skill's name, description, scope, and language-specific source do. A future externally distributed localization would require a separate equivalence review rather than independently edited core copies.

The cross-language discourse principles in `sources/core/communication.md` are local guidance derived from this marketplace's language-design review. They are not copied from or attributed to `im-not-ai`.

## `im-not-ai`

- Repository: <https://github.com/epoko77-ai/im-not-ai>
- Source commit: [`31a66d165a9cc6c26c4c1246553f95d0468d27fb`](https://github.com/epoko77-ai/im-not-ai/commit/31a66d165a9cc6c26c4c1246553f95d0468d27fb)
- Sources consulted:
  - [`docs/en/integration.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/docs/en/integration.md)
  - [`skills/humanize-korean/references/quick-rules.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md)
  - [`skills/humanize-korean/references/ai-tell-taxonomy.md`](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/ai-tell-taxonomy.md)
- Adapted subset: genre and register preservation, double-passive avoidance, promotional buzzword restraint, unsupported emphasis restraint, repeated conclusion restraint, unnecessary metaphor restraint, and a non-numeric final repetition check.
- Excluded: workspace handling, risk scores, severity grades, change-rate calculation, file-output workflow, and the diagnostic, rewrite, and finalizer multi-call pipeline.
- Local scope: Korean explanatory prose includes implementation reports, technical answers, and technical documents. Code, commands, logs, identifiers, protected literals, structure, facts, conditions, uncertainty, and obligation levels are preserved.

## MIT notice

```text
MIT License

Copyright (c) 2026 epoko77-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
