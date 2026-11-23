# Motion

Use this when a proposal adds, changes, reviews or removes animation.

## Decide whether to animate

1. **Frequency.** The more often people see it, the less it should move.
   Keyboard-initiated and many-times-a-day actions should respond immediately.
2. **Purpose.** Name it: feedback, keeping spatial position, showing a state
   change, explaining, or avoiding an abrupt change. If you cannot name one,
   do not animate.
3. **Function.** Data people are reading or acting on should not move for
   style.

No animation is a valid outcome. When proposing motion, list what you chose
not to animate and why.

## Behavior

- Motion starts where its cause is: a popover grows from its trigger, and an
  element leaves the way it entered.
- Never block input during a transition; people must be able to interrupt or
  reverse it.
- `prefers-reduced-motion: reduce` asks for gentler motion, not none: replace
  movement with short fades and keep changes that aid understanding. Also
  respect `prefers-reduced-transparency` and `prefers-contrast`.
- Avoid large moving backgrounds and endless loops; auto-playing motion longer
  than five seconds needs a way to pause it.

Durations and easing depend on the product's character. Follow the existing
design system; do not present one value as universally right.

For an authorized implementation, choose the least costly suitable mechanism:
CSS transitions for reversible state changes, CSS animation for predetermined
motion, or a programmatic tool when the interaction genuinely requires it.
Reuse existing motion tokens. Review trigger origin, interruption, exits, input
capabilities and the reduced-motion result in the actual interface. A review
alone does not authorize changing the animation.

Additional adaptations: Emil Kowalski's
[`animate`](https://github.com/emilkowalski/skills/tree/64eb3deb9a5fbfa041faf783e0bc3fd635872e9c/skills/animate)
and [`review-animations`](https://github.com/emilkowalski/skills/tree/64eb3deb9a5fbfa041faf783e0bc3fd635872e9c/skills/review-animations)
(MIT). Product needs and accessibility requirements override fixed values.

## Cost

Animating `transform` and `opacity` usually avoids layout and paint; `width`,
`height`, `top`, `left`, `margin` and `padding` trigger layout. Animation
driven frame by frame from JavaScript runs on the main thread and drops frames
when the page is busy. Changing an inherited CSS variable restyles every
descendant. Confirm smoothness on a real mid-range device; a fast desktop
proves little.

Blur combines many neighboring pixels for each output pixel, so its cost grows
with the blurred area and radius, and animating it repeats that work every
frame. Engines differ: check blur in each target browser on real hardware and
name a cheaper treatment with a similar impression, such as reduced opacity or
a pre-blurred image, for engines where it stutters. Sources: Chrome's
[animated blur note](https://developer.chrome.com/blog/animated-blur) and a
[conference site](https://toss.tech/article/simplicity4-frontend-engineering)
that found blur slow in Safari and lowered a background's opacity there.

## Removing motion

Check for elements whose start state is hidden until an animation runs, code
that waits for an animation to end, exits that delay unmounting, focus moved
after an animation, and tests that wait for animation classes.

## Gotchas

- Judging how motion feels needs a recording or running build, not code alone.
- CSS transitions retarget mid-way; keyframe animations restart.

For implementation detail, see Emil Kowalski's [motion skills][upstream]
(MIT), from which these points are adapted.

[upstream]: https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills
