---
name: lecture-study
description: Import course audio and slides, transcribe them with agy Gemini, and create source-grounded lecture notes, exam preparation, exercises or report outlines. Use for this project's lecture materials and study questions.
---

# 授業資料から学習資料を作る

保存方針とCLIは [project README](../../../README.md) を先に読む。
学期・授業・回を既存の `sources.json` から確認する。日付と回の推定は記録し、内容確認済みにしない。
原本追加はCLIでコピーし、既存ファイルを上書きしない。

文字起こしには `transcribe` を使う。指定Geminiで音声・PDFを実際に読ませる。
部分結果、要約、PDFの機械抽出を、完了した文字起こしとして扱わない。
不明箇所を保持し、数式・単位・条件・ページ番号を原資料と照合する。タイムスタンプは不要。
中断後は同じ入力・設定で再開する。実行前に対象回と音声の長さ/ページ数を確認し、
今回の対象だけを処理する。プロジェクト初期化だけの依頼で全授業の生成を自動開始しない。

文書作成は、読者の前提、目的、対象回を会話から決める。試験対策は重要概念、
公式の適用条件、誤解しやすい点、練習問題と解説を必要に応じて構成する。
講義内の事実、資料から導出した説明、補足知識、自作問題を区別し、根拠がない出題予想は断定しない。
複数回を横断する場合も出典を保つ。補足を外部調査する場合はその出典を別に示す。

Markdownの初稿には `draft` を使える。質問しながら読める資料は
[explain-html](../explain-html/SKILL.md) のbriefに文字起こしの根拠を渡し、生成・照合後にローカル画面を開く。
保存先は `outputs/{学期}/{授業}/{回またはcourse-wide}/{用途}/`。質問は既存文書へ反映し、
文字起こしそのものには混ぜない。原資料にない説明を授業の発言として書き戻さない。
