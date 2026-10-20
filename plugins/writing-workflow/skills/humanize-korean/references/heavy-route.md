# Heavy route

Read when the selected route is heavy: strict or precision requests, a second
pass, selected category, requested paragraph, intensity change, new genre, or
`route_hint` recommending it (long text). Use the `SKILL_ROOT`, `RUN_DIR`, and
`GENRE` from the main skill. Chunk and reassembly mechanics are in
[runtime details](runtime.md#chunking-and-reassembly).

Follow-up passes start a new run whose `01_input.txt` is the selected latest
text, using this route; never overwrite an older run. Limit automatic editorial
rounds to three, then recommend review.

1. Diagnose exactly as in the standard route, creating `02_diagnosis.md`, then
   request the deterministic chunker:

   ```bash
   python3 "$SKILL_ROOT/scripts/prepare_monolith_input.py" \
     --run-dir "$RUN_DIR" --genre "$GENRE" --no-sanitize \
     --diagnosis "$RUN_DIR/02_diagnosis.md" --chunk
   ```

2. Read `chunk_manifest.json`. Use each body entry's exact `input_file` and
   `rewritten_file`; skip passthrough entries. Edit body chunks with
   [the editing role](roles/monolith.md), without summaries or invented
   introductions/conclusions. Do not alter code even if a chunk boundary cuts a
   fenced block; inspect the whole original to identify protected spans. One
   body chunk still follows this procedure.
3. Once every body output exists, always reassemble, even for a single chunk:

   ```bash
   python3 "$SKILL_ROOT/scripts/reassemble_chunks.py" \
     --run-dir "$RUN_DIR" --strict
   ```

4. After successful reassembly, copy `03_reassembled.md` to `final.md`. Report
   warnings. Reassembly restores passthrough text and checks character
   accounting; it is not a semantic or code-preservation guarantee.
5. Run the common gates, then always finalize by directly comparing original,
   candidate, and diagnosis with [the finalizer](roles/finalizer.md). The
   finalizer adds exactly one summary block because chunk outputs have none.
   Re-run the gates afterward. `hold_and_report` needs review.
