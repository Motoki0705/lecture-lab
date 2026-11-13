> lecture-labへの移植版。モデルはGemini 4 Hydrogen (High)、agyはローカル環境の実体を使用します。
> 元の文書生成APIに加え、`Gemini.turn(media_files=(... ,))` は指定メディアの読み取りを許可します。
> メディア入力時はrequest-reviewモードとパス照合hookを使い、指定ファイルのread_fileだけを承認します。
> 文書生成だけの場合はstrictモードを維持します。出典の読取り、正常終了、実効モデル、構造化結果を照合します。
> 共通CLIと保存方針は[project README](../../../README.md)を参照してください。

# 説明HTMLの契約・Gemini編集・ローカルservice

[English](README.md) · [简体中文](README.zh-CN.md)

[#1710](https://github.com/Motoki0705/tennis-lab/issues/1710) の文書・編集の共通契約と、
永続的な版store、visual import・managed renderer・画像生成の可否を明示する境界、
Geminiによる候補生成と独立した意味検査、loopback HTTP/job runtimeを提供する。
ブラウザUI、画像provider実装、ブラウザ品質評価は別途注入する。
既存依存のPydantic・Pillow・jsonschema・FastAPI・uvicornとPython標準ライブラリを使う。

## 契約の正本と入口

[schema.py](schema.py) がwire型、HTTPパスと応答型、job遷移、公開エラー、JSON/Python使用例の
唯一の正本。下流から直接importする。repoのPythonで `PYTHONPATH=.agents/ops` を指定し、
`python -m explain_html.schema` でOpenAPI 3.1を生成できる。adapterやweb assetsへschemaを
複製しない。`contract_schema()` は同じ契約をメモリ内で返し、`examples()` は初版候補と、
commitできない未検証の判定例を含む。JSONには厳密な `parse()` を使い、未知fieldや型変換を拒否する。

| モジュール | 責務 |
|---|---|
| [schema.py](schema.py) | 文書、根拠・assets・図、要求、候補、検証結果、HTTP契約 |
| [document.py](document.py) | ID、HTML参照、選択対象、変更一覧の完全性 |
| [store.py](store.py) | 初版import、stage、commit、現在版・履歴、復元、export snapshot |
| [paths.py](paths.py) | symlinkを辿らないPOSIXのdirectory descriptor操作 |
| [parsing.py](parsing.py) | 曖昧なHTML構文とCSS resource記法の共通拒否 |
| [images.py](images.py) | ローカル画像import、能力の報告、失敗時に停止する画像adapter |
| [visual_definitions.py](visual_definitions.py) | 観測誤差例・比較グラフの厳密な宣言的設定と数値モデル |
| [visuals.py](visuals.py) | SVG/HTML/CSSの安全検査、図のmarkup、offline renderer policy |
| [renderers/visuals-v2.js](renderers/visuals-v2.js) | 宣言したfigureだけを描画し、図別に失敗を隔離する現行renderer |
| [renderers/visuals-v1.js](renderers/visuals-v1.js) | 旧revision用にbytesを固定して保持するrenderer |
| [editor.py](editor.py) | 初回執筆・編集、根拠保持、独立した意味検査 |
| [gemini.py](gemini.py) | model固定・tool禁止のagy実行、private証拠、中断 |
| [no_tools.py](no_tools.py) | schema検証済みの完了処理だけを許可するPreToolUse hook |
| [jobs.py](jobs.py) | 永続的な重複排除、文書別queue、公開前の再確認、復旧 |
| [managed.py](managed.py) | 実figure compile・画像利用不可adapter・staged visual検査のservice接続 |
| [service.py](service.py) | 共通契約からのHTTP route、token/Origin/Host検査、公開ファイル |
| [__main__.py](__main__.py) | ローカルstart/serve/status/stopとoffline export CLI |

## ID・対象・候補

生成側は編集対象となる論理ブロックへ `data-content-id` を付ける。同じ論理内容のIDを保持し、
新しい内容には新IDを付ける。見出し・配置・配色・ブロックのタグ・順番は固定しない。
HTMLは明示的で対応の取れた閉じタグを使う。HTML ID・内容ID・成果物IDの重複は失敗する。
HTML本来の `id` と `data-content-id` は別の名前空間。図・根拠は `data-figure-id`・
`data-evidence-id` で参照し、リソースには `data-asset-id` を使える。

共通parserは曖昧・未完了のcomment、processing instruction、単純なHTML5 doctype以外の宣言を拒否する。
commentは`<!-- ... -->`を使い、内部の連続hyphenや末尾hyphenを許可しない。`<!-->`・`<!--->`・
`--!>`閉じ・閉じないcomment・不正な`<!...>`宣言は`invalid_document`にし、document/visualの両検査で
補正しない。style属性・style要素内のCSS resource記法も共通に拒否する。`url()`のほか、
`image-set()`/`-webkit-image-set()`の文字列URL、`image()`・`src()`を含み、参照所有/変更申告から
静かに除外する代わりに未対応CSSとして拒否する。

すべての要求は `base_revision` へ対象を固定する。内容対象は存在必須。選択対象は、
完全一致の引用とprefix/suffix、ブロックのDOM `textContent` 全体における **UTF-16 code unit**
のstart/endを渡す。[HTML parser規則](https://html.spec.whatwg.org/multipage/parsing.html#preprocessing-the-input-stream)
に従い、入力CRLF/CR→LF、実体参照の展開、`pre`/`textarea`/`listing` 直後のLF1個の除去を経た
文字列で数える。その他の空白は保持し、非BMP文字は2 code unitとする。保存・markup比較用の
生HTMLは変更しない。text node内のoffsetや `innerText`
ではない。位置・引用・前後文脈のすべてとsurrogate境界を検査し、自動的な引用移動やrebaseはしない。

Candidateは更新後の完全なDocument、元のEditRequest、内容変更、理由付きの根拠変更、変更要約を持つ。
初版・部分更新・全体再構成は同じ契約。adapterが差分を完全な候補へ組み立ててからstageする。
初版は文書全体対象とnullのbaseを使い、以後の更新は現在版IDが必須。

`content_changes()` はブロックmarkupの追加・削除・変更と、図定義・renderer・参照assetが
変わるブロックを列挙する。ID注釈やFigureがない通常の `src`・`href`・`data` と、
`srcset`/`imagesrcset` の各候補もmanifestから解決する。すべての参照箇所がcontent IDの
配下にあることが必須で、head内の共通resourceも含め、所属がない参照は `broken_reference` にする。
asset変更は所属するすべてのcontent IDへ通知する。ブロックの移動や外側だけの配置変更では空の変更一覧も許す。
`evidence_changes()` は根拠の追加・削除・変更を列挙する。stageは未申告・架空・重複の変更を拒否する。
根拠変更の理由が妥当かは独立した意味検証が判定し、storeが推測しない。

## 検証

この移植版では [tests README](../../../tests/README.md) のコマンドで、文書契約・版管理・Gemini境界・ジョブ管理と講義処理を検証します。実Geminiの試行結果はGit対象外の `.cache/` に保存します。
