---
status: accepted
date: 2026-10-18
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

Records follow these rules:

* Each record is `docs/decisions/NNNN-title-with-dashes.md`, numbered in
  sequence, and starts from the
  [MADR 4.0.0 template](https://github.com/adr/madr/blob/4.0.0/template/adr-template.md).
  `status` and `date` go in the YAML front matter.
* An accepted record is not edited, except to fix errors or to change its
  `status`. To change a decision, write a new record and set the old record's
  `status` to `superseded by ADR-NNNN`. This follows the
  [AWS Prescriptive Guidance ADR process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html).

### Consequences

* Good, because the reasons for a decision and the rejected options stay next
  to the code they affect.
* Good, because superseded records keep the history of why a decision changed.
* Bad, because every decision change needs a new record rather than an edit.

### Confirmation

Every file in `docs/decisions/` has `status` and `date` front matter and the
sections "Context and Problem Statement", "Considered Options", and "Decision
Outcome".

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
