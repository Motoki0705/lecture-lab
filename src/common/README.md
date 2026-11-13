# 共通処理

- `library.py`: ミラー構造、コピー、内容照合、出典登録。
- `pipeline.py`: PDFページ分割、音声分割、Gemini入力、再開可能な途中保存、完成判定、Markdown文書の初稿。
- `__main__.py`: CLI。コマンド例は [project README](../../README.md)。

モデル実行・版/モデル照合・処理タイムアウト・ローカルログは `.agents/ops/explain_html/gemini.py` を再利用します。
作成途中の文書は `processed/` に公開せず、全パートの成功後だけ完成した文字起こしを保存します。
並列worker用のジョブキューではありません。同じ入力の同時処理は行わないでください。
