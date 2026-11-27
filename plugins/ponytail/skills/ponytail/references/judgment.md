# Judgment calls

Read this when a lint diagnostic, a name, a guard, a test, or a repeated rule
needs a decision a linter cannot make. The project's lint configuration
decides which rules run and how severe they are; this file does not restate
it. A contract the project states overrides every default below.

Change code, or request a change in review, only when you can state all of:

1. The reachable situation: a real caller, input, or state.
2. What goes wrong there, or what the code costs today.
3. The result that is needed, not a prescribed fix.

"Less readable", "might be slow", and "may be needed later" are not reasons
by themselves. When you cannot state all three, leave the code and report
nothing.

## Lint diagnostics

- A diagnostic that fails the project's lint check, whatever its label, is a
  failed check. Fix it, or use the exception the project's policy allows.
- A warning your change caused, wherever it appears: fix it when the fix
  keeps behavior and reads better. Otherwise keep the code and give the
  reason in the change summary, such as "both comparisons express one price
  range". Do not add a disable comment or a helper only to silence it.
- A warning that existed before your change is not yours to fix.

## Unneeded tests

A test is a removal or merge candidate when deleting it leaves no reachable
contract violation undetected. Three cases:

- **The same failure twice.** `110 -> 100` and `120 -> 100` exercise one cap
  rule: keep one. `100` and `101` sit on either side of the boundary: keep
  both.
- **Implementation instead of contract.** It breaks when a private helper is
  renamed or call order changes while the result stays right. Keep it when
  the count or order is the contract, such as charging a card exactly once.
- **An invalid premise.** It runs only by forcing a value that the entry
  boundary and every caller exclude, such as `null as unknown as Order`. The
  boundary's own rejection test stays.

Tests of one story at different levels are not duplicates when they catch
different failures. A surviving mutant is a lead, not a finding: it counts
only when an agreed, reachable case changes its result and the tests still
pass.

## Type guards and boundaries

Validate an outside value once, where it enters, and pass the narrowed type
inward. Report a guard only when it re-proves a guarantee that already holds
on every path that reaches it.

- Every internal caller passes `OrderId`, but the parameter accepts
  `string | number | undefined`: narrow the parameter type. Confirm every
  caller with the language server's references before removing a branch.
- Structured `unknown` from HTTP, a file, or a message: parse it at the
  boundary with the schema library the project already uses, and derive the
  inner type from that schema. Do not add a schema dependency to replace one
  `typeof` check.
- `response.json() as Order` is an unchecked assertion. The compiler believes
  it; nothing verified it.
- A branch on a valid domain state, such as `order.status`, is a domain rule,
  not a guard.
- A second entry path, such as a batch job or a data restore, is a separate
  boundary. Guard it where it first reads the untrusted value.

When a branch is reachable only through a cast, or through a test that sets
internal state no real caller or concurrent operation produces, delete the
branch and the test that exists for it.

## Names and validation results

A caller that needs yes or no gets a question-shaped name and a `boolean` or
a type guard: `isValidEmail()`. A caller that needs the reason gets a result
object: `validateEmail()`. One public function must not return `true` on one
path and `{ ok: false }` on another: the object is truthy, so the failure
takes the success branch.

Follow a naming contract the project states. Without one, do not rename
`hasPermission` or `canRetry` to a house prefix, and do not judge a function
by its name alone. Check whether a caller can misread its result.

## Conditions and evaluation cost

Name a judgment when one expression makes the reader rebuild two different
business rules, such as purchase eligibility and payment readiness. A name
that restates the expression, such as `condition1`, is not an improvement.
Leave `price >= min && price <= max` and operands that are already named.

Extraction must keep evaluation order, count, and short-circuiting. In
`user != null && canPurchase(user)`, do not hoist the right side into a
variable that runs first. Add a function or memoization only after naming
which computation repeats, and when.

## Boolean meaning

Separate conversion, presence, and business condition. `count > 0` is a
quantity check, `enabled ?? defaultEnabled` handles an unset value, and
`result.ok` reads a validation result. Do not rewrite `isReady` as
`isReady === true`.

## Promise failures

Judge what the caller observes after a failure, not whether `.catch()`
exists. A save fails and the success notice still shows: that is the defect.
Propagating the error, returning the recovery value the contract defines, or
showing a failure state and stopping the success path all handle it. Do not
require a rethrow or a log line in every handler. A log line alone does not
handle a failure either.

## Duplication, rule ownership, and extension points

- Merge two pieces of code only when they must change for the same reason.
  The same number or shape with different reasons stays separate.
- One product rule has one owner. A cancellation deadline computed separately
  by an API and a batch job drifts. Input validation is different: each entry
  boundary validates its own input.
- An option no caller sets, a registry with one strategy, or a fallback no
  input reaches is a removal candidate when this change added it. Having one
  caller is not a reason: keep an interface that isolates complexity or
  protects an external contract today.
- Follow the module or SDK boundary the project defines, and name the public
  path to use instead. Do not invent a folder or domain boundary.
