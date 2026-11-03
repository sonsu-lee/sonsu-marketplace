# UI evidence

Show reviewers the changed location and result without running the app.
Repository evidence requirements come first.

- **Screenshots** for appearance; **video** for interaction, transitions, or
  timing; both only when each shows something different.
- Skip evidence only when nothing visible changes, and say why if that is not
  obvious.

## Capture

1. Run the real app or documented preview at the intended revision, with safe
   test data. Never use a mockup or a fabricated before-state.
2. For an existing screen, show Before and After under the same conditions. A
   new screen can show After only.
3. Mark the changed area in each screenshot with a box, arrow, or numbered
   callout, and add alt text and a short caption.
4. For video, show the starting state, the action, and the result. Do not cut
   timing or ordering under review.

## Check and publish

1. Open every image and play every video. Confirm the revision, the change,
   and legible markers.
2. Check for credentials, tokens, personal data, and customer data.
3. Put evidence where the repository requires it, otherwise in the PR body.
   For uploads, follow [publishing](publishing.md).
4. Check the rendered PR. Update evidence when the UI changes.

## Gotchas

- A failed capture, marking, or upload does not make evidence unnecessary.
  Report what is missing; a Draft may note the gap but must not present the
  evidence as complete.
- Do not commit media just to get a URL.

## References

- [Google: reviewing functionality][google].
- [GitHub CLI attachments][attachments].

[google]: https://google.github.io/eng-practices/review/reviewer/looking-for.html#functionality
[attachments]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
