# Runtime helpers

Read when interpreting metrics, handling long or mixed-content documents, or
resolving helper errors. These are the pinned upstream implementations, not the
Codex wrapper scripts. Invoke them with Python 3.10 or newer by absolute path
from the installed skill. Their resources are local; no third-party Python
packages, external executables, credentials, or network calls are required.

## Dependency closure

- `scripts/prepare_monolith_input.py` imports `references/metrics_v2.py`, with
  upstream fallback to `metrics.py`, and optionally `scripts/sanitize_text.py`.
  It uses `scripts/checks.py` to recognize inline footnote references and
  `scripts/console.py` for UTF-8 console handling.
- `references/metrics_v2.py` imports adjacent `metrics.py`; both read adjacent
  `baseline.json` / `baseline_v2.json` as applicable.
- `scripts/verify_gates.py` imports `scripts/checks.py`, `metrics_v2.py`, and
  `scripts/restore_modality.py`. The modality helper imports the gate's shared
  modal expressions, metric helpers, and checks; keep these files together.
- `scripts/verify_change_rate.py` imports `metrics_v2.py`, `checks.py`, and
  `console.py`. Both gates and modality restoration use the summary recognizer
  in `checks.py`.
- `scripts/reassemble_chunks.py` needs only the standard library and
  `console.py`. Its input manifest and body files live in the caller's run.
- `sanitize_text.py` and `checks.py` also use the bundled console helper when
  invoked as commands. Sanitation is disabled in the skill workflow.

Legacy implementation comments and some diagnostic labels retain upstream
Korean terminology. Rulebooks, role contracts, and generated editing guidance
are English with Korean linguistic examples. Structured JSON field names remain
upstream-compatible.

## Preparation and sanitation

`prepare_monolith_input.py --run-dir DIR --genre GENRE --no-sanitize` reads
`DIR/01_input.txt` and writes `00_metrics.json` plus
`01_input_with_metrics.txt`. With `--diagnosis PATH`, diagnosis precedes metrics.
The original prose follows the generated evidence block.

Explicit relative paths resolve from the caller's working directory, not the
installed skill. Prefer an absolute caller-owned temporary `--run-dir`.
Standalone `--text` without `--run-dir` allocates a unique OS temporary directory
and prints its path; it does not create a target-repository `_workspace`.

The upstream optional sanitizer can normalize NFD Hangul, remove invisible
characters, and normalize spaces in the stored input. That can alter code,
quotes, or terms, so the workflow always passes `--no-sanitize`. Do not run it
as detector evasion or imply that sanitation removes an AI watermark. Preserve
raw input if a separate user-authorized normalization task requires it.

Preparation preserves upstream metric-degradation behavior: an unavailable or
failed metric module produces `00_metrics.error` and combined prose without a
metric block. Inspect that error and report the missing measurements. A success
exit for preparation is not proof every metric was computed.

## Metrics and routing

The router chooses among light, standard, and heavy from length, raw pattern
counts, and the v1 risk band. Its suggestion is advisory; explicit user intensity
wins. More than 15,000 characters recommends heavy. Short text can legitimately
have too little evidence for some metrics.

The v1 baseline has essay, column, report, blog, and abstract keys. `report` is
only a measurement proxy for technical docs, not a validated technical baseline.
Neither lexical density nor necessary terminology should be edited to force a
technical document toward a prose-corpus mean.

The v2 baseline contains estimated placeholder cells. The metric JSON can contain
numeric `v2_z_scores` alongside `v2_baseline_warnings`; do not mistake those
numbers for calibrated evidence. Preparation intentionally omits them from
editing guidance. Nonzero counts still need contextual review against the
rulebook, especially inside code, quoted text, and intentionally repeated terms.

## Chunking and reassembly

`--chunk` creates `chunk_manifest.json` with original offsets, source hash,
body/passthrough entries, and exact input/output filenames. The upstream target
is 7,000 characters, with a 9,000-character maximum before boundary handling.
Boundaries prefer headings and paragraph breaks, then sentence boundaries for
oversized paragraphs. Short inputs can produce an advisory chunk warning;
heavy still follows its manifest/reassembly procedure.

