# Keep model evaluations local and run only model-free checks in CI

- Date: 2026-10-23
- Status: accepted
- Decision-makers: sonsu-lee

## Context

Skill changes need evidence from real model runs in omp, Codex, and Claude
Code, as in [#22](https://github.com/sonsu-lee/sonsu-marketplace/pull/22).
Those runs need model credentials, and the maintainer wants to use the existing
Claude and ChatGPT subscriptions rather than pay for API usage. The repository
is public and maintained by one person, who is also the only author of skill
changes.

Running those checks in this repository's CI would put subscription
credentials where the security boundary cannot hold them:

- Workflow logs of a public repository are public.
- An agent under test runs with its credential, so it can read it. Masking,
  manual dispatch, and branch restrictions reduce but do not remove that
  exposure. Even OpenAI's own Codex action, which proxies the key, states that
  a process able to read its memory can read the key.
- OpenAI documents subscription logins in CI only for trusted private
  automation, and a Codex subscription login rotates its refresh token, which
  a CI copy would have to write back to the secret after every refresh.
  Anthropic describes subscription OAuth for its own applications.

## Decision

Run model evaluations locally with subscription logins in dedicated test
client homes, never in this repository's CI. Record each run's profile and
results in the pull request. CI runs only checks that need no credentials,
such as plugin catalogs, skill format, installation, discovery, and loading.
The current procedure is in the README's
[testing section](../../README.md#testing-a-plugin).

This keeps subscription credentials on the maintainer's machine and out of
anything public, and uses the existing subscriptions instead of paid API usage.

## Rejected alternatives

- **Subscription logins as repository secrets with a manual workflow:** keeps
  the subscriptions but exposes them to public logs and to the agents under
  test, and needs a token that can rewrite repository secrets for Codex.
- **A private repository or self-hosted runner that checks out this one:**
  makes logs private, but the agents still hold the subscription credentials,
  and it adds a second environment to maintain for one contributor.
- **A credential gateway such as omp's auth-broker and auth-gateway:** keeps
  subscription credentials on one machine and gives CI only a revocable token,
  but needs a network path from hosted runners to that machine, is unverified
  with Codex and Claude Code, and leaves open whether routing subscription
  OAuth through a proxy fits the providers' terms.
- **API keys in CI with spending limits:** the standard CI setup, bounding
  exposure to one revocable key and a budget, but it adds per-run cost while
  one maintainer already runs these checks when changing a skill.

## Consequences

Model evaluation evidence depends on the maintainer running it and reporting
it honestly; nothing blocks a merge without it. Results come from one machine
and reflect the pinned model profile, not every user's configuration.
The agents under test can still read the test-home credentials, but only on
the maintainer's machine and with nothing published. Runs consume the
subscriptions' usage limits instead of adding API charges.

Reconsider when outside contributors change skills, when scheduled regression
runs across model releases become necessary, or when results must come from an
environment independent of the maintainer's machine. API keys with spending
limits in a gated workflow are the expected next step in those cases.
