# 📚 MakeShorts 実行フローガイド

このドキュメントは、`shorts_pipeline.py` を使って縦型ショートの完全パッケージを生成し、必要に応じて Vertex AI で画像を描画するまでの手順を段階的にまとめたものです。

## 1. 事前準備

1. 依存パッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. `config.example.py` をコピーして Vertex AI の設定を記入します。
   ```bash
   cp config.example.py config.py
   ```
   - `SERVICE_ACCOUNT_FILE` には GCP サービスアカウント JSON のパスを記入します。
   - `PROJECT_ID` や `LOCATION` も必要に応じて上書きします。
3. `private_settings.example.py` を複製し、OpenAI 互換 API の情報をまとめます。
   ```bash
   cp private_settings.example.py private_settings.py
   ```
   `private_settings.py` は `.gitignore` に登録済みなので、API キーがリポジトリに残ることはありません。
4. `.env` を利用する場合は、同じ情報（`OPENAI_API_KEY` など）を記入したうえでリポジトリの外へバックアップしておきます。

## 2. フルパッケージの生成

著名人・偉人の名前を 1 つ与えるだけで、要求仕様を満たした JSON パッケージを生成できます。

```bash
python shorts_pipeline.py "ウォルト・ディズニー"
```

- 実行すると `packages/woruto-dhizuni/` のようなスラグ化されたフォルダが作成されます。
- フォルダ内には以下が出力されます。
  - `shorts_package.json`: 台本、サムネイル/モーションプロンプト、SEO 情報などを含む構造化データ。
  - `meta.json`: Vertex AI Imagen 用の 30 件の画像プロンプト。
  - `raw_response.txt`: LLM からのレスポンス全文（検証や再利用用）。
- CLI は結果の概要を標準出力に表示するため、フォルダパスをすぐに確認できます。

### モデルの切り替え

`--model` オプションまたは環境変数 `OPENAI_MODEL` を指定すると、利用するテキスト生成モデルを差し替えられます。

```bash
python shorts_pipeline.py "ウォルト・ディズニー" --model gpt-4.1-mini
```

## 3. 画像の自動生成（任意）

Vertex AI Imagen を同時に実行する場合は、`--auto-images` オプションを付けます。`config.py` の `OUTPUT_DIR`、もしくは環境変数 `VERTICAL_IMAGE_OUTPUT` で保存先を変更可能です。

```bash
python shorts_pipeline.py "ウォルト・ディズニー" --auto-images
```

内部的には `generate.generate_images_from_prompts` を呼び出し、`meta.json` のプロンプトを元に 30 枚の画像を順番に描画します。

## 4. 画像のみ再描画したい場合

後から画像だけを再生成したいときは `generate.py` を直接利用します。

```bash
python generate.py
```

`meta.json` の場所を明示したい場合は `generate_images` 関数を呼び出します。

```python
from generate import generate_images

generate_images("packages/woruto-dhizuni/meta.json")
```

## 5. 生成物の管理

- `packages/`、`credentials/`、`output/` は `.gitignore` 済みなので、生成物や資格情報が誤ってコミットされることはありません。
- 生成された JSON を編集したい場合は、`shorts_package.json` を開いて必要なセクション（台本、SEO、チェックリストなど）を直接修正できます。
- Vertex AI のコスト管理のため、`generate_images_from_prompts` の戻り値で生成枚数を確認し、ログを残しておくと便利です。

## 6. トラブルシューティング

| 症状 | 対処法 |
| ---- | ------ |
| `openai` モジュールが無いというエラー | `pip install -r requirements.txt` を再実行し、`OPENAI_API_KEY` が設定されているか確認します。 |
| `config.py` が見つからない | テンプレートからコピーし、`SERVICE_ACCOUNT_FILE` を正しいパスに更新します。 |
| Vertex AI で認証エラー | サービスアカウント JSON の権限（Vertex AI User など）を確認し、時計ズレがないかもチェックします。 |
| JSON 解析エラー | `raw_response.txt` を確認し、レスポンス末尾に余計な文字が無いかを検証します。必要であれば `_extract_json_block` のロジックが自動抽出を試みます。 |

このフローを基に、著名人の名前だけを変えながら量産的にショート動画台本を作成できます。
