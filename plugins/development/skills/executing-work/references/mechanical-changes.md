# Mechanical changes

Use this reference when an authorized change repeats one rule across many
sites, or when work continues on such a change after new edits. Completeness
should come from a repeatable query, not from rereading every file.

## Establish the scope once

Express the targets as a query you can rerun: a search pattern, a syntax-aware
rule, language-server references, or an explicit file list. Read representative
matches and every ambiguous case, then record the exclusions. Check that the
query separates targets from comments, literals, similar names, and distinct
bindings; if it cannot, use a syntax- or symbol-aware query instead.

Record the query, the exclusions, and, once coverage is proven, the verified
paths in the plan or the final report, so a continuation can reuse them. Reuse
them rather than surveying again; investigate again only when evidence changes
them, such as a new pattern or a failed check, not merely because a new turn or
stage began.

## Choose the means

Use the least machinery that applies the rule consistently:

1. **Direct edits** when sites are few or differ from each other.
2. **One invocation of an existing tool** when the pattern is uniform: a
   language-server rename, a syntax-aware rewrite, or a literal replacement
   whose pattern matches only targets. Use the parser that fits each syntax.
3. **A one-off script** only when no existing tool can express the rule.

Reuse installed tools before adding any. Do not add dependencies, tool
configuration, or helper files to the project for a one-off change. Keep a
one-off script outside the repository or run it inline, and remove it when done.
Commit a codemod only when the user asks for it or the project already keeps
codemods.

A preview permits no file changes. If an input cannot be parsed, report the file
and error; do not skip it silently or claim full coverage. When the operation
must be atomic, apply nothing until every input can be handled.

## Prove coverage

After applying, rerun the query: it should return exactly the exclusions you
recorded, which shows both that no target remains and that non-targets survive.
Confirm that the diff touches only targets and that no untracked helper files
remain. Then run the applicable checks. A clean query and diff show coverage,
not semantic correctness.

## Continue incrementally

When files change after coverage was proven, such as follow-up edits, a rebase,
or new files, narrow the scope to those changes: take them from the request,
the rebase, or untracked files not among the verified paths, and do not count
the transformation's own edits. Apply the same rule and exclusions there and
rerun the query over the full scope to confirm coverage. Do not reread files
already verified unless the change touched them.
