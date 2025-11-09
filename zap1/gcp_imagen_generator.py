import os
import json
import base64
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# ========= 設定 =========
# ダウンロードしたJSONファイルのパスを指定
SERVICE_ACCOUNT_FILE = "/Users/fumiaki/GeminiStudio/makeshorts-477014-fb3e71c2c530.json"

# GCPプロジェクトID（Google Cloud Consoleで確認）
PROJECT_ID = "makeshorts-477014"

# リージョン（通常は us-central1）
LOCATION = "us-central1"

META_PATH = "meta.json"
OUTPUT_DIR = "output"

# Imagen モデル
MODEL = "imagegeneration@006"  # Imagen 3.0

# Vertex AI エンドポイント
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"
# ========================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 認証
def get_access_token():
    """サービスアカウントキーからアクセストークンを取得"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

if not os.path.exists(META_PATH):
    raise FileNotFoundError(f"❌ meta.jsonが見つかりません: {META_PATH}")

with open(META_PATH, "r", encoding="utf-8") as f:
    meta = json.load(f)

title = meta.get("title", "untitled")
prompts = meta.get("image_prompts", [])

if not prompts:
    raise ValueError("❌ meta.json に image_prompts が含まれていません。")

print(f"\n==============================")
print(f"🎬 タイトル: {title}")
print(f"🖼 生成シーン数: {len(prompts)} 枚")
print(f"🧠 使用モデル: Imagen 3.0 (Vertex AI)")
print(f"📍 プロジェクト: {PROJECT_ID}")
print(f"🌐 リージョン: {LOCATION}")
print("==============================\n")

# アクセストークン取得
try:
    access_token = get_access_token()
    print("✅ 認証成功\n")
except Exception as e:
    print(f"❌ 認証エラー: {e}")
    print("\n📝 確認事項:")
    print("   1. SERVICE_ACCOUNT_FILE のパスが正しいか")
    print("   2. JSONファイルが有効か")
    print("   3. サービスアカウントに適切なロールが付与されているか")
    exit(1)

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for i, prompt in enumerate(prompts, start=1):
    print(f"\n🧩 Scene {i} を生成中...")
    
    full_prompt = (
        f"Cinematic ultra-realistic vertical 9:16 image. "
        f"{prompt} "
        f"Dynamic lighting, dramatic colors, detailed textures, 4K quality."
    )
    
    payload = {
        "instances": [
            {
                "prompt": full_prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",
            "mode": "generate"
        }
    }
    
    print(f"📝 プロンプト: {prompt[:80]}...")
    
    try:
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print(f"📥 ステータスコード: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ エラー:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            continue
        
        data = response.json()
        
        # 画像データを抽出
        predictions = data.get("predictions", [])
        if not predictions:
            print("⚠️ 画像が生成されませんでした")
            continue
        
        image_data = predictions[0].get("bytesBase64Encoded")
        if not image_data:
            print("⚠️ 画像データが見つかりませんでした")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            continue
        
        # 画像を保存
        file_name = os.path.join(OUTPUT_DIR, f"{i:02d}_{title}_scene.png")
        with open(file_name, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        print(f"✅ 画像保存完了: {file_name}")
        
    except Exception as e:
        print(f"⚠️ Scene {i} で例外発生: {e}")

print("\n🎉 全シーンの生成が完了しました!")
print(f"📁 出力フォルダ: {os.path.abspath(OUTPUT_DIR)}")

# コスト概算を表示
cost = len(prompts) * 0.04
print(f"\n💰 概算コスト: ${cost:.2f} USD")