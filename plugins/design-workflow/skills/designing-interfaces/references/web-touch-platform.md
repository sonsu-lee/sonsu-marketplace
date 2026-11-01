# Web on touch devices

Read this when a web interface will be used on phones or tablets. These are
browser behaviors, not taste; check current browser support before relying on
a specific detail.

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

Desktop device emulation does not reproduce sticky hover, tap delay,
rubber-banding, safe areas or the on-screen keyboard; simulators cover more
but not touch feel. Say which behavior was checked on a real device and which
only from code.

Adapted from Emil Kowalski's
[`mobile-native`](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/mobile-native)
skill (MIT).
