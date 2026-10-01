# 既存のデザイン作業から再開する

`interface-design`、`operations-ui`、`figma-workflow`、`design` の既存記録は、そのまま保存する。omp 版は旧記録を自動検出・移行・削除せず、移行用 helper や SessionStart hook を実行しない。

現在のユーザーが指定した作業と記録だけを読み取り専用で確認する。他のセッションや worktree を検索しない。過去の要約を現在の承認とみなさず、最新の指示、元の成果物、外部操作の結果と照合する。複数の記録が競合する場合や操作結果が不明な場合は、対象と実際の状態を確認するまで再実行しない。

再開に必要な確認済みの状態と次の操作は [omp の作業継続](continuity.md) に従って標準の todo とセッション履歴で扱う。`.sonsu` の記録や Git exclude を書き換えず、新しい独自 checkpoint も作らない。

保存済みのデザイン品質 contract/report の `profile` 値（`interface-design`、`operations-ui`、`figma-workflow`）は互換性のため変更しない。旧プラグインの削除はインストール済みパッケージだけを対象とし、ユーザーが依頼した場合に限る。作業成果物と過去の記録は残す。
