# Worst-case data

Use this when a reviewed design renders user- or system-supplied values,
including names, labels, counts, dates, lists, images or states.

## Gotchas

- Tidy sample content does not establish how actual content will render.
- Do not edit the design to produce a break.

## Find the real limits

List each rendered value with its source, type and limit. Take limits from the
validation schema, database column or API contract. If none exists, report the
value as unbounded; that is a finding. Note where the input limit and the
storage limit disagree.

## Values to try

Use realistic examples, not random strings:

- **Names:** long hyphenated names with diacritics, a one-letter name, stacked
  diacritics, CJK, right-to-left script, emoji and joined emoji, extra spaces, a
  missing name with only an email, a name whose spacing, word order or
  romanization differs from the record it must match in another system.
- **Identifiers:** long emails and URLs, file names, unbroken tokens such as
  UUIDs. Use `example.com`, `example.org` or `.test` domains.
- **Labels:** long titles and status text, long compound words, translated text
  that expands, many tags, empty or whitespace-only text, literal markup.
- **Numbers:** zero, one, large values, negatives, decimals, missing values,
  another locale's formatting, and values that update in place or sit in a
  column for comparison.
- **Collections:** none, one, exactly one page and one more, a very long list,
  one item much larger than the rest, identical names, and items or
  notifications the feature generates on its own, at their real frequency, next
  to what the person created.
- **Time:** just now, old, future, timezone-day boundaries, long durations.
- **Media:** missing or broken images, very wide or tall images, a transparent
  or dark logo on a dark theme, and a graphic that changes by stage, count or
  level, at its first and last stage, past any cap, and at its displayed size.
- **States:** loading, errors with raw messages, partial data, every status at
  once, no permission, the current user in the list, and repeated validation
  failures that never say what did not match, up to any attempt limit or
  lockout.
- **Environment:** the narrowest supported width, the widest, increased text
  zoom, dark theme and right-to-left layout where supported, and an OS
  notification banner or the on-screen keyboard over content being read or a
  field being filled, where either can actually appear at that moment.

## Judge and report

For each break, say whether it is broken (unreadable, unreachable or wrong
data), ugly, or fragile (one realistic step from breaking). Never truncate
numbers, amounts, dates or values users compare; when other text is truncated,
there must be a way to see the full value. When a list or menu is cut off by
its container, including at larger text sizes, check that something signals
more items beyond the edge. Where numbers are compared in a column or update in
place, digits that change width and shift alignment are a finding; confirm the
font offers tabular figures before recommending them. Say which values held up.

Report generated items that bury what the person created with the volume you
assumed; whether to change the automation is the owner's decision. For repeated
validation failures, report missing recovery; raise a missing cause as a
question where vagueness may be a security choice, and do not recommend
removing an attempt limit, which may be a security control. Inspect attempt
limits and lockout from supplied screens or an authorized fixture; never
trigger them on a real account.

Distinguish observed breaks from inferred ones. Render the design when you can;
otherwise report breaks you can infer from the markup as inferred, and list
values whose effect you cannot infer as open questions. In an omp strict run, a
`web` capture can target a URL that serves a worst-case fixture, with
`assert-no-overflow` steps.

Exercise data through the existing input boundary, with realistic or
schema-backed values. Compare empty, single-item, and large collections when
reachable. Creating fixtures or a development toggle needs appropriate
authorization; a read-only review does not permit changing the design or data.
These additions also draw from Emil Kowalski's
[`break-ui`](https://github.com/emilkowalski/skills/tree/64eb3deb9a5fbfa041faf783e0bc3fd635872e9c/skills/break-ui)
(MIT).

Adapted from Emil Kowalski's
[`break-ui`](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/break-ui)
skill (MIT).

The name-record, generated-item, overlay, staged-graphic, figure-width and
cut-off-list checks draw on these sources. They show where such values mattered
in other products' design work; they do not show that the reviewed design has
the same problem. A link marked "(session transcript)" or "(session video)"
redirects to a conference session page; the talk's transcript or its linked
video's captions were the source.

- <https://toss.tech/article/45787> — names rejected against external records,
  with repeated unexplained failures and a lockout.
- <https://toss.tech/article/27396> — an automatic option drawn at real volume
  buries the person's own transactions and multiplies notifications (session
  transcript).
- <https://toss.tech/article/platform-designer-work> — a notification banner
  can cover a guidance screen while its message arrives.
- <https://toss.tech/article/toss-signup-process> — the on-screen keyboard hides
  a field on some device sizes.
- <https://toss.tech/article/layers-of-your-time> — a stacked object must hold
  from the first to the tenth step and changes past its cap.
- <https://toss.tech/article/chipmunk> — a character changes by growth stage and
  loses clarity at its displayed size.
- <https://toss.tech/article/27358> — proportional digits make compared or live
  values hard to read (session video).
- <https://toss.tech/article/toss-design-system> — a long menu, especially with
  larger text, hid that more items existed below.
