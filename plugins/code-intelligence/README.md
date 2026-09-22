# Code Intelligence

신뢰된 단일 workspace에서 semantic LSP 요청만 제공하는 `1.0.0` AVAILABLE capability pack이다.
자동 설치·enable하지 않는다. 언어 server는 read 요청에서도 build script, proc macro, compiler plugin
또는 project config를 실행할 수 있으므로 설치/enable은 현재 workspace를 신뢰한다는 사용자 승인이다.
별도 sandbox를 제공한다고 주장하지 않는다.

## Prerequisites

- OMP: host-native `lsp` capability와 대상 언어 server
- Codex: PATH의 exact `mcpls 0.6.0`과 대상 언어 server

둘 중 필요한 executable이 없거나 matching client가 없으면 grep fallback이나 추정 결과를 만들지
않고 `blocked`로 끝낸다. plugin은 downloader, shell bootstrap, `curl | sh`, package-manager command를
실행하지 않는다. Codex는 trusted workspace의 project scope 설치를 권장한다. user-scope enable은
이후 여는 모든 workspace에도 language-server 실행 권한이 이어질 수 있다.

Codex manifest만 non-autodiscovered `codex-mcp.json`을 참조한다. launcher는 session cwd를 그대로
상속하고 canonical directory인지 확인한 뒤 plugin-owned config와
`MCPLS_TRUST_PROJECT_CONFIG=false`, `MCPLS_LOG=warn`, `MCPLS_LOG_JSON=true`를 강제한다. project의
`mcpls.toml`을 신뢰하지 않는다. `[workspace] roots=[]`는 process 시작 cwd 하나를 canonical root로
사용하며 하위 project marker routing은 mcpls built-in heuristics가 담당한다.

OMP catalog에는 `mcpServers`, `lspServers`와 package `.lsp.json`이 없다. native `lsp`가 있으면
공통 skill은 항상 그것을 우선한다. workspace를 바꾼 뒤에는 MCP reconnect 또는 session restart가
필요하다. canonical session cwd 밖 target, 밖으로 향하는 symlink와 복수 외부 root는 tool 호출 전
`blocked: outside-workspace`가 된다.

## Privacy and operations

pack은 log file이나 telemetry를 직접 만들거나 보관·전송하지 않는다. mcpls JSON stderr는 host가
수집할 수 있다. server log/message는 path, diagnostic와 source fragment를 포함할 수 있어 사용자가
LSP 장애 진단을 직접 요청한 때만 호출하고 host/model logging 경계를 먼저 알린다.

기본 운영값은 raw prompt export off, OTEL endpoint unset이다. plugin은 Codex의
`analytics.enabled`, `log_dir`, `otel.exporter`, `otel.log_user_prompt`나 OMP session JSONL,
`omp stats`, OTLP env, `pi.logger`를 변경하지 않는다. 외부 export는 operator opt-in이고 collector의
access, retention, deletion은 operator 책임이다. 삭제가 필요하면 host session/log와 collector에서
각각 수행해야 하며 이 pack은 redaction, fixed TTL이나 hard erasure를 보장하지 않는다.

## Verification

```bash
python3 -m json.tool plugins/code-intelligence/codex-mcp.json
python3 -B -m unittest discover -s plugins/code-intelligence/tests -p 'test_*.py' -v
```

mcpls는 재배포하지 않는 runtime dependency다. 출처와 license는 [UPSTREAM.md](UPSTREAM.md)와
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)를 확인한다.
