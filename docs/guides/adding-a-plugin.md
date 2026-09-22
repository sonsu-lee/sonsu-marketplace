# 플러그인 개발·수정·추가하기

Sonsu Marketplace의 얇은 capability pack을 로컬에서 수정하고 검증하는 절차입니다. 현재 구조는
[아키텍처](../architecture/overview.md), field 계약은 [manifest 참조](../reference/plugin-manifest.md),
외부 원본 업데이트는 [upstream runbook](../runbooks/updating-upstream-plugin.md)을 참고합니다.

## 먼저 확인할 것

1. 요청이 host baseline으로 이미 해결되는지 확인합니다. 일반 구현·debugging·test·Git·웹 조사·문장
   교정·memory·continuity를 plugin으로 다시 만들지 않습니다.
2. domain judgment 또는 external artifact boundary가 독립 package를 정당화하는지 확인합니다.
3. 이름, exact upstream commit/runtime version, 포함 범위와 license를 확인합니다.
4. 다른 plugin 설치, router, setup skill, hook 또는 fixed model roster 없이 동작하도록 설계합니다.

## 로컬 등록

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
# 또는
omp plugin marketplace add .
```

기존 사용자 설정과 분리한 disposable HOME/profile에서 실제 등록·설치 probe를 수행합니다.

## Package 구조

```text
plugins/<name>/
  .codex-plugin/plugin.json
  README.md
  skills/<skill>/SKILL.md
  UPSTREAM.md                 # 외부 source/runtime/consulted material이 있을 때
```

공통 skill은 두 host에서 읽을 수 있어야 합니다. Codex-only `apps`/`mcpServers`는 manifest에만 선언하고
OMP catalog로 투영하지 않습니다. secret, user-specific absolute path, network installer와 unsafe trust
bypass를 package config에 넣지 않습니다.

외부 파일을 포함하면 source path, exact commit, 최종 path와 license를 기록합니다. 아이디어만 참고하면
`consulted-only`로 표시하고 재배포 license를 주장하지 않습니다. 실행 파일 dependency는 자동 download
대신 exact version guard와 deterministic failure를 제공합니다.

## Catalog 등록

`.agents/plugins/marketplace.json`에는 root-relative `./plugins/<name>`,
`.omp-plugin/marketplace.json`에는 `metadata.pluginRoot`-relative `./<name>`을 등록합니다. folder, 두 entry,
manifest의 이름과 version이 일치해야 합니다.

```json
{
  "name": "my-plugin",
  "source": { "source": "local", "path": "./plugins/my-plugin" },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Productivity"
}
```

```json
{
  "name": "my-plugin",
  "description": "실제 책임과 경계",
  "version": "1.0.0",
  "source": "./my-plugin",
  "category": "productivity"
}
```

## Skill 작성

Description은 positive target과 negative trigger를 함께 적습니다. host-native fallback이 의미상 같은
결과를 보장하지 않으면 검색이나 추정으로 성공을 모사하지 말고 `blocked`를 반환합니다. write/remote
operation은 skill 선택과 별도 approval boundary로 둡니다. 자동 선택하지 않을 skill은 frontmatter의
`allow_implicit_invocation: false`를 사용하고 실제 host registry에서 확인합니다.

## 검증

```sh
python3 scripts/render-design-quality.py --check
python3 -B -m unittest discover -s evals/design-quality -p 'test_*.py' -v
python3 -B -m unittest discover -s plugins/code-review/tests -p 'test_*.py' -v
python3 -B -m unittest discover -s plugins/code-intelligence/tests -p 'test_*.py' -v
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py' -v
python3 evals/plugin-compat/native_probe.py --output /absolute/evidence-directory
python3 evals/skill-routing/native_smoke.py --help
```

정적 JSON/path 검사, model-free native loader probe, ownership case와 representative behavior를 서로
구분합니다. semantic behavior는 exact mcpls/language-server prerequisite가 있을 때만 실행합니다.
실행하지 못한 검사를 성공으로 표시하지 않고 blocker와 host/tool version을 기록합니다.

변경 후 package README, root README, routing, catalog, evaluation fixture와 migration 문서를 함께
갱신합니다. 제거한 이름에는 alias나 deprecated wrapper를 남기지 않습니다.
