# AIの入口

作業開始時に [.agents/memory/SUMMARY.md](.agents/memory/SUMMARY.md)、
[.agents/README.md](.agents/README.md)、対象ディレクトリのREADMEを読む。

- 保存方針・文字起こし仕様の正本は [README.md](README.md)。ユーザーに確定済みの方針を聞き直さない。
- Pythonはこのrepoの `.venv/bin/python` を使う。tennis-labの環境を参照しない。
- コード変更はこのrepoの `.claude/worktrees/<task-name>` に専用worktreeを作って行う。
- 原本を編集しない。取り込みはコピーと照合。rawやoutputs、認証情報、privateログをGitへ追加しない。
- Geminiの実効モデルと完了状態を確認する。別モデル、別の音声認識方式への暗黙の切替は禁止。
- 聞き取り不明箇所を推測で埋めない。要約を文字起こしと呼ばない。授業資料と補足説明を区別する。
- 共通処理は `src/common/`、授業固有の処理は `src/courses/{授業名}/`。各授業内の構成は必要に応じて決める。
- 意味のあるテストを先に設計し、変更後に実行する。PR本文は日本語。
- GitHubの作成・公開設定はユーザーの担当。依頼なしにremote設定やpushを行わない。
