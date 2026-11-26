---
name: grill-with-docs
description: >-
  Interview the user about a plan or design while checking the repository's
  domain language and decisions. Use when repository domain documents matter;
  discussion alone does not authorize glossary or ADR changes.
---

# Grill with docs

Load `grilling` and, if installed, `domain-modeling` using the
[client loading reference](references/clients.md). Run the interview against
the repository's glossary, decision records, and relevant code. If the optional
companion is unavailable, say so and use the following standalone procedure:

- Read the glossary map, if present, to find the affected context. Compare
  proposed vocabulary with existing definitions and actual behavior. Bring a
  concrete example or contradiction to the next round.
- As a term resolves, offer a glossary entry: the project term and its agreed
  meaning, not implementation details. Edit the relevant glossary only when
  the user authorizes that write.
- Follow the project's ADR criteria. Without a local convention, offer a
  record when a decision is hard to reverse, surprising without context, and
  involves real alternatives and a tradeoff. Keep it in chat unless the user
  authorizes the ADR file. Glossary permission does not grant ADR permission.

These write boundaries also apply when `domain-modeling` is loaded. Keep other
decisions in the conversation; do not start implementation.
