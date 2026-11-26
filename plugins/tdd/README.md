# tdd

Confirm the test contract, then implement one behavior at a time with red-green-refactor.

## Install

Register the marketplace using the [root guide](../../README.md#install), then
run the command for your client:

```sh
omp plugin install tdd@sonsu-marketplace
codex plugin add tdd@sonsu-marketplace
claude plugin install tdd@sonsu-marketplace
```

The package has one skill and no hooks, agents, or test runner. It uses the
target project's existing checks; it does not require the development plugin.

## Usage

Ask for test-first implementation, for example:

```text
Reject an empty email on form submission. Use test-driven development.
Show me the proposed test contract and existing coverage before writing tests.
```

The [test-driven-development skill](skills/test-driven-development/SKILL.md)
proposes a concrete, caller-visible example, explains the expected result and
which failure matters, then identifies the smallest suitable check. Approve the
contract in the plan or directly in chat. Once implementation is authorized,
the agent reuses or extends existing coverage rather than duplicating it. Only
a changed interface or expected behavior needs fresh confirmation. A blocked
test or a test never observed failing is not evidence of red-green-refactor.

### CLI

```text
omp:         Read skill://test-driven-development and apply it to this change.
Codex:       $tdd:test-driven-development
Claude Code: /tdd:test-driven-development
```

These are session prompts. The skill does not bypass client permission checks,
sandboxing, assigned verification roles, or limits on reproducing failures.

## Contributing

Pull requests are welcome. Ask questions in
[GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) and
follow the [contributor guide](../../CONTRIBUTING.md).

## License

[MIT](../../LICENSE) © sonsu-lee. The adapted Superpowers skill and supporting
text are MIT © Jesse Vincent. See the [source revision](SOURCES.md) and
[full upstream notice](THIRD-PARTY-LICENSES).
