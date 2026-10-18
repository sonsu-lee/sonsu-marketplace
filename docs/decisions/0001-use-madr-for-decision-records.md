---
status: accepted
date: 2026-10-19
decision-makers: sonsu-lee
---

# Use MADR 4.0.0 for decision records

## Context and Problem Statement

Decisions about this marketplace, such as the plugin format, depend on omp
behavior that changes between releases. The README says how to do things but
not why, and the reasons are easy to lose. Which format should decision records
follow, and how are they kept up to date?

## Considered Options

* [MADR](https://adr.github.io/madr/) 4.0.0
* [Michael Nygard's template](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
* No separate records; explain decisions in the README

## Decision Outcome

Chosen option: "MADR 4.0.0", because it records the options that were
considered and how a decision is confirmed, which the decisions here depend on,
and its required sections stay small.

Record one significant choice and its rationale per ADR, rather than treating
each implementation step as a new decision. Keep current operating instructions
separate so readers can understand why a choice was made without using a
historical record as a command reference.

Use the [AWS ADR lifecycle](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html):
proposals can be refined during review, while accepted decisions retain their
rationale. A changed decision gets a new record that supersedes the old one.
This preserves the context needed to evaluate later reversals.

### Current instructions

The [README's decision-record guidance](../../README.md#decision-records)
defines naming, required sections, review states, and documentation ownership.
Use the [MADR 4.0.0 template](https://github.com/adr/madr/blob/4.0.0/template/adr-template.md)
when drafting a record.

### Consequences

* Good, because the reasons for a decision and the rejected options stay next
  to the code they affect.
* Good, because superseded records keep the history of why a decision changed.
* Bad, because changing an accepted decision needs a new record rather than
  an edit.

### Confirmation

Review records against the README's decision-record guidance: each captures
a coherent choice, considered alternatives, and its rationale, with an accurate
review state and links to current operational instructions.

## Pros and Cons of the Options

### MADR 4.0.0

* Good, because it has sections for considered options, their pros and cons,
  and confirmation.
* Good, because its file naming and `docs/decisions/` location need no extra
  convention.
* Neutral, because it is a community template, not a formal standard.

### Michael Nygard's template

* Good, because it is the original ADR format and the shortest.
* Bad, because it has no section for the options that were rejected.

### No separate records

* Good, because there is only one document to maintain.
* Bad, because reasons and rejected options would crowd out the instructions in
  the README.
