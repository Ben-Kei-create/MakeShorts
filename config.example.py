# ============================================
# 🔑 GeminiStudio 設定ファイル (テンプレート)
# ============================================
#
# このファイルをコピーして config.py を作成してください:
# cp config.example.py config.py
#
# ⚠️ config.py は .gitignore に含まれています
# ============================================

# 🔑 GCP認証情報
# Google Cloud Console でダウンロードしたJSONキーファイルのパス
SERVICE_ACCOUNT_FILE = "credentials/your-service-account-key.json"

# GCPプロジェクトID
# Google Cloud Console の「プロジェクト情報」で確認できます
PROJECT_ID = "your-gcp-project-id"

# リージョン（通常は変更不要）
LOCATION = "us-central1"

# ============================================
# 🎨 画像生成設定
# ============================================

# 使用するモデル
MODEL = "imagegeneration@006"  # Imagen 3.0

# 出力フォルダ
OUTPUT_DIR = "output"

# プロンプト定義ファイル
META_FILE = "meta.json"

# ============================================
# 🌐 APIエンドポイント（自動生成・変更不要）
# ============================================
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"
