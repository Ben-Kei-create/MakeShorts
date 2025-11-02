# 🎬 MakeShorts Automation Toolkit

MakeShorts は、歴史ドキュメンタリー風の縦型ショート動画をワンクリックで設計・生成できる Python ツールキットです。Google Vertex AI Imagen 3.0 を利用した画像出力と、大規模言語モデルによる完全台本生成の両方をサポートします。

## ✨ 主な機能

- 🧠 **フルオート台本生成**: 有名人の名前を指定するだけで、オープニングからエンディングまで 12 セクションの完全台本、サムネイル/モーション用プロンプト、SEO 素材を自動生成。
- 🎨 **サムネイル一括生成**: 9:16 のサムネイル/シーン用プロンプトを 30 件まとめて生成し、Vertex AI Imagen で一括描画。
- 🗂️ **パッケージ化された成果物**: JSON 形式で構造化されたショート動画パッケージ、meta.json（画像生成用）、生レスポンスログを自動保存。
- 🔐 **セキュアな設定管理**: API キーは環境変数または `.env`（Git 管理外）で管理。Vertex AI の資格情報は従来通り `config.py` / `credentials/` に配置。

## 📦 セットアップ

1. 依存パッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. `config.example.py` をコピーして `config.py` を作成し、Vertex AI のプロジェクト設定とサービスアカウント JSON のパスを入力します。
   ```bash
   cp config.example.py config.py
   ```
3. `private_settings.example.py` を `private_settings.py` にコピーし、OpenAI 互換 API キーやベース URL をまとめて記入します。
   ```bash
   cp private_settings.example.py private_settings.py
   ```
   `private_settings.py` は `.gitignore` に含まれているため、実際の資格情報はリポジトリに残りません。
4. OpenAI 互換 API キーを環境変数または `.env` に設定します。
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export OPENAI_MODEL="gpt-4.1"  # 任意
   ```
   `.env` を利用する場合はリポジトリ直下に配置し、Git 管理対象外にしてください。

## 🚀 使い方

詳細な手順は [`USAGE.md`](USAGE.md) にまとめています。ここでは最もシンプルなフローを抜粋します。

### 1. 縦型ショート用パッケージを生成

著名人や歴史上の人物の名前を 1 つ渡すだけで、必要なコンテンツ一式がまとめて生成されます。

```bash
python shorts_pipeline.py "ウォルト・ディズニー"
```

- `packages/woruto-dhizuni/`（人物名をスラグ化したフォルダ）に以下が生成されます。
  - `shorts_package.json`: 台本、サムネイル/モーションプロンプト、SEO など全データ
  - `meta.json`: Imagen 3.0 用サムネイルプロンプト 30 件
  - `raw_response.txt`: モデルからのレスポンス全文

#### 実行フローの概要

1. `shorts_pipeline.py` が人物名からプロンプトを構築します。
2. `private_settings.py` もしくは環境変数にある API 情報で OpenAI 互換 API にアクセスし、完全パッケージを JSON 形式で取得します。
3. 応答結果を `packages/<slug>/` 配下に保存し、サムネイル生成用の `meta.json` を自動で書き出します。
4. `--auto-images` オプションを付けた場合は、続けて Vertex AI Imagen にサムネイル/モーション用画像生成を依頼し、`output/` 以下に保存します。
5. 生成後は `shorts_package.json` をもとに動画編集やナレーション収録へ進められます。

#### 画像を自動生成する場合

Vertex AI の設定が完了している場合は `--auto-images` を付けます。
```bash
python shorts_pipeline.py "ウォルト・ディズニー" --auto-images
```
`generate.py` の既存ロジックを内部で呼び出し、`config.py` の `OUTPUT_DIR` または `VERTICAL_IMAGE_OUTPUT`（環境変数）に画像を保存します。

### 2. 既存の meta.json から画像だけ生成

```bash
python generate.py
```

`packages/<slug>/meta.json` を指定して生成したい場合は次のようにします。
```python
from generate import generate_images

generate_images("packages/woruto-dhizuni/meta.json")
```

## 🧱 ディレクトリ構成

```
MakeShorts/
├── README.md
├── requirements.txt
├── config.example.py
├── create_meta.py
├── generate.py
├── shorts_pipeline.py
├── meta.example.json
├── packages/              # 自動生成（任意、Git 管理外推奨）
├── credentials/           # GCP サービスアカウント (Git ignore)
└── output/                # 画像出力先 (Git ignore)
```

## 🔐 セキュリティと運用メモ

- `config.py`, `credentials/*.json`, `output/`, `packages/` は Git 管理対象から除外してください。
- OpenAI 互換 API キーやその他資格情報は `.env` または OS の環境変数で安全に管理してください。
- `shorts_pipeline.py` はレスポンス JSON をそのまま保存します。必要に応じて情報セキュリティのポリシーに従って管理してください。

## 🧪 テストのヒント

- API 呼び出しが行われるため、ユニットテストでは `TextModelClient.generate_package` をモックすることで離線検証が可能です。
- `generate_images_from_prompts` は `requests` を通じて Vertex AI にアクセスするため、タイムアウトなどの例外ハンドリングを行っています。モック化で確認できます。

## 📮 コントリビューション

改善提案やバグ報告は Issue / Pull Request で歓迎しています。
