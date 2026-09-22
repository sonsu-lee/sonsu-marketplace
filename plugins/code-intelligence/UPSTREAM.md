# Code Intelligence upstream

## Runtime dependency

`mcpls` is not redistributed by this package. Codex users must install exact release `0.6.0` separately.
The reviewed source is [`bug-ops/mcpls`](https://github.com/bug-ops/mcpls) commit
`6b06d1af30292b71d2e4af05928cfb3bcd9856b1`, licensed under MIT OR Apache-2.0. The launcher accepts
only `mcpls 0.6.0` from PATH and never downloads a binary or language server.

The package config changes only the MCP tool prefix and workspace root selection. mcpls built-in language
mappings, server heuristics, file patterns and project markers remain authoritative. A compatible language
server must also be installed on PATH.

## Excluded alternatives

- Serena: upstream prohibits marketplace/MCP installation and its memory/editing workflow overlaps the host.
- agent-lsp: its daemon and 65-tool workflow operating system exceeds the thin-pack boundary.
- mcp-language-server: beta status, per-language manual process configuration and lower maintenance activity
  make it unsuitable for this catalog contract.

These projects are not redistributed and no text, code or template was copied from them.
