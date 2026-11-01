# Worst-case data

Read this when the reviewed design renders data: names, labels, counts, dates,
lists, images or states that come from users or a system. A design shown with
tidy sample content says nothing about the content it will actually receive.

## Find the real limits

List each rendered value with its source, type and limit. Take limits from the
validation schema, database column or API contract. If none exists, report the
value as unbounded; that is a finding. Note where the input limit and the
storage limit disagree.

## Values to try

Use realistic examples, not random strings:

- **Names:** long hyphenated names with diacritics, a one-letter name, stacked
  diacritics, CJK, right-to-left script, emoji and joined emoji, extra spaces, a
  missing name with only an email.
- **Identifiers:** long emails and URLs, file names, unbroken tokens such as
  UUIDs. Use `example.com`, `example.org` or `.test` domains.
- **Labels:** long titles and status text, long compound words, translated text
  that expands, many tags, empty or whitespace-only text, literal markup.
- **Numbers:** zero, one, large values, negatives, decimals, missing values and
  another locale's formatting.
- **Collections:** none, one, exactly one page and one more, a very long list,
  one item much larger than the rest, identical names.
- **Time:** just now, old, future, timezone-day boundaries, long durations.
- **Media:** missing or broken images, very wide or tall images, a transparent
  or dark logo on a dark theme.
- **States:** loading, errors with raw messages, partial data, every status at
  once, no permission, the current user in the list.
- **Environment:** the narrowest supported width, the widest, increased text
  zoom, dark theme and right-to-left layout where supported.

## Judge and report

For each break, say whether it is broken (unreadable, unreachable or wrong
data), ugly, or fragile (one realistic step from breaking). Never truncate
numbers, amounts, dates or values users compare; when other text is truncated,
there must be a way to see the full value. Say which values held up.

Distinguish observed breaks from inferred ones. Render the design when you can;
otherwise report breaks you can infer from the markup as inferred, and list
values whose effect you cannot infer as open questions. In an omp strict run, a
`web` capture can target a URL that serves a worst-case fixture, with
`assert-no-overflow` steps. Do not edit the design to produce a break.

Adapted from Emil Kowalski's
[`break-ui`](https://github.com/emilkowalski/skills/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/break-ui)
skill (MIT).
