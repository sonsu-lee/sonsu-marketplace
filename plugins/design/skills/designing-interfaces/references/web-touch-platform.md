# Web on touch devices

Use this for web interfaces on phones or tablets. Check current browser support
before relying on a specific behavior.

## Platform behavior

- **Hover sticks on touch.** A tap applies `:hover` and it stays. Put hover-only
  effects inside `@media (hover: hover) and (pointer: fine)`, give touch users
  press feedback with `:active`, and never hide an action behind hover alone.
  Gate by capability, not device: tablets with trackpads and touch laptops mix
  both.
- **`100vh` is the largest viewport.** It overflows while browser bars are
  visible. Use `dvh` for an app shell that follows the visible area and `svh`
  for content that must fit the smallest one.
- **Small inputs zoom the page.** iOS Safari zooms when focusing an input whose
  font size is under 16px. Size the input; never disable zoom with
  `user-scalable=no` or `maximum-scale=1`, which is an accessibility failure.
- **Safe areas need `viewport-fit=cover`.** Without it, `env(safe-area-inset-*)`
  is zero. Give `env()` a fallback.
- **Scroll chaining.** `overscroll-behavior: contain` on a sheet's or modal's
  scrolling content stops its scroll from passing to the page; it does not
  lock the page while the sheet is open. `none` on the page also removes
  pull-to-refresh.
- **`touch-action` names what the browser may still do.** A horizontal carousel
  keeps `pan-y`; use `none` only when the element handles every gesture. Prefer
  native scroll snapping to hand-built carousels.
- **Keyboards.** Choose `type` and `inputmode` for the right keyboard,
  `enterkeyhint` for the return key, and disable autocapitalize and
  autocorrect for codes and emails.
- **Browser color.** Where the browser honors `theme-color`, set it per color
  scheme to match the top of the page. Some browsers derive the tint from the
  page background instead.
- **Media with sound waits for a gesture.** Browsers generally refuse to start
  video or audio with sound until the person has interacted with the page, and
  the details vary by browser and setting. Muted or silent video may autoplay,
  but unmuting without a gesture can pause it, and settings can block even
  silent autoplay. When an experience depends on playback, design a
  tap-to-start state and show it when `play()` rejects with `NotAllowedError`;
  a source the browser cannot play needs an error state or alternative content
  instead. Do not try to route around the policy.

Match each intervention to an observed need. Preserve text selection where
content must be copied and retain clear press feedback if changing tap
highlights. Respect zoom and keyboard behavior. Recheck on actual hardware
when available instead of treating desktop emulation as device evidence.
These additions also draw from Emil Kowalski's
[`mobile-native`](https://github.com/emilkowalski/skills/tree/64eb3deb9a5fbfa041faf783e0bc3fd635872e9c/skills/mobile-native)
(MIT).

The media item follows WebKit's
[iOS video policies](https://webkit.org/blog/6784/new-video-policies-for-ios/)
and
[autoplay policy changes](https://webkit.org/blog/7734/auto-play-policy-changes-for-macos/),
MDN's
[autoplay guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay)
and a
[conference site's mobile build](https://toss.tech/article/simplicity4-frontend-engineering),
which added a tap-to-start control where playback was refused.

## Gotchas

Desktop emulation does not reproduce sticky hover, tap delay, rubber-banding,
safe areas or the on-screen keyboard; simulators cover more but not touch feel.
Report what was checked on a real device and what was checked only from code.

Adapted from Emil Kowalski's
[`mobile-native`](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/mobile-native)
skill (MIT).
