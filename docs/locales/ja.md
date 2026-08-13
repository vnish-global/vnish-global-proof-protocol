---
layout: default
title: VNISH GLOBAL Proof Protocol 日本語クイックスタート
lang: ja
---

# VNISH GLOBAL Proof Protocol：日本語クイックスタート

`vnish-verify` は、ローカルファイルをバージョン指定のマニフェストと照合します。ハッシュはローカルで計算され、ファームウェアはダウンロードされません。

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`：SHA-256、バイト数、指定した条件が単一のレコードと一致します。
- `NO_MATCH`：一致するレコードがありません。作業を止め、ファイルと情報を確認してください。
- `AMBIGUOUS`：複数のレコードが一致します。正確なリリース、モデル、制御ボード、インストール方法を指定してください。
- `SOURCE_UNAVAILABLE`：ファイルまたはマニフェストを読み取り、検証できません。

`MATCH` は安全性や適合性を保証しません。変更前に、正確なモデル、制御ボード、インストール方法、復旧手順を確認してください。

- VNISH GLOBAL のデータと検証方法：<https://vnish.global/ja/data/>
- VNISH Ninja の復旧手順：<https://vnish.ninja/ja/recovery/>
- ROI ASIC の段階的展開：<https://roiasic.com/ja/enterprise/>

プロトコルのバージョン：0.1.0、2026年8月13日。

[フィールドハンドブックに戻る](../index.md)
