# Implementation plan template

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

## For approval

**Approach:** [What changes and why this way, in two or three sentences]

**You will see:** [One sentence per changed behavior: in this situation, this
action gives this result. Cite the PRD's case when it already states it.]

**Needs your decision:** [A choice that changes behavior, scope, or a
material risk, with what each answer changes; or "None"]

Approving this section approves the test specification. Everything below is
for the executor: file names, test levels, and commands are implementation
choices.

> **For the executing controller:** REQUIRED SUB-SKILL: Use development:executing-work
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Spec:** [path to the spec/design doc or approved design from chat — the plan
argues from the spec, so the spec travels with it; executors read both]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

## Review Focus

[Up to five reachable input classes or failure modes the spec implies but no task's
tests exercise that are most likely to bite a person using this software
— one line each, naming the input or condition and the behavior a
reasonable person would expect, most likely first. The spec is a vision
document: it says what the software must do, not everything it will
meet, and its silence on an input is not permission for that input to
break the program. Write the list here, once, with the spec in front of
you. Then, for each line, add the test that pins it to the task that
owns the code, in that task's own step style.]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Modify: `src/cart.py`
- Test: `tests/cart/test_cart.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

**Test specification:**
- Observable interface: `quantity_for(sku: str) -> int` on the cart.
- Initial state and action: a cart has two units of `tea`; add one more.
- Expected result and basis: `quantity_for("tea") == 3`; the design says
  adding the same SKU increments its quantity.
- Failure caught: replacing the old quantity instead of adding to it.
- Test type and reuse: focused unit test at the public cart interface.
  Name an existing test if it already catches this failure; otherwise add
  the example below.

- [ ] **Step 1: Write the failing test after specification approval**

```python
def test_adding_same_sku_increments_quantity():
    cart = Cart()
    cart.add("tea", quantity=2)
    cart.add("tea", quantity=1)
    assert cart.quantity_for("tea") == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/cart/test_cart.py::test_adding_same_sku_increments_quantity -v`
Expected: FAIL for the missing behavior, e.g. actual quantity 1 rather than 3.

- [ ] **Step 3: Implement `Cart.add(self, sku: str, quantity: int) -> None` in `src/cart.py`**

One line on the approach when the signature and the test leave a choice
(which library call, which data structure); a code block only for an
algorithm they do not determine.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/cart/test_cart.py::test_adding_same_sku_increments_quantity -v`
Expected: PASS

- [ ] **Step 5: Refactor while green; rerun this check and the affected
  callers’ checks.**
````
