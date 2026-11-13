# lecture-lab

授業の音声・スライドを保存し、Gemini 4 Hydrogenによる内容重視の文字起こしから、自分向けの学習資料を作るプロジェクトです。
試験対策、演習問題と解説、理解を深める講義ノート、レポートの論点整理に使います。
`explain-html` で作成した資料には、閲覧画面から質問・変更指示を送り、回答を本文へ反映できます。

## 保存先

```text
data/
  raw/2026_spring/集積回路/01/          # 生の音声・PDF（Git対象外）
    audio/
    slides/
  processed/2026_spring/集積回路/01/    # 文字起こし・出典・処理記録（Git管理）
src/
  common/                              # 取り込み・文字起こし・文書生成
  courses/集積回路/                     # 授業ごとのコード・設定。内部構成は自由
outputs/2026_spring/集積回路/01/        # 生成文書（Git対象外）
.cache/                                # 分割音声・途中結果・ログ（Git対象外）
.agents/skills/                        # AIの作業手順
```

`raw` と `processed` は `{学期}/{授業名}/{授業回}` を共有します。授業回は `01` のようにゼロ埋めします。
学期名はユーザー指定の `2026_spring` を使用しています。今回の集積回路資料の日付は2026年9〜11月です。
原本を上書きせず、文字起こしにタイムスタンプは付けません。スライドのページ番号、専門用語、数式、説明の条件を保持します。
文字起こしと出典記録までGitに保存し、それを加工した学習資料・質問履歴は `outputs/` に保存します。
Gitをcloneするだけでは原本や生成資料は復元されません。これらは別途保管してください。

## セットアップ

WSL/LinuxのシステムPython 3.12、uv、Node.js/npm、ffmpeg/ffprobe、認証済みのagyが必要です。
ローカル閲覧サービスの停止にLinuxのpidfd APIを使うため、`uv.toml` でシステムPythonを選択します。

```bash
uv sync --locked
npm ci
node_modules/.bin/playwright install chromium --only-shell
.venv/bin/python -m src.common --help
```

agyの版は [.agents/ops/lib/agents.conf](.agents/ops/lib/agents.conf)、使用モデルは
[Gemini adapter](.agents/ops/explain_html/gemini.py) が正本です。現在はagy 1.5.7、`gemini-4-hydrogen-high` / high。
指定モデル・版と実行時の証拠が一致しない場合は停止し、別モデルへ自動で切り替えません。

## 授業資料を追加する

```bash
.venv/bin/python -m src.common --course 集積回路 --lesson 07 init
.venv/bin/python -m src.common --course 集積回路 --lesson 07 import /path/to/slides.pdf --kind slides
.venv/bin/python -m src.common --course 集積回路 --lesson 07 import /path/to/recording.m4a --kind audio
```

原本はコピーし、内容の一致を確認して `sources.json` に登録します。
同じ内容の再取り込みは重複せず、同名の異なるファイルは上書きせずエラーにします。
学期を変える場合は `--term 2026_fall` のように明示します。

## 文字起こし

```bash
.venv/bin/python -m src.common --course 集積回路 --lesson 01 transcribe 'data/raw/2026_spring/集積回路/01/slides/第1回集積回路20260925.pdf'
.venv/bin/python -m src.common --course 集積回路 --lesson 01 transcribe 'data/raw/2026_spring/集積回路/01/audio/集積回路1.m4a'
```

音声は5分、PDFは3ページずつGeminiへ渡します。全パートが成功した時点で
`processed/.../{audio|slides}/{原本ファイル名}/transcript.md` と `processing.json` を保存します。
途中結果は `.cache/` に保持し、同じコマンドで再開します。試行する場合は `--limit-parts 1` を付けます。
この指定は「今回新しく処理するパート数」の上限で、部分結果を完成した文字起こしとして登録しません。
未読入力・空回答・モデル不一致・中断を成功扱いにしません。モデル出力は人間による校閲済みではなく、
聞き取り不明箇所は本文と処理記録に残します。

同じ原本に対する同時実行は避けてください。校閲で文字起こしを変更した場合は、出典と修正理由を残し、
処理記録も明示的に更新してから資料生成に使います。

## 学習資料と質問

```bash
.venv/bin/python -m src.common --course 集積回路 --lesson 01 draft --name exam-notes --purpose '大学の授業の試験対策。重要概念、公式の適用条件、よくある誤解、確認問題と解説を含める'
```

複数回を横断する資料や、質問で更新できるHTML資料は、AIに例えば次のように依頼します。

> lecture-study と explain-html を使って、集積回路の第1〜3回を試験対策用の資料にして。
> MOSFETの前提から説明し、計算問題と解説も入れて。後から質問できるページを開いて。

AIは文字起こしを根拠として読み、[explain-htmlの手順](.agents/skills/explain-html/SKILL.md)で
ローカル閲覧画面を起動します。生成元資料の記載と、補足説明・導出・自作問題を区別します。
出題範囲は資料や指示に明示されている場合だけ確定情報として扱います。

## 開発と検証

[AGENTS.md](AGENTS.md)、[src/README.md](src/README.md)、[tests/README.md](tests/README.md) を参照してください。
GitHubのremoteは未設定です。ユーザーが空のリポジトリを作成した後、そのURLを `origin` に設定してpushできます。
