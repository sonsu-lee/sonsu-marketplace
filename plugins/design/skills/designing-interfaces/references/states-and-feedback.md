# State and feedback judgments

These are contextual research-derived heuristics, not validated product outcomes
or proof of accessibility conformance. Video sources give intervals in seconds;
their stills and captions are sampled, not continuous independent validation.
Article sources are linked by URL; results they report belong to their own
product and context, not to the current artifact. Some article links redirect
to a conference session page: "(session transcript)" marks a page that carries
the talk's transcript, and "(session video)" one whose linked talk video's
captions were the source. Check applicable standards separately.

## P28: Differentiate selected state, current status, and available action

Distinguish selection, status and available action; reconcile dependent choices
without discarding compatible ones. When the system knows that a target or item
carries a risk, show the warning before the step that commits the user, not
after it, together with the source the warning relies on and what the user can
do next; a final confirmation may follow. Whether to block the action is a
policy decision. Carry the risk in text or a labelled icon as well as color,
and verify that cue in the artifact before calling it accessible.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=iHqhtvWn_0s&t=62s> — 62–100 seconds. The cited
  source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=iHqhtvWn_0s&t=207s> — 207–249 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=iHqhtvWn_0s&t=393s> — 393–440 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=543s> — 543–570 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=KHu6uCrtiZ8> — 414–548 seconds. The cited
  source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=Xji7nZLcfOQ&t=561s> — 561–632.85 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://toss.tech/article/27370> — a reported-account warning shown while
  the recipient is entered, with the number of police reports (session video).
- <https://toss.tech/article/27348> — a risk area on an item's detail screen
  and one more confirmation before the final trade (session video).

## P29: Design a coherent composing and submission state

Design the composing state and show only input-criterion outcomes actually
checked.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=347s> — 347–437 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=572s> — 572–637 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=qbE7pAnVFLo&t=754s> — 755.94–803.449 seconds.
  Targeted 785-second JPEG shows a visible numeric/length criteria list with
  different states alongside a tooltip-only alternative.

## P30: Preserve message ownership and reading order across turns

Keep message ownership and reading order recognizable across turns.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=639s> — 639–685 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=903s> — 903–920 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P31: Choose an overlay that preserves the needed context and has a clear exit

Choose an overlay appropriate to the task, with context and a clear exit.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=438s> — 438–510 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=1002s> — 1002–1102 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=l-y3tR3N_b8&t=386> — 386.16–453.15 seconds.
  427-second retained frame shows the hero and one expanded information panel
  alongside collapsed panels. A still does not establish the event mechanism;
  the narration supplies that rationale.
- <https://www.youtube.com/watch?v=cZCvf0HY0jk&t=1471> — 1471.96–1504.149 seconds.
  At 1480 seconds the first plan is expanded while other rows are collapsed; at
  1500 seconds several plan detail regions are simultaneously expanded. These
  retained states support the described disclosure model, not a measured
  comparative advantage or an independently exercised live site.

## P32: Associate progress, response content and sources with the right state

Associate progress and sources with the correct response; claim completion
only when known. For long-running processing, group internal states into a
few steps that tell users where things stand, decided with the engineers and
operators who own those states, and keep every state that needs user action,
such as failure or return; one label must not mean both in progress and done.
Show real partial results as they arrive and mark expected delay as in
progress so it does not read as an error; do not simulate progress. Say users
can leave only after confirming that processing continues without them and
that completion or failure reaches them. For an AI answer, show what it cannot
answer or does not know and what the user can do next, including when and how
a person takes over where a human channel exists or is required, rather than
letting it guess.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=687s> — 687–790 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=3ZXBb8Ol_2M&t=267s> — 267–346 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://toss.tech/article/remittance_transfer> — internal transfer stages
  reduced with the server engineer to a few user-meaningful states; in a
  pre-launch trial transfer, one status stayed on screen for days.
- <https://toss.tech/article/toss-securities-earnings-call> — translation lag
  marked as in progress so it would not be taken for an error.
- <https://toss.tech/article/1st_interaction_designer> — a wait screen of
  unrelated imagery replaced by review results as they completed.
- <https://toss.tech/article/27372> — users were returned to the start once
  a teammate confirmed the review continues with the app closed, with a
  notification on completion (session video).
