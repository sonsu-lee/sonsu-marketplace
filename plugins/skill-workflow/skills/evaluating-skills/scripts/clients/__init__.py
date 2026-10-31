"""Client adapters for omp and Codex."""

from __future__ import annotations

from scripts.clients.codex import CodexClient
from scripts.clients.omp import OmpClient


def get_client(name: str):
    if name == "claude":
        raise ValueError("Claude Code uses Anthropic's skill-creator plugin; "
                         "evaluating-skills runs omp and Codex only")
    clients = {"omp": OmpClient(), "codex": CodexClient()}
    if name not in clients:
        raise ValueError(f"unknown client {name!r}; choose omp or codex")
    return clients[name]
