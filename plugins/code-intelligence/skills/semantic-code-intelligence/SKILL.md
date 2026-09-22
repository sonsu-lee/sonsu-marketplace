---
name: semantic-code-intelligence
description: Definition, references, hover/type, implementation, diagnostics, code action 또는 symbol rename처럼 text search가 callsite나 type relation을 놓칠 요청에만 사용한다. 일반 구현·파일 탐색·formatting에는 사용하지 않는다.
---

# semantic-code-intelligence

compiler와 language server가 아는 symbol/type 관계가 필요한 요청만 처리한다. 일반 파일 탐색,
문자열 검색, 구현 lifecycle이나 formatting을 가로채지 않는다. semantic 결과가 필요한데 matching
client가 없으면 grep 결과를 의미론으로 가장하지 않는다.

## Trust와 workspace boundary

언어 server는 read 요청에서도 build script, proc macro, compiler plugin과 project config를 실행할
수 있다. 이 pack은 language server를 sandbox에 가둔다고 주장하지 않는다.

1. session 시작 cwd를 symlink-resolved canonical directory로 고정한다.
2. 모든 target을 canonical path로 resolve하고 Python `Path.relative_to(workspace)`와 같은 의미로
   target이 workspace와 같거나 descendant인지 확인한다. 문자열 prefix 비교를 쓰지 않는다.
3. root 밖 target, root 밖으로 해석되는 symlink, 복수 외부 root 요청은 semantic tool/server를
   호출하기 전에 `blocked: outside-workspace`로 끝낸다.
4. current workspace가 trusted라는 host signal을 확인한다. Codex에서는 trusted workspace의
   project-scope 설치를 권장한다. user-scope enable은 이후 여는 모든 workspace에도 host가 bundled
   MCP를 초기화할 수 있음을 알린다. OMP native LSP 호출 전에 host trust signal이 없으면 build
   script, proc macro, compiler plugin과 project config 실행 가능성을 설명하고 사용자의 명시 확인을
   받은 뒤에만 호출한다. 확인되지 않은 workspace에서는 semantic tool을 호출하지 않고 `blocked`로
   끝낸다.

workspace를 바꾼 뒤에는 Codex MCP reconnect 또는 session restart가 필요하다.

## Host 선택

현재 host가 실제 노출한 native `lsp` tool이 있으면 그것만 사용한다. OMP에서는 native `lsp`와
built-in server detection이 유일한 실행면이며 mcpls process를 시작하거나 별도 `.lsp.json`을 찾지
않는다. native `lsp`가 없고 현재 host가 `lsp_*` MCP tools를 실제 노출했을 때만 그 bridge를 쓴다.

server/language 선택은 host 또는 mcpls의 built-in language ID, file pattern, project marker와 PATH
routing에 맡긴다. 이 pack은 별도 marker, root priority나 language server installer를 만들지 않는다.
matching client가 없거나 host가 ambiguity/error를 반환하면 text search fallback 없이 발견한 host,
file language, tool/client 상태와 필요한 executable/config prerequisite를 보고하고 `blocked`로 끝낸다.

## 요청별 action

기본은 read-only semantic query다.

- definition → native `lsp` definition 또는 exposed `lsp_get_definition`
- references → native `lsp` references 또는 exposed `lsp_get_references`; declaration 포함 여부를 결과에서 구분
- hover/type → hover 또는 type definition
- implementation → implementation
- diagnostics → 현재 document/workspace diagnostics
- code action → 사용자가 변경을 요청한 경우에만 host preview와 approval 뒤 적용
- symbol rename → 사용자가 변경을 요청한 경우에만 semantic rename preview, 전체 callsite 검토와
  현재 approval policy 뒤 적용

rename과 code action을 plain text replace로 대체하지 않는다. 사용자가 변경을 요청하지 않은
read-only 질문에서 write-tier `rename`, `rename_file`, `code_actions`, raw `request`나 `reload`를
호출하지 않는다. 변경 action은 host가 보여 주는 edit 범위를 preview하고 workspace 밖 edit,
생성 file, dependency/config mutation이 있으면 승인 없이 적용하지 않는다.

## Logs와 observability

pack은 log file, telemetry event를 직접 생성·보관·전송하지 않는다. mcpls JSON stderr는 host가
현재 설정에 따라 수집할 수 있다. `get_server_logs`/`get_server_messages`는 path, diagnostic와 source
fragment를 포함할 수 있으므로 사용자가 LSP 장애 진단을 명시적으로 요청한 경우에만 호출한다.
호출 전 결과가 현재 model/session과 host logging 또는 OTEL 경계에 들어갈 수 있음을 알린다.

Codex analytics/log/OTEL 설정과 OMP session JSONL, stats, OTLP env, logger를 감지하거나 변경하지
않는다. external export, collector access/retention/deletion은 operator opt-in과 책임이다. redaction,
fixed TTL과 hard deletion을 보장하지 않는다.

## 결과

사용한 host surface, canonical workspace, language client, query 종류, definition/reference 위치와
host가 반환한 type/diagnostic을 구분해 보고한다. server 미발견, ambiguity, outside-workspace와 trust
미확인은 각각 정확한 blocker와 prerequisite를 적는다. text search로 semantic 성공을 추정하지 않는다.
