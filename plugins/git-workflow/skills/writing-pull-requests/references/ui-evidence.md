# UI evidence

Follow repository evidence requirements first. Select the smallest useful set
for the actual change: screenshots for static appearance, video for interaction,
transitions, or timing, and both when each shows something distinct. Include the
conditions needed to see the change. Evidence may be unnecessary when there is
no observable UI or interaction change; explain when that is not obvious.

A failed capture, annotation, or upload is not unnecessary evidence. Report the
missing evidence and prerequisite; an authorized Draft may record the gap but
must not present it as complete.

## Capture and mark

Run the actual application or documented preview at the intended revision.
Use safe test data and avoid production side effects. Never substitute a mockup,
synthesized UI, or fabricated before-state. For an existing UI, prefer labeled,
comparable Before and After views with matching conditions where possible. A
new screen may show After only; if the old state cannot be reproduced, say so.

Keep enough context to identify the surface. Mark each screenshot's changed
area with a box, arrow, or numbered callout without obscuring the result. Add
descriptive alt text and a concise caption explaining the marker. If marking is
unavailable, report the blocker rather than claiming completed evidence.

For video, show a recognizable starting state, the action, and the result;
identify the scenario and highlight the target when needed. Do not rely on
audio alone. Do not edit away timing or ordering under review; disclose
meaningful cuts or image sequences and limits on what they establish.

## Inspect and publish

Open every final image and play every video. Confirm the intended revision and
change, legible markers and captions, and the relevant trigger and outcome.
Inspect for credentials, tokens, personal information, private notifications,
and customer data; use sanitized data and check any redactions.

Place evidence where the repository requires it, or in the PR body; link a
required separate comment. For authorized upload, follow the
[publishing procedure](publishing.md#edge-cases). Inspect rendered placement and
playback, and report any inspection limitation. Update or mark stale evidence
when the UI changes. Do not commit media merely to obtain URLs.

## References

- [Google: reviewing functionality][google].
- [GitHub CLI attachments][attachments].

[google]: https://google.github.io/eng-practices/review/reviewer/looking-for.html#functionality
[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
