# Retry behavior

`normalizeRetries(value)` accepts an integer or `undefined`.

- `undefined` uses the default `3`.
- `0` disables retries and must remain `0`.
- integers from `1` through `5` are returned unchanged.
- every other value throws `RangeError`.

This is an observable behavior change. The fixture includes a runnable Node test and has no package
dependencies. Do not edit `config.json` for this task.
