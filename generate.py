import os
import json
import base64
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# config.py から設定を読み込み
try:
    from config import *
except ImportError:
    print("❌ config.py が見つかりません")
    print("📝 セットアップ:")
    print("   1. cp config.example.py config.py")
    print("   2. config.py を編集してGCP情報を設定")
    exit(1)

def get_access_token():
    \"\"\"GCPアクセストークンを取得\"\"\"
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token
    except FileNotFoundError:
        print(f"❌ {SERVICE_ACCOUNT_FILE} が見つかりません")
        print("📝 GCPサービスアカウントキーを配置してください")
        exit(1)
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        exit(1)

def generate_images():
    \"\"\"meta.jsonから画像を生成\"\"\"
    
    # 出力フォルダ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # meta.json読み込み
    if not os.path.exists(META_FILE):
        print(f"❌ {META_FILE} が見つかりません")
        print("📝 create_meta.py を実行してプロンプトを作成してください")
        exit(1)
    
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
    
    title = meta.get("title", "untitled")
    prompts = meta.get("image_prompts", [])
    
    if not prompts:
        print("❌ image_prompts が含まれていません")
        exit(1)
    
    print(f"\\n{'='*70}")
    print(f"🎬 タイトル: {title}")
    print(f"🖼️  生成枚数: {len(prompts)} 枚")
    print(f"🧠 モデル: Imagen 3.0 (Vertex AI)")
    print(f"📍 プロジェクト: {PROJECT_ID}")
    print(f"{'='*70}\\n")
    
    # GCP認証
    print("🔑 GCP認証中...")
    access_token = get_access_token()
    print("✅ 認証成功\\n")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 画像生成ループ
    success_count = 0
    
    for i, prompt in enumerate(prompts, start=1):
        print(f"\\n{'─'*70}")
        print(f"🎨 Scene {i}/{len(prompts)} 生成中...")
        print(f"📝 プロンプト: {prompt[:100]}...")
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "9:16"
            }
        }
        
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                print(f"❌ エラー (Status {response.status_code}):")
                print(response.text[:200])
                continue
            
            data = response.json()
            image_data = data.get("predictions", [{}])[0].get("bytesBase64Encoded")
            
            if not image_data:
                print("⚠️  画像データが見つかりませんでした")
                continue
            
            # ファイル名生成
            filename = os.path.join(OUTPUT_DIR, f"{i:02d}_{title}.png")
            
            # 保存
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            print(f"✅ 保存完了: {filename}")
            success_count += 1
            
        except requests.exceptions.Timeout:
            print("⏱️  タイムアウト")
        except Exception as e:
            print(f"⚠️  エラー: {e}")
    
    # 完了メッセージ
    print(f"\\n{'='*70}")
    print(f"🎉 完了！ {success_count}/{len(prompts)} 枚生成")
    print(f"📁 保存先: {os.path.abspath(OUTPUT_DIR)}")
    print(f"💰 概算コスト: ${success_count * 0.04:.2f} USD")
    print(f"{'='*70}\\n")

if __name__ == "__main__":
    generate_images()