- <https://toss.tech/article/27370> — transfers blocked by bank maintenance
  were queued and users notified when sent; one completion screen served every
  entry point (session video).
- <https://toss.tech/article/chatbot> — answer rules against guessing, for
  saying when it does not know, and for handoff conditions and authority
  limits.
- <https://toss.tech/article/AI_chatbot> — the designer worked out how to show
  what the assistant can and cannot do; suggested questions came from actual
  inquiries.

## P33: Match suggestions to the user's current context and task state

Update suggestions to reflect the current task and state.

Limit: Source-grounded design guidance, not measured user outcomes or runtime
validation.

- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=298s> — 298–346 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=572s> — 572–591 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.
- <https://www.youtube.com/watch?v=ENIvZFD9iLM&t=725s> — 725–742 seconds. The
  cited source illustrates or discusses this decision; it does not establish an
  outcome for the current artifact.

## P48: Explain relevant notification retention in an empty history

Explain relevant retention limits when notification history is empty.

Limit: Independently critiqued captions and static authoring states, not
enforced retention, measured comprehension or source-product conformance.

- <https://www.youtube.com/watch?v=Hzt7nv2ZBuo&t=486s> — 486.39–512.27 seconds.
  496-second frame shows no-notification heading, notification-settings copy and
  bottom explanatory retention/deletion notes.

## P51: Make each error state say what happened, who can fix it and what next

Write an error state from the cause, fix and avoidability the engineers
confirm: say what happened, whether the user can resolve it, and a next action
in the user's terms that is reachable from the message, such as a direct
contact action rather than an instruction to find support. Where security
keeps the cause vague, the message can still tell users whether the problem is
theirs to fix. Choose the container by how much must be explained and how
serious it is: an explanation the user needs does not belong in a message that
disappears on a timer, and alarm color is for real severity. Prevent an error,
for example by not offering an option certain to fail, only where that policy
is confirmed and users can still find their intended path. As an irreversible
consequence such as a lockout approaches, show the remaining attempts and the
alternatives before the last try, give the reason for a failure only as far as
the security owner allows, then route to whatever help remains.

Limit: Article-derived writing and recovery practice; it does not show that a
message is announced to assistive technology or that a stated fix works.

- <https://toss.tech/article/how-to-write-error-message> — situation, reason
  and fix; a dialog instead of a timed toast; saying whether users can fix it;
  a one-tap contact action; an error avoided by not listing an option the
  transfer rule rejects.
- <https://toss.tech/article/introducing-toss-error-message-system> — writers
  asked engineers why each error occurs, how it is fixed and whether it could
  be avoided.
- <https://toss.tech/article/27366> — remaining attempts and reasons shown, a
  stronger suggestion before the last try, and routing by whether help was
  possible (session video).
- <https://toss.tech/article/45787> — users whose names differed in format from
  external records failed repeatedly without a cause until locked out.

## P52: Expose visual state to assistive technology and check what is heard first

Expose progress, state changes and outcomes as text or state that assistive
technology can read and announce, including what a progress bar or other
graphic conveys. A distinct sound can reinforce an announcement but does not
replace it, since some users turn sound off or read with a braille display. In
dense items, check what a screen reader speaks first: guidance, role or state
placed after long content can be missed by users who move on early. The order
of the app's own label text is a design choice; the platform's order for role
and state is not, and changing it in one app may break consistency with other
apps, so do not override it in the app; raise the need for an operating-system
or screen-reader setting with the product owner. Splitting an item into more
focus stops can surface its role sooner but may slow navigation; weigh that
tradeoff. Claim assistive-technology behavior only after running it, and treat
sessions with people who use that technology daily as the evidence for
usability.

Limit: Article cases from authentication, list and event flows; not a
conformance assessment, and announcement behavior varies by platform and
version.

- <https://toss.tech/article/accessibility_face> — a progress bar that showed
  state only visually gained progress and completion sounds after sessions with
  blind users.
- <https://toss.tech/article/voiceover_usability> — role spoken after long
  list content; splitting, sound hints and role-first reading were weighed, and
  a platform-level option was preferred to an app-only reorder.
- <https://toss.tech/article/27178> — reading the visual screen's text aloud
  failed repeated sessions with blind users, who stopped listening before the
  next-step guidance (session transcript).
