# UI evidence

Provide visual evidence for UI changes so reviewers can understand the changed
location, appearance, and behavior without running the application. Follow any
repository evidence requirements first. This is review evidence, not a
replacement for tests or a claim that every behavior was checked.

## Select what to show

Plan the evidence before recording: the change being demonstrated, starting
state, action, and expected result. Select the smallest useful set of media.

| Change | Default evidence | Show |
| --- | --- | --- |
| Layout, style, copy, or static state | Screenshot | Location and difference |
| Input, navigation, or state transitions | Video | Start, action, and result |
| Animation, timing, or response order | Video | Trigger and actual behavior |
| Important appearance and interaction | Both | Distinct useful details |
| No observable UI or interaction change | May omit | Explain if non-obvious |

Choose based on the actual diff, not merely the file extension. Do not attach a
screenshot that only duplicates the video's final frame unless its detail is
useful. Do not require every viewport, theme, or state without relevance to the
change or repository policy. Include the conditions that expose the change.

Distinguish evidence that is unnecessary from evidence that cannot be captured,
marked, or uploaded. Report the latter as incomplete, with the missing
prerequisite. An authorized Draft may record that gap; it must not present the
evidence as complete or silently become ready for review.

## Capture the actual implementation

Run the relevant application or preview using its documented setup. Capture the
actual changed surface and scenario. Do not substitute a mockup, synthesized UI,
or fabricated before-state. Use safe test data; avoid production side effects.

For an existing UI, prefer comparable Before and After views. Match viewport,
zoom, data, theme, and starting state where possible, and label each version.
A new screen can use After only. If the old behavior cannot be reproduced, say
so and explain the difference without manufacturing a comparison.

Keep enough surrounding UI to identify the location; crop unrelated space only
when it does not hide context or a regression. Record relevant conditions in a
caption, not an exhaustive environment inventory.

## Mark every screenshot

Mark the changed area with a box, arrow, or numbered callout. Do not obscure text
or the behavior being demonstrated. When several regions matter, use numbered
markers and a short matching caption. The reviewer should not have to search
for the change or guess what a colored box means.

Use an available image annotation tool. For example, with FFmpeg installed, a
box can be added without changing the rest of the screenshot:

```sh
ffmpeg -i before.png \
  -vf 'drawbox=x=120:y=80:w=240:h=100:color=red:t=3' before-marked.png
```

The coordinates are illustrative: choose them from the actual captured image,
not from this example. Write a separate marked file so the source capture is
preserved. Inspect the resulting image at its intended display size. If the
chosen tool is unavailable, use another available tool or report the blocker;
do not silently attach an unmarked image as completed evidence. Follow the
user's installation policy rather than installing tools without authorization.

Provide descriptive image alt text and a caption identifying the change.
Marking draws attention; the caption explains its meaning.

## Make recordings understandable

Keep each recording focused on one changed flow:

1. Identify the scenario in the surrounding caption or a short opening label.
2. Show a recognizable starting state.
3. Perform the relevant action, making its target visible.
4. Hold the result long enough to understand it.

Use cursor or click highlighting, a callout, or concise on-screen text where
needed to locate the change. Do not rely on audio alone. Leave text readable
and omit irrelevant setup, logins, waiting, and unrelated navigation. Split
unrelated demonstrations rather than making one long tour.

When behavior differs, show the same Before and After scenario if feasible.
Do not speed up, splice, or otherwise edit away timing or ordering under review.
Disclose meaningful cuts or image sequences presented as video, and any limits
on the timing or ordering they establish. Captions explain what to notice,
not every click or production step. Include capture metrics only when they
affect interpretation of the evidence.

## Inspect and publish

Before uploading, open every final image and play every final video. Check:

- The capture comes from the intended revision and actually shows the change.
- Markers, captions, and important text are legible and do not hide the result.
- The recording includes the relevant trigger and outcome without misleading
  editing or unexplained state changes.
- No credentials, tokens, personal information, private notifications, or
  customer data are exposed. Prefer sanitized test data; inspect any redaction.

Use the repository template's evidence location, otherwise a dedicated area of
the PR body. Keep author-check statements concise and point to the media rather
than repeating their descriptions. If the repository requires a separate
comment, link it from the body so evidence remains discoverable.

When upload is authorized, read the
[attachment procedure](publishing.md#attach-and-verify-media).
After upload, inspect the rendered PR: images must load with their intended
placement, and recordings must play. Keep captions and evidence synchronized
with UI revisions; remove or clearly mark outdated evidence rather than leaving
it as the apparent current result. Media are review artifacts, not repository
assets to commit unless the project explicitly requires that.

## References

- [Google: reviewing functionality][google] explains why UI behavior can require
  a demonstration rather than code inspection alone.
- [GitHub CLI attachments][attachments] documents upload and rendering behavior.

[google]: https://google.github.io/eng-practices/review/reviewer/looking-for.html#functionality
[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
