---
name: grilling
description: >-
  Interview a user to resolve consequential uncertainties in a plan, decision,
  idea, or communication. Use when they request a stress test or interview;
  do not interrogate a clear request or ask for facts available from tools.
---

# Grilling

Interview the user relentlessly until you reach a shared understanding. Map
this as a **design tree**: every decision branches into the decisions that
hang off it.

Work the tree in **rounds**. The **frontier** is every consequential decision
whose prerequisites are already settled: the questions you can ask *now*
without guessing at answers you haven't heard yet. Ask the whole frontier in
one round: number each question and give your recommended answer. Then wait for
the user's answers before the next round.

Format a round like so:

```text
❓ **Q1** - **<question title>**: <question body, might be multiple
paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple
paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the
frontier outward and unblock questions that depended on them. Recompute the
frontier and ask the next round. A question whose answer depends on another
question still open in this round belongs to a *later* round, not this one.

Finding *facts* is your job, never the user's. Use the environment to look
them up; delegate independent research only when the host permits it. A
running exploration is an unsettled prerequisite. Only its downstream
questions wait; ask the rest of the frontier now. The *decisions* are the
user's: put each to them and wait.

When the frontier is empty, summarize the decisions and ask the user to confirm
the shared understanding. Confirmation closes the interview; it does not
authorize implementation or file edits.
