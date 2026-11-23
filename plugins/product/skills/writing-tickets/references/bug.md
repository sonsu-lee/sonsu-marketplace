# Bug tickets

Read this when existing behavior differs from the product, documentation, or an
established contract, including regressions.

## Workflow

1. **Describe the failure.** Use the selected template's bug fields, or the
   default body's Problem section if none exist. Write only known information;
   collect unknowns once as unresolved questions in the draft. A required
   template field may briefly state what is not yet known. Remove secrets and
   personal data from anything quoted or attached.
   - **Summary:** Put the observed failure and condition in the title, not a
     suspected fix.
   - **Steps:** Give a minimal numbered sequence from a stated starting state,
     including necessary setup, data, account role, and configuration. State
     whether it always reproduces, is intermittent (with known frequency), or
     cannot be reproduced on demand. Never fabricate steps; if none are known,
     record what is known about when it occurred.
   - **Actual and expected:** Quote exact error text and state what happened and
     what should have happened. Separate observation from suspected cause.
   - **Environment:** Include relevant version, build, platform, configuration,
     and whether a current version still fails. For regressions, give the last
     known good and first known bad version or change when known.
   - **Evidence:** Link or attach logs, traces, crash identifiers, screenshots,
     recordings, or a reduced test case rather than pasting them at length.
   - **Impact:** State who or what is affected, frequency, and any workaround;
     use these for priority and severity proposals.
2. **State the desired outcome.** Describe restored behavior at a judgeable
   level, potentially broader than one reproduction. Preserve the expected
   result as evidence. If expected behavior is disputed, say so and name the
   decision needed rather than treating one interpretation as the contract.
3. **Add a recording when useful.** For failures dependent on interaction,
   timing, or visual state that steps describe poorly, include a short screen
   recording and note when the failure appears. Use a recording supplied by the
   user or source; create one only when asked. If data in it cannot be removed,
   describe what it shows or share it through a restricted location instead.

## Gotchas

- Recordings supplement written steps and results; those must remain readable
  and searchable without playback.
- Do not make the outcome hiding the symptom, suppressing the error, or
  special-casing the reproduction input.
- Similar symptoms can have different causes: link apparently related failures
  rather than merging them on symptoms alone. Not every bug is urgent.

## Sources

- [Mozilla Bug Writing Guidelines][mozilla]: summaries, reproduction, results,
  facts versus speculation, affected versions, and one bug per report.
- [Chromium bug reporting guidelines][chromium]: current builds and reduced tests.
- [How to Report Bugs Effectively][tatham]: intermittent failures and separating
  observation from diagnosis.

[mozilla]: https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
[chromium]: https://www.chromium.org/for-testers/bug-reporting-guidelines/
[tatham]: https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
