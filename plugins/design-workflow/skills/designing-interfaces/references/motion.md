# Motion

Read this when a proposal adds, changes, reviews or removes animation.

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
  reverse it. CSS transitions retarget mid-way, keyframe animations restart.
- `prefers-reduced-motion: reduce` asks for gentler motion, not none: replace
  movement with short fades and keep changes that aid understanding. Also
  respect `prefers-reduced-transparency` and `prefers-contrast`.
- Avoid large moving backgrounds and endless loops; auto-playing motion longer
  than five seconds needs a way to pause it.

Durations and easing depend on the product's character. Follow the existing
design system; do not present one value as universally right.

## Cost

Animating `transform` and `opacity` usually avoids layout and paint; `width`,
`height`, `top`, `left`, `margin` and `padding` trigger layout. Animation
driven frame by frame from JavaScript runs on the main thread and drops frames
when the page is busy. Changing an inherited CSS variable restyles every
descendant. Confirm smoothness on a real mid-range device; a fast desktop
proves little.

## Removing motion

Check for elements whose start state is hidden until an animation runs, code
that waits for an animation to end, exits that delay unmounting, focus moved
after an animation, and tests that wait for animation classes.

Judging how motion feels needs a recording or a running build, not code alone.
For implementation detail, see Emil Kowalski's [motion skills][upstream]
(MIT), from which these points are adapted.

[upstream]: https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills
