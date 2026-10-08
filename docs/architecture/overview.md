# 마켓플레이스 아키텍처

- Status: Current
- Last reviewed: 2026-10-07

## 목적

Sonsu MarketplaceはCodex・Claude Code・ompのプラグインを一つのリポジトリで管理し、
アップストリームの出典とローカル変更を追跡するマーケットプレイスです。

## 구성 요소

| 경로 | 책임 |
| --- | --- |
| `.agents/plugins/marketplace.json` | 마켓플레이스 식별자와 제공할 플러그인을 등록 |
| `plugins/<name>/.codex-plugin/plugin.json` | 개별 플러그인의 메타데이터와 구성 요소 진입점 정의 |
| `.claude-plugin/marketplace.json`, `plugins/<name>/.claude-plugin/plugin.json` | Codex 정본에서 생성한 Claude Code 배포 메타데이터 |
| `.omp-plugin/marketplace.json` | omp向け6件のカタログ。Codex catalogから対象だけを生成 |
| `plugins/{design,workflow,fluent-korean}/omp/` | 独自runtimeを含まない、生成済みのomp専用パッケージ |
| `plugins/<name>/skills/` | 플러그인이 제공하는 스킬 보관 |
| `plugins/<name>/UPSTREAM.md` | 업스트림 기준 commit, 포함 범위와 로컬 차이 기록 |
| `scripts/` | 공유 정책·연속성 참조 생성 등 저장소 유지보수 도구 |
| `docs/` | 현재 구조, 결정 이유, 요구사항과 운영 절차 보관 |
| `evals/` | 평가 fixture와 검증 도구 |

## 로딩 경계

```text
Codex: 저장소 루트
  → .agents/plugins/marketplace.json
  → source.path
  → plugins/<name>/.codex-plugin/plugin.json
  → skills, hooks와 기타 선언된 구성 요소
Claude Code: 저장소 루트
  → .claude-plugin/marketplace.json
  → plugins/<name>/.claude-plugin/plugin.json
  → skills, hooks와 지원되는 구성 요소
omp: リポジトリルート
  → .omp-plugin/marketplace.json
  → plugins/{workflow,design,fluent-korean}/omp または plugins/{fluent-english,fluent-japanese,career}
  → skillsと必要な同梱資料
```

CodexとClaude Codeは、ほとんどのパッケージで共通のスキル・hook・scriptをそれぞれのローダーで読み込みます。
`memory-manager`의 정본은 `plugins/memory-manager/`이며 Claude Code 배포본은 내부
`plugins/memory-manager/claude/`에 생성합니다. 스킬·script·hook의 수정은 정본에서만 하고
`scripts/render-claude-compat.py`로 배포본을 갱신합니다. Codex 전용 connector 선언은 이식하지 않습니다. 구성과
검증 절차는 [플러그인 개발 가이드](../guides/adding-a-plugin.md)에 있습니다.

omp向けはWorkflow、Fluent Korean、Fluent English、Fluent Japanese、Design、Careerの6件に限ります。
開発実行・task・todo・session・review・メモリはomp標準の機能を使い、カスタムロールの設定を追加しません。
`scripts/render-omp-compat.py` がDesign・Workflow・Fluent Koreanの専用パッケージを生成します。
独自runtime extension、hook、evidence gate、`task-continuity.py` は配布しません。
Fluent KoreanはCodexの単一呼び出しスキルと参考資料を投影し、現在のホストモデルを使います。
Claude Codeの多段階・strictモードや固定Opusエージェントはomp配布に含めません。
元パッケージのCodex・Claude Code向けファイル、English・Japaneseのスキル、Designの品質契約とプロファイル、
Workflowの権限境界は維持します。生成先の継続資料は `.sonsu` へ書き込まず、omp標準のtodo・sessionを案内します。
生成物やインストールキャッシュの手編集は行いません。

| ompでの責任 | 担当 |
| --- | --- |
| 開発実行・task・todo・session・review | omp標準 |
| Git・チケット・PRの操作権限と成果物 | Workflow |
| 言語別の文章品質・保護規則 | Fluent Korean・English・Japanese |
| UI・prototype・handoff品質とnative tool前提 | Design |
| 경력 원본·지원 서류·면접 준비 | Career |
| 必要に応じた調査・製品探索・文章構成 | Research・Product・Writing。基本配布に追加しない選択候補 |

Engineeringのompプロファイルは直接インストールした選択・legacy利用者のgate・実行・独立レビューが
参照するため保持します。基本6件の設定には使わず、独自セッションID注入やStop hookも提供しません。

`main` への公開は既存のインストールへの反映を意味しません。公開・自動更新の条件と
セッション再起動は[配布のライフサイクル](plugin-lifecycle.md)を参照してください。

마켓플레이스 등록은 저장소의 파일을 변경하거나 커밋하는 작업과 별개입니다. 호스트에
등록하거나 설치하는 작업도 각각 외부 상태 변경이므로 사용자가 요청한 범위에서만 수행합니다.

플러그인은 책임과 업데이트 경계에 따라 독립적으로 설치됩니다. Engineering은 개발 lifecycle과
코드 shape·단순성·유지보수성·실패 모드·운용 가능성 및 PR 리뷰·통합 결과 게시, Workflow는 Git과
delivery 산출물·PR 상태 조회·복구, Research는 외부 다중 출처 조사, Prompting은 프롬프트 산출물, Fluent Languages는
출력 언어를 담당합니다. Writing은 독자·목적에 맞는 정보 선별, 문서 배치와 글의 구성을 담당합니다.
Memory Manager는 명시적으로 호출하는 에이전트 메모리 점검·정리를
담당하며 저장 방식과 수정 권한은 대상 호스트의 계약을 따릅니다. Product는 제품 기회·문제·근거·도메인 규칙·검증과 PRD 변환을,
[Design](design.md)은 일반·운영 웹·앱 화면의 신규 설계·재설계·감사를 하나의 플러그인에서 담당합니다.
Figma를 사용하는 경우 native 화면·prototype과 handoff 품질을 확인하고, 코드 이전에는 해당 결과의 명시적 허가를 받습니다.
Figma가 정본이 아니면 기존 앱에 직접 구현합니다. 운영 업무 계약은 필요할 때 내부 참고 자료로 적용합니다.
Design Patterns는 실제 설계 forces와 필요한 guarantee에 근거한 named pattern 선택과 기존 적용의
읽기 전용 검토를 담당합니다. 전체 개발 lifecycle이나 broad code quality review는 소유하지 않습니다.
Career는 개발자 이직을 위한 경력 원본 정리, 미국식 resume·履歴書·職務経歴書 작성과 면접 준비·모의면접·회고를 담당합니다.
Figma canvas의 agent mutation은 registered official Figma MCP가 단독으로 소유하고, companion은
사용자가 Desktop에서 직접 실행합니다. 한 요청에서 여러 책임이 필요하면 runtime이 설치된 스킬을
조합하며 manifest dependency나 공통 router를 전제하지 않습니다.
세부 책임과 함께 적용하는 방식은 [스킬 라우팅](skill-routing.md)에서 관리합니다.

단일 upstream fork뿐 아니라 Engineering으로 이동한 품질 자료처럼 여러 source를 합성한 영역도 원본을
별도 baseline commit에 byte-for-byte로 보존한 뒤 최종 경로로 이동해 수정합니다. 현재 파일의
출처는 `UPSTREAM.md`의 source·baseline·final mapping으로 추적합니다.

## 문서 경계

현재 구조는 이 디렉터리에서 갱신하고, 선택의 이유와 대안은
[`decisions/`](../decisions)에 보존합니다. 구현 계획은 장기간 유지할 아키텍처 지식과
구분하며 기본적으로 `docs/` 밖에서 관리합니다.
