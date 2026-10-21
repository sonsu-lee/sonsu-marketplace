# Bug tickets

Read this when the ticket reports existing behavior that differs from what the
product, documentation, or an established contract promises, including a
regression.

## Describe the failure

Use the selected template's bug fields when it has them; otherwise structure
the default body's Problem section as follows. Write a field only from known
information. Collect what is unknown once, as unresolved questions in the
draft, instead of filling the body with "unknown" entries; a required template
field may state briefly what is not yet known. Remove secrets and personal
data from anything quoted or attached.

- **Summary:** state the observed failure and its condition in the title, not
  the suspected fix. "Cancelling a file copy crashes the file manager" rather
  than "Software crashes" or "Add a null check to the copy dialog".
- **Steps to reproduce:** a minimal numbered sequence from a stated starting
  state, including necessary setup, data, account role, or configuration.
  State whether the failure reproduces always, intermittently (with any known
  frequency), or not on demand. Never fabricate steps; when none are known,
  record what is known about when it occurred.
- **Actual and expected results:** what happened, quoting exact error text,
  and what should have happened. Keep observations separate from suspected
  causes.
- **Environment:** the version, build, platform, and configuration that
  matter, and whether a current version still fails. For a regression, give
  the last known good and first known bad version or change when known.
- **Evidence:** logs, traces, crash identifiers, screenshots, screen
  recordings, or a reduced test case, linked or attached rather than pasted at
  length.
- **Recording:** include a short screen recording when the failure depends on
  interaction, timing, or visual state that steps describe poorly. It
  supplements the written steps and results, which stay readable and
  searchable without playback; note when in the recording the failure appears.
  Use recordings the user or source provides, and create one only when asked.
  If a recording shows data that cannot be removed, describe what it shows or
  share it through a restricted location instead.
- **Impact:** who or what is affected, how often, and any workaround. Use this
  for priority and severity proposals without assuming every bug is urgent.

Do not merge failures on symptoms alone; similar symptoms can have different
causes, so link apparently related failures instead.

## State the desired outcome

Describe the restored behavior at the level that makes completion judgeable,
which may be broader than the single reproduction: "Saving under any role
produces one record" rather than "Step 4 no longer shows an error". Preserve
the expected result as evidence; do not let the outcome become hiding the
symptom, suppressing the error, or special-casing the reproduction input.

When the expected behavior is itself disputed, say so and name the decision
needed instead of presenting one interpretation as the contract.

## Sources

- [Mozilla Bug Writing Guidelines][mozilla]: summaries describe the problem,
  precise reproduction, expected and actual results, facts versus speculation,
  earliest affected version, and one bug per report.
- [Chromium bug reporting guidelines][chromium]: verify on a current build and
  reduce to a simplified test where possible.
- [How to Report Bugs Effectively][tatham]: intermittent failures and
  separating observation from diagnosis.

[mozilla]: https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
[chromium]: https://www.chromium.org/for-testers/bug-reporting-guidelines/
[tatham]: https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
