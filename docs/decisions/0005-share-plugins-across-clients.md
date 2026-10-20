# Share plugin sources across clients and separate execution differences

- Date: 2026-10-20
- Status: proposed

## Context

Adding Codex alongside omp raises a recurring design choice: should each new
client get its own copy of the plugins, or should clients share plugin sources?
Copies allow independent customization but make common behavior, fixes, and
assets diverge. This cost grows with every additional client.

[ADR-0002](0002-plugin-format.md) already selected standard Agent Plugins
packages with client-specific components alongside them. It does not settle
how shared workflows should accommodate different client capabilities.
Clients can expose different tools, subagent APIs, native workflows, and
permission controls even when they use the same underlying model. The boundary
here is the client and execution environment, not the model name.

Review illustrates the distinction: the current omp procedure uses a native
reviewer plus a focused worker, while the Codex procedure uses custom general
and focused workers. Their review criteria can be shared without pretending
their native features or execution APIs are interchangeable.

## Decision

Keep one source package per plugin as clients are added. Share the skill's
purpose, judgment criteria, and common behavior, together with standard
metadata, scripts, and assets. Put only necessary client-specific discovery,
metadata, components, and execution procedures at the client boundary.
Do not duplicate a plugin merely because a new client or model is introduced.

Preserve common workflow requirements without forcing identical execution.
Use each client's supported capabilities; when a required capability is
unavailable, disclose the limitation rather than silently weaken the workflow
or claim equivalent support. This keeps common changes maintainable in one
place without coupling every client to another client's native features.

This direction applies to future clients as well. omp, Codex, and Claude Code
are the current application of the approach. Claude Code shows that client
metadata can include a package-level manifest when a client would otherwise
load another client's components; it is not a second package tree. Keep actual
support scope, client procedures, and verification
requirements in the [layout](../../README.md#layout),
[plugin-authoring procedure](../../README.md#adding-a-plugin), and
[test procedure](../../README.md#testing-a-plugin). This proposal extends
ADR-0002's portability direction; it does not replace its packaging choice or
change its accepted status.

## Rejected alternatives

- **Maintain a plugin tree for each client:** permits independent evolution,
  but duplicates common behavior and assets and requires fixes to be carried
  across copies. The current client differences do not justify that cost.
- **Force one execution procedure on every client:** avoids separate execution
  references, but either gives up useful native capabilities or assumes APIs
  and guarantees that some clients do not provide. Share the workflow's
  requirements, not an unsupported promise of identical execution.

## Consequences

Common fixes have one source, but changes to shared behavior require checks
across supported clients. Every added client needs its own installation,
discovery, and representative execution evidence; another client's success
does not establish compatibility. Model choice alone does not justify a new
package or establish workflow quality.

Client-specific procedures must track their APIs and permission boundaries.
Shared instructions do not enforce permissions or guarantee identical outputs.
If a future client's packaging or required behavior cannot fit this boundary,
revisit the design explicitly rather than hiding a fork inside the shared
package. Implementation completion does not change this record's proposed
status.
