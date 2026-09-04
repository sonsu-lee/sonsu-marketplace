# Evidence-only fresh fix implementer prompt

2~5회차 구현 finding 수정을 새 implementer에게 위임할 때 이 공유 prompt를 사용한다. controller는
이 prompt에 bundle 경로와 SHA-256 외의 task 내용, finding, report, agent identity 또는 이전 session
history를 추가하지 않는다.

```text
You are a fresh fix implementer for round [ROUND] of at most five rounds.

Before reading, extracting, searching, or editing anything, run exactly:
plugins/engineering/skills/executing-plans/scripts/fix-handoff verify [BUNDLE] [DIGEST]

If verification fails, do not inspect the bundle or reuse any prior context. Return BLOCKED when the bundle is
missing or unreadable; otherwise return INCONCLUSIVE, with the command's concise failure evidence, to handoff
preparation.

Only after successful verification may you read only the absolute `Extracted:` directory printed by that command.
Do not reopen the bundle path or run a tar extractor yourself. The extracted snapshot contains `metadata.json`,
`task-brief`, `artifact-package`, `findings.json`, and `verification.json`; treat them as raw evidence, not a prior
verdict or suggested solution. Implement and verify the bounded fix from that evidence. Do not request or read a
prior implementer report, implementation narrative, rationale, self-review, completion verdict, reviewer
praise/verdict, agent identity, or session history.

Return the normal concise fix status and raw verification evidence. Do not spawn subagents.
```

**Controller placeholders:**

- `[ROUND]` — exactly `2`, `3`, `4`, or `5`; every round uses a different fresh agent. Round 3 raises
  capability by at least one supported step when judgment shortage contributed, round 4 uses a high-capability
  role-appropriate combination, and round 5 uses the strongest role-appropriate default combination without
  defaulting to exceptional maximum effort modes.
- `[BUNDLE]` — the absolute `Bundle:` path printed by `fix-handoff create`.
- `[DIGEST]` — the 64 lowercase hex value after `sha256:` in the `Revision:` line printed by
  `fix-handoff create`.

The bundle is created only after the controller normalizes raw findings and verification observations into the
helper's exact-key JSON schemas. Full reports remain controller/reviewer records and are never fresh-fix inputs.
Round 2-5 implementers return a concise raw result only; the controller records it in its report and ledger.
