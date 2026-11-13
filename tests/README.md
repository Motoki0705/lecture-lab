# 検証

```bash
.venv/bin/python -m pytest -n auto
node --test tests/unit/agents_ops/explain_html/visuals.test.mjs
```

原本の保持、同名異内容の拒否、パスの逸脱拒否、途中結果の再開と完成判定を検証します。
explain-htmlの移植元の文書契約・版管理・モデル出力・ジョブ管理の回帰テストも含みます。
通常のpytestでは実際のモデルを呼ばず、認証やGPUを必要としません。
実機の音声/PDF試行結果は `.cache/` へ保存し、原本内容やprivateログをテストfixtureに混ぜません。
