
# ========================================
# 📄 README.md
# ========================================
"""
# 🎨 GeminiStudio - AI Image Generator

Google Cloud Platform (Vertex AI) の Imagen 3.0 を使用して、プロンプトから高品質な画像を生成するPythonプロジェクトです。

## ✨ 特徴

- 🖼️ **バッチ生成**: 複数の画像を一度に生成
- 📝 **簡単設定**: JSONファイルでプロンプト管理
- 🎬 **縦長対応**: 9:16 フォーマット対応
- 💰 **コスト表示**: 生成コストを自動計算

## 📦 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/GeminiStudio.git
cd GeminiStudio
```

### 2. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Platform (GCP) の設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Vertex AI API を有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. JSONキーファイルを `credentials/` フォルダに配置

### 4. 環境設定

`config.example.py` をコピーして `config.py` を作成:

```bash
cp config.example.py config.py
```

`config.py` を編集:

```python
SERVICE_ACCOUNT_FILE = "credentials/your-service-account.json"
PROJECT_ID = "your-gcp-project-id"
```

## 🚀 使い方

### Step 1: プロンプトを作成

対話形式でプロンプトを作成:

```bash
python3 create_meta.py
```

または、`meta.json` を直接編集:

```json
{
  "title": "My Project",
  "image_prompts": [
    "A beautiful sunset over mountains, cinematic, 9:16 format",
    "A dragon flying through clouds, fantasy art, vertical"
  ]
}
```

### Step 2: 画像を生成

```bash
python3 generate.py
```

生成された画像は `output/` フォルダに保存されます。

## 📁 プロジェクト構成

```
GeminiStudio/
├── README.md              # このファイル
├── requirements.txt       # Python依存パッケージ
├── .gitignore            # Git除外設定
├── config.example.py     # 設定ファイルのテンプレート
├── config.py             # 実際の設定（Git除外）
├── generate.py           # 画像生成スクリプト
├── create_meta.py        # プロンプト作成ツール
├── meta.json             # プロンプト定義
├── credentials/          # GCP認証ファイル（Git除外）
│   └── .gitkeep
└── output/               # 生成画像の保存先（Git除外）
    └── .gitkeep
```

## 💰 料金

- **Imagen 3.0**: 約 $0.04/枚
- **初回特典**: $300 の無料クレジット（90日間有効）

## 🔒 セキュリティ

⚠️ **重要**: 以下のファイルは絶対にGitにコミットしないでください:

- `config.py` (GCP設定)
- `credentials/*.json` (サービスアカウントキー)
- `output/*` (生成画像)

`.gitignore` で自動的に除外されます。

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエスト歓迎！

## 📧 お問い合わせ

Issue を作成してください。
"""