Read the manifest rather than deriving filenames. Passthrough entries are
restored from the original. Body outputs contain only revised text, not summaries
or newly invented boundary transitions. Reassembly is mandatory even with one
body chunk and can handle no-body/passthrough cases without inventing text.

Numbered lines such as `1) ...` and `[1] ...` remain editable procedure prose
unless an inline citation references them. Only referenced trailing definitions
become footnote passthrough; numbered runbooks are not exempt from editing.
Preparation and fidelity checks share recognition of `N)` and `[N]` citations.
Markdown links and code examples do not turn numbered prose into definitions.

The chunker is not a Markdown or programming-language parser. It does not
protect every code block or detect executable directives. Before editing any
chunk, use the complete original to identify protected spans, including a fence
or quotation that crosses its boundary. Preserve these verbatim. Final review
must compare them directly; reassembly's hash and character accounting do not
prove code or semantic preservation.

Re-running `--chunk` removes stale chunk inputs, outputs, and reassembly artifacts
in that run. Create a new run for a new editorial round rather than re-chunking
a completed run whose artifacts must be retained.

`reassemble_chunks.py --run-dir DIR --strict` checks source hash, manifest
coverage, required body files, and character-accounting warnings, then writes
`03_reassembled.md` and `03_reassembly_report.json`. A nonzero result is not a
successful reassembly. Resolve its cause before copying the result to `final.md`.

## Gate interpretation

The gate prints readable diagnostics and, with `--json`, a JSON object after
them. Its stdout is not a JSON-only stream. Capture output with the caller's tool
if needed; do not feed all stdout directly to a JSON decoder.

- **P0:** Character change rate, computed as `1 - SequenceMatcher.ratio()` with
  `autojunk=False`, not Levenshtein distance. At least 0.30 warns; at least 0.50
  blocks acceptance. Only a complete terminal `HUMANIZE-SUMMARY` comment in the
  [editing-role format](roles/monolith.md#summary-format), outside code examples,
  is excluded. Inline, earlier, or malformed markers remain document content.
- **P1:** Selected v1 target z-scores and possible overcorrection. Metric failure
  can leave this axis unjudged rather than failing the whole command. Inspect
  stderr and disclose an unavailable axis; do not call it a complete pass.
- **P2:** Antithesis annihilation: at least five original matches reduced to zero
  warns. This is not a requirement to preserve every repeated formula.
- **P3:** Known preservation checks for register, heading independence, footnotes,
  quotes, and introduced numbers. These are heuristics, not exhaustive fidelity.
  Numeric checks retain signs and normalize grouping, decimals, and single
  Korean magnitude suffixes (`1만` equals `10,000`). They compare value sets,
  not quantities: unit-only changes such as `5 ms` to `5 s` or `10%` to `10건`,
  reassigned values, and compound numeric expressions require direct semantic
  comparison. Do not infer unit preservation from a passing gate.
- **P4:** Sentence touch rate and dropped numbers are observations only and do
  not themselves affect exit status. Review dropped numbers even on exit 0.
- **P5:** Sentence-pair modality loss. Confident losses can warn; uncertain
  low-similarity pairs remain observations that still require human judgment.

Exit 0 is measured convergence, 1 warns and requires finalization, 2 blocks
acceptance, and 3 indicates an explicit file/read error. An unhandled exception
is also an execution failure, whatever its status; never confuse it with an
editorial warning or bypass the checks. The gates do not comprehensively check
code, identifiers, commands, URLs, semantic entailment, or all dropped facts.
Direct finalizer comparison remains necessary.

`--ignore-markup` cross-measures P0 after stripping selected formatting. It does
not exclude all code content or validate technical syntax. Report both rates
when using it, and never use it to hide a factual or code change.

`verify_change_rate.py --before PATH --after PATH` provides the standalone P0
measurement; use `--ignore-markup` only for the same disclosed cross-check.
`restore_modality.py` is retained because P5 imports its sentence alignment;
the workflow does not invoke its automatic rewriting command. Restore lost
meaning through the finalizer's contextual comparison instead.
