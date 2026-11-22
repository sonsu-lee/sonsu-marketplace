# Provenance and adaptation record

Read when auditing, updating, or explaining this adaptation of
[coji/natural-japanese][source] at commit
`03bc944a0c4a9f0b2a66eab065b30de5c529bf08`, under the exact upstream
[MIT license](../LICENSE), copyright 2026 coji. It is not needed to edit prose.

Instructions and supporting guides are translated into English while keeping
Japanese examples and linguistic distinctions. The runtime retains upstream
detectors, Japanese diagnostic text, and dependency ranges. Local fixes exclude
fenced examples from structural statistics and keep document-wide findings
stable across baseline comparisons without changing detector thresholds.
This adaptation removes client-specific metadata, resolves resources relative
to the installed skill, makes runner failures explicit, and preserves technical
prose eligibility. It omits upstream `semantic.py` and `exp` diagnosis (an
optional approximately 1 GB model download), corpus calibration, development
checks, release/install scaffolding, and benchmark fixtures. No remaining
workflow invokes those omitted components.

[source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
