---
name: brainstorming
description: >-
  Use before creative work when a feature, component, change of behavior,
  or new project needs a design. Not for a settled design or a standalone
  PRD from agreed material.
license: MIT
metadata:
  source: https://github.com/obra/superpowers
  source-commit: 22f0b463e7a5e579904dd6211a520321035526f7
---

# Brainstorming

You are very good at building. You build what you believe your human
partner wants, and that belief is usually thinner than it feels. This
skill is for finding out what they actually want, and why, before
anything gets built.

People often haven't finished working out what they want. Good questions
help them think it through. When you understand the why, you make the
hundred decisions they never mention the way they would have made them.

## First: What Do You Actually Know?

Before you reply, ask yourself: what do I know about what they want, and
why?

- **Everything that matters is in the request** ("make the icon cornflower
  blue"). This is a quick, clear task. Do what they asked through the normal
  workflow. If an approved design or PRD already settles the choices, use it.
- **Something non-trivial is missing.** Start the conversation.

Before you start implementing, you must, in order:

1. Lay out the approaches in a message of their own, and have your
   human partner pick one unless they have handed you the choice.
2. Write the design, short or full (see Size the Work).
3. Get their approval of that design.
4. If planning is in scope, hand the approved design to `development:writing-plans`.

If nothing is open when you write your first message and there's one
sensible way, steps 1 to 3 happen in that message.

## Look Before You Ask

For a requested design interview or draft refinement, load the appropriate
Grill skill before opening the draft. For a code task, load `ponytail` before
inspecting its implementation. If it is missing, stop before reading code.

In an existing project, or when they've given you context (a spec, a plan,
a handoff, files they pointed at, earlier conversation), dig in before your
first message. Read what they referred to and the code or material it
connects to, and keep reading until you can explain how the relevant
parts work today and what this change would touch. Never ask what the
project or their context already answers, or reopen what they've
already decided.

## Your First Message

Before replying to a design request with an open choice, read
[Your First Message and The Conversation](references/conversation.md).
Use the detailed-request or open-question branch there. If they did not
ask for brainstorming and choose to skip the discussion, return to the
requested workflow; its approvals still apply.

## The Conversation

Follow the same reference for asking one question at a time, laying out
the approaches, showing visual choices, and offering a throwaway spike.
Ask a question only when the answer would change what gets built and
neither the request nor the project answers it.

## Play It Back

Play back as you go. As soon as you understand one part well enough to
describe it (what it's for and who it serves, say, or how one piece
behaves), describe that part back in about 200-300 words, then return to
questions about the next part. Playback and questions alternate through
the whole conversation; the last chunk covers whatever is left.

Only what they said goes in as theirs. Anything you filled in goes in
as your proposal, with your reason. End each chunk by asking what's wrong
or missing.

Before you send a chunk, check it: does it describe something they'll
look at, like a page, a screen, a schedule, or a printout? If so, put a
text sketch next to the description. If the look itself is theirs to
decide and they haven't seen the visual companion offer yet, send the
offer instead (its own message, below) and hold the chunk for the next
message. Once they've accepted, put a mockup next to the description.

## Size the Work

Once you understand what they want and they've picked an approach, say
how big the work is in plain words. They can override it.

- **A small change:** a short design doc: what you already covered together,
  written down.
- **A project:** the full written design (below).

Short or full, the design doc has an **Approaches** part: the two or
three ways you considered building it, what each trades off, which one
they picked, and why. If only one fits, explain why.

If it grows mid-task, stop, say so, and step up a size. If this is really
several independent projects, say so, agree on an order, and brainstorm
them one at a time.

## The Written Design

Write a plain document a talented builder in the domain could plan
from without going back to your human partner. Cover:

- intent and the why
- goals, non-goals, anti-goals
- constraints
- approaches (above)
- the parts of the how they decided, as they decided them
- what's left to the builder

For a small change, the short design covers the same points in a line
or two each and goes straight to your human partner, without the
builder check.

**Where it goes:** in chat unless they authorize a file and destination.
Use an undated name. Do not commit.

**Builder check** (for a project): read the
[builder check prompt](references/builder-check-prompt.md) and give it
to a fresh subagent through the host's native mechanism when permitted.
When you tell your human partner you're writing it up, say a reviewer will
read it first and you may come back once with a few questions. Don't hand
over the document until the check is back. Sort what the builder asks:

- **Answered already** by the conversation or the project: put the answer
  in the document.
- **Minor:** a sensible builder could settle it without changing what gets
  built. Settle it yourself and mark it in the document as your call.
- **Theirs:** only your human partner can answer it, and the answer changes
  what gets built.

Bring the "theirs" pile in one message, most important first. Update the
document with their answers, then hand it over with a short list of the
calls you made so they can check those while reading. That's the only
round of questions the check produces. Without a permitted subagent,
read the document as that builder yourself and identify it as a self-check.

**Nothing gets built until your human partner approves the design shown.**
Building includes writing product code, scaffolding, installing dependencies,
creating projects, and invoking an implementation skill. Reading and exploring
are fine. Build an approved spike only in its authorized location or a disposable
copy outside the worktree; it stays labeled throwaway,
and keeping what it produced is a new request. If they opted out of the
questions, follow the normal workflow rather than imposing this design gate.

Approval covers the design they saw, including one shown in chat; don't ask
twice. Stop here for design-only work. If they need a PRD, load
`prd:writing-prd` before drafting it from agreed material. For implementation
planning load `development:writing-plans` before breaking the approved design
or existing PRD into tasks. Report an unavailable required skill.

## Red Flags

If tempted to skip a conversation step, treat a reaction as approval, or keep
a spike as production code, read [Red Flags](references/red-flags.md).

## Visual Companion

Offer a visual just in time, not upfront, when the look itself is theirs
to decide. Make the offer its own message. If they decline, stay in text
unless they raise it. If they accept, read the
[visual companion guide](references/visual-companion.md) before showing
the first mockup using an available native surface.
