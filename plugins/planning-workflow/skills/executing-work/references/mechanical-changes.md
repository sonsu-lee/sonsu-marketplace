# Mechanical changes

Use this reference when an authorized change repeats across files or needs a
syntax-aware transformation. A small, isolated edit does not require a bulk
workflow.

1. Establish the approved targets and exact transformation before writing.
   Enumerate candidates across the approved scope and classify their patterns.
   Inspect representative matches, callers, and ambiguous exceptions rather
   than assume one example covers every file. Preview permits no mutation.
   Existing approval for this bulk scope does not need to be repeated.
2. Choose a tool suited to the actual structure. Use a batch-capable tool for
   repetitive changes across files, and syntax- or symbol-aware operations when
   text replacement would alter comments, literals, similar names, or distinct
   bindings. Handle different file syntaxes with their appropriate parsers.
   Do not claim a bulk transform was validated if only individual edits ran.
   Reuse installed project tools and versions before adding a dependency.
3. Preview or otherwise inspect the proposed match set and exclusions before
   applying it. If parsing fails, report the file and error; do not silently
   skip it or claim complete coverage. Preserve unrelated changes and avoid
   applying a partial result when the requested operation must be atomic.
4. Apply only the authorized transformation. Inspect the result and run the
   applicable authorized checks against the final revision, including tests
   for behavior and exclusions. Report actual coverage and failures; a clean
   parse or successful command alone does not establish semantic correctness.
