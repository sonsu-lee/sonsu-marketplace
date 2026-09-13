# Review target

The current change adds an external webhook adapter, an internal dispatcher, a provider-backed
execution path, and a v3 client. Review the files in this fixture as the complete change.

Contracts:

- `receiveWebhook` is the only untrusted JSON boundary. It must reject unsupported `kind`, an empty
  `accountId`, and non-object input before producing `TrustedWebhook`.
- `dispatch` only accepts `TrustedWebhook`; every caller gets the value from `receiveWebhook`.
  Repeating shape validation in `dispatch` is outside the requested design.
- `runWithProvider` must close every successfully opened session after `execute` succeeds or fails.
  A failure to open creates no session to close.
- `docs/provider-api-v2-snapshot.md` is an immutable historical source snapshot. Current v3 behavior
  belongs in code and current contract docs; a code change does not rewrite this snapshot.
- No production incident, traffic volume, or deployed provider version is supplied by this fixture.
