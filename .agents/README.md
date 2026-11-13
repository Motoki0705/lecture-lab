# AI運用

全AI共通の入口は [AGENTS.md](../AGENTS.md)。仕様は各README、繰り返す手順はskills、
仕様化していない再利用できる観察だけmemoryへ置く。tennis-labの進捗・担当者・個人情報は移植しない。

## 使用するスキル

- [lecture-study](skills/lecture-study/SKILL.md): 取り込み、文字起こし、試験対策・演習・論点整理。
- [explain-html](skills/explain-html/SKILL.md): Geminiが書いたHTMLを開き、質問と指示で本文を更新する。
- [memory](skills/memory/SKILL.md): 共有の観察を読む・記録する・整理する。
- [skill-creator](skills/skill-creator/SKILL.md): このプロジェクトの新しい作業手順を作る・改善する。

`explain-html` と依存runtime・回帰テストはtennis-labの `origin/main`（2026-11-13取得）から移植。
lecture-labではローカルagyの検出、Hydrogenモデル、メディア入力、独立したPython/Node依存へ適応した。
GPU学習・テニス注釈・既存GitHub親issueに依存するスキルは対象外。

実装契約は [ops/explain_html/README.ja.md](ops/explain_html/README.ja.md) とコードに置く。
講義用のメディア入力は `Gemini.turn(..., media_files=...)` を使用し、明示したファイルの読み取りだけを追加許可する。
文字起こしを実行するCLIは [src/common](../src/common/README.md)。
