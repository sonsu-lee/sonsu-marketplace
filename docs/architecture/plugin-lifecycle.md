# 플러그인 생명주기

- Status: Current
- Last reviewed: 2026-09-29

## 흐름

```text
후보 선정
  → 업스트림과 라이선스 확인
  → 원본 기준 commit 가져오기
  → 원본 동일성 검증
  → 별도 기준 commit
  → Codex 정본 manifest와 marketplace 등록
  → package 검증과 실제 로딩 검증
  → 로컬 정책 변경
  → 로컬 변경 commit
  → 이후 업스트림 업데이트
```

## 업스트림 기준선

외부 플러그인은 원본 파일과 실행 권한을 먼저 보존하고, 업스트림 출처와 기준 commit을
`UPSTREAM.md`에 기록합니다. 여러 upstream의 일부 파일을 합성할 때는 source path, 임시 baseline
path, 최종 path와 hash를 함께 기록합니다. 원본 가져오기와 로컬 커스텀을 서로 다른 commit으로
남겨 이후 업데이트에서 두 변경의 출처를 구분할 수 있게 합니다.

## 로컬 커스텀

로컬 정책은 원본 기준선 이후에 적용합니다. 하나의 upstream plugin을 fork한 매니페스트 버전은
업스트림 버전 뒤에 `-sonsu.<revision>`을 붙여 원본 릴리스와 구분합니다. 여러 source를 합성하거나
로컬에서 새로 설계한 plugin은 독립 semantic version을 사용합니다. 여러 source를 합성했다면
`UPSTREAM.md`에서 각 source와 변환을 추적하고, 가져온 source가 없는 독립 plugin은 upstream
기준선을 만들지 않습니다. 정책 변경은 관련 결정 기록과 현재 아키텍처 문서를 함께 갱신합니다.

Engineering은 [독립 플러그인 결정](../decisions/0009-maintain-engineering-as-an-independent-plugin.md)에
따라 독립 semantic version을 사용하며 upstream 동기화나 이전 호환 경로를 배포 계약으로 두지
않습니다.

## Codex 배포

`.agents/plugins/marketplace.json`과 각 `.codex-plugin/plugin.json`이 Codex 패키지의 정본입니다.
기존 연구·라이선스·upstream 기록은 유지합니다. `shared/agent-policy`와 `shared/task-continuity`에서
각 플러그인에 필요한 자료를 생성해 다른 패키지 설치 없이 실행되게 합니다.

## Claude Code 배포

Codex catalog와 manifest를 정본으로 두고 `python3 scripts/render-claude-compat.py`로
`.claude-plugin/marketplace.json` 및 각 패키지 manifest를 생성합니다. 대부분의 스킬·hook·script는
같은 패키지 파일을 사용합니다. `memory-manager`는 네 스킬과 저장 스크립트·훅을 별도 Claude
패키지에 생성합니다. 정리·승격 스킬만 Claude의 수동 호출 제한을 적용합니다. 모델 프로필은 호스트별로 분리하며, Codex connector와
Claude Code MCP 구성은 별도의 실행 환경 상태입니다.

## ompは5件だけを配布する

`python3 scripts/render-omp-compat.py` はCodex catalogの順序を保ち、`workflow`、
`fluent-korean`、`fluent-english`、`fluent-japanese`、`design` の5件だけを
`.omp-plugin/marketplace.json` に生成します。Codex・Claude Codeの配布対象と元パッケージは変更しません。

| プラグイン | omp catalogのsource |
| --- | --- |
| Workflow | `./plugins/workflow/omp` |
| Fluent Korean | `./plugins/fluent-korean` |
| Fluent English | `./plugins/fluent-english` |
| Fluent Japanese | `./plugins/fluent-japanese` |
| Design | `./plugins/design/omp` |

Design・Workflowのomp専用パッケージは、必要なskills・references・assets・scripts・
figma-plugin・ライセンスを元パッケージから生成し、他のプラグインに依存せずに使える形にします。
スクリプトの実行権限はコピー時に保持します。独自hook、evidence gate、`task-continuity.py`、
omp runtime extensionは含めません。元パッケージのhook・継続スクリプトはCodex・Claude Code用に残します。
言語3件のスキルとエージェント、Designの品質契約・プロファイル、Workflowの操作権限境界は保持します。

生成先の `references/continuity.md` はomp標準のtodo・sessionによる継続を案内します。
`.sonsu` への継続記録、復元hookやセッションID転送を独自に追加しません。
カスタムロール用の `task.agentModelOverrides` も要求しません。

生成物は直接編集しません。生成器は `--check` で内容・実行権限の鮮度と不要な旧生成物を確認し、
通常実行では自身が生成したと確認できる旧extensionの `package.json`・`extension.ts` だけを整理します。
利用者のファイルや既存の `.sonsu`・`.engineering` 記録、インストールキャッシュは削除・編集しません。

### 公開と利用者の更新を分ける

この5件構成への変更は未公開です。生成・検証・コミットと、GitHubへの公開、利用環境への反映は別の操作です。
ローカル変更だけで既存のGitHub登録先やインストール済みパッケージが更新されたとは扱いません。

利用者は `~/.omp/agent/config.yml` の `marketplace.autoUpdate` を `auto` に設定できます。
ompは起動時に24時間より古いカタログの更新を可能な範囲で試みます。インストール済みプラグインを
自動更新するには、配布するカタログ内の対象プラグインのバージョンを上げる必要があります。
同じバージョンのまま `main` を変更しても自動更新の条件にはなりません。常時監視やホットリロードでもありません。

旧構成のアンインストールと不要設定の除去は[READMEの移行手順](../../README.md#omp)に従います。
整理後はセッションを終了してompを再起動し、読み込み済みの旧hook・agentを外します。

## 검증

生成器の `--check`、各ホストのcatalog・スキルパス・frontmatterの検査、実際のloader・行動評価は
分けて確認します。静的JSONの検査通過だけで、実際のスキル選択やホスト別のhook動作を確認済みとは扱いません。
미실행은 `not_run`, 원인 불명은 `inconclusive`로 기록합니다.
[업데이트 런북](../runbooks/updating-upstream-plugin.md)과
[ADR 0015](../decisions/0015-independent-skills.md)를 따릅니다. 이전 Engineering 게이트 결정은
[ADR 0014](../decisions/0014-use-codex-managed-engineering.md)에 역사적 근거로 보존합니다.
