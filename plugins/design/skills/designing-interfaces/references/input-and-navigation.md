# Input and navigation judgments

These are contextual research-derived heuristics, not validated product outcomes
or proof of accessibility conformance. Video sources give intervals in seconds;
their stills and captions are sampled, not continuous independent validation.
Article sources are linked by URL; results they report belong to their own
product and context, not to the current artifact. Some article links redirect
to a conference session page: "(session transcript)" marks a page that carries
the talk's transcript, and "(session video)" one whose linked talk video's
captions were the source. Check applicable standards separately.

## P06: Design the full hit area, not just the visible text or icon

Design the interactive area and separation, not only the visible glyph.

Limit: Supported as source guidance, not a measured usability or conversion
outcome.

- <https://www.youtube.com/watch?v=ZT1UZQCTj_U&t=69s> — 69–96 seconds. The cited
  source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=YNDhbNQo_io&t=146s> — 146–200 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P08: Label icons whose meaning is not reliably recognizable

Label icons whose meaning would otherwise be uncertain.

Limit: Supported as source guidance, not a measured usability or conversion
outcome.

- <https://www.youtube.com/watch?v=ZT1UZQCTj_U&t=311s> — 311–352 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P09: Simplify primary navigation without hiding other destinations

Prioritize primary navigation while keeping other destinations discoverable.
Group destinations by the action users come to take rather than by the team,
business line or data source behind them. Offer a secondary function in the
situation that calls for it, such as just before the step it supports or after
a failure, while keeping another stable path to it. Moving or removing an
existing entry point is the owner's decision; state which users would lose
which path.

Limit: Supported as source guidance, not a measured usability or conversion
outcome.

- <https://www.youtube.com/watch?v=ZT1UZQCTj_U&t=352s> — 352–403 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://toss.tech/article/mydoc> — a team-based document hub regrouped into
  issuing, paying and receiving notices.
- <https://toss.tech/article/bad-reference-uses> — license check and support
  moved to the moments they are needed, with a second path for the check.

## P42: Match selection controls to the allowed choice combinations

Match selection controls to allowed combinations.

Limit: Conditional research guidance with independently critiqued evidence
attribution; no runtime product, measured user outcome or overall accessibility
conformance was established. Suggested checks remain unperformed.

- <https://www.youtube.com/watch?v=nxFe-EC02qs&t=53s> — 53–133 seconds. The cited
  source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P43: Separate navigation from control of applicable automatic content

Distinguish navigation from controls for applicable automatic content.

Limit: Conditional research guidance with independently critiqued evidence
attribution; no runtime product, measured user outcome or overall accessibility
conformance was established. Suggested checks remain unperformed.

- <https://www.youtube.com/watch?v=5SOloM9U-1o&t=290s> — 290–327.42 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P47: Choose input mechanisms for the actual values and adjustment task

Choose input controls for actual values and adjustment tasks, retaining
compatibility.

Limit: Independently audited and corrected source guidance; no measured
input-speed advantage, implemented control behavior or source accessibility
conformance. Suggested checks remain unperformed.

- <https://www.youtube.com/watch?v=qbE7pAnVFLo&t=414s> — 414.9–496.249 seconds.
  The retained 458-second source sample shows two payment radio options versus
  the same choices in an expanded dropdown.
- <https://www.youtube.com/watch?v=hqT_bEsauWs&t=499s> — 499.449–607.68 seconds.
  The retained699-second editor state is later illustrative selection context,
  outside499.449–607.68. It does not demonstrate the earlier sequential
  interaction or prove a compatibility dependency.
- <https://www.youtube.com/watch?v=iYnP-3vsDhI> — 292.0–423.409 seconds.
  390-second frame compares +/- with editable quantity against dropdown and
  arrow-based examples; 298-second sample shows original control.
- <https://www.youtube.com/watch?v=nTbckygsz4M&t=902s> — 902.519–1001.509 seconds.
  The 927-second target shows a mixed brand-badged product stream. The
  943-second sample shows the existing multi-line logo block selected while the
  presenter describes brand tabs; it is not an implemented selector. The
  1000-second target shows an original/revised canvas comparison with an
  All/brand strip and separate brand-headed product rows. None establishes
  working filtering or correct brand/product data.

## P49: Ask only the questions the task needs

Before polishing a form or branching step, check each question against what
the task actually needs. Reuse values the system already holds or can derive
and may use for this purpose: prefill them where the user may change them, or
show them for confirmation with the existing correction path where they may
not, and keep a final review before submission. When a value the user may
decide is inferred with uncertainty, offer candidates and leave the choice
with the user. Never reuse a choice that amounts to consent, and do not carry
a previous answer to a costly-to-reverse choice into a new transaction
automatically; whether such a choice may have a default at all follows P55 in
`commitments-and-policy.md`. Whether a field can go is decided by whoever
consumes the data, such as operations, finance or legal, so propose a removal
with their answer rather than deleting on design judgment. When a question
must stay, rephrase it into one users can answer at once from their own
situation, such as whether they already hold a document, instead of a choice
between processes whose consequences they cannot foresee, and keep the
existing paths reachable.

Limit: Article cases from internal tools, applications and claim flows; they
do not show that dropping any particular question is safe or effective here.

- <https://toss.tech/article/real-reason> — the data's consumer named the one
  detail it needed; defaults came from merchant type and time, and a final
  confirmation stayed.
- <https://toss.tech/article/insurance-claim-process> — a choice between help
  and self-service became a question about having documents; the provider list
  narrowed to linked data, with another path for users without it.
- <https://toss.tech/article/rebuild-legacy-cs-products> — agents stopped
  retyping values the support tool already knew.
- <https://toss.tech/article/4-ways-for-minimum-input> — asks whether input
  can be avoided by filling known or previously entered information.
- <https://toss.tech/article/27378> — a request form dropped fields the system
  already knew and pre-checked access by job role (session video).
- <https://toss.tech/article/27368> — application steps were skipped where
  stored data existed, so each user saw different questions (session video).
- <https://toss.tech/article/27346> — legal confirmed a question had to stay,
  so it became a simple two-way choice; derivable fields were dropped (session
  video).
- <https://toss.tech/article/toss-money-transfer-bank-recommendation> — the
  bank was inferred from the account number, with several candidates and the
  final choice left to the user.

## P50: Show the concrete value before asking for an unavoidable cost

When a step that costs effort, verification or personal data cannot be
shortened, show before it what the user concretely gains and why the
information is needed, not only the action to take. Make the value specific
enough to imagine, for example a preview of the result. A preview built from
sample data must read as an example wherever attention lands: label it
visibly, and avoid the user's own name or changing figures that make it look
like their account. When and how consent or permissions are requested, and
their scope, remain the owner's policy decision; the design proposes the
explanation, not a new consent order.

Limit: Article cases of a lookup funnel, a sign-up flow and an observational
study; not evidence that a preview or explanation raises completion here.

- <https://toss.tech/article/value-first-cost-later> — a sample-data preview
  of the result placed before an external verification funnel the team could
  not shorten.
- <https://toss.tech/article/signup> — one platform asked for identity details
  without saying why; the article presents that as its hypothesis for the drop.
- <https://toss.tech/article/launching-product-in-one-day> — a satisfaction
  question folded into a dialog users were already using.
- <https://toss.tech/article/senior-usability-research> — older participants
  missed a small example tag and read a demo with their name and moving
  amounts as their own data.

## P53: Make pressable elements and content beyond the visible edge recognizable

Let each element's form show whether it can be pressed, and keep informational
elements from looking like controls. A tag styled like a button, a list that
mixes entry styles or an entry cue made only of bare text or a small arrow can
lead some users to the wrong target. When content continues below the fold or
inside a scrolling menu, show that more exists; some users do not scroll unless
something on screen suggests there is more. Check this at the device sizes and
large-text settings you support, where the cut moves, and treat a cue as a
proposal to verify on the rendered screen, not a property of a static mockup.

Limit: Moderated sessions with older users and a component's support feedback;
not a measurement for other audiences or of any particular cue.

- <https://toss.tech/article/senior-usability-research> — most participants
  missed text and arrow entry points; tags were taken for buttons, and some
  participants did not scroll without a visible cue.
- <https://toss.tech/article/toss-design-system> — a long menu at large text
  gave no sign of more items until a fade at its edges was specified.
