import requests
import json

GEMINI_API_KEY = "AIzaSyB5JjQVP_HQcl_BuJCzWadEAofu9rcoZ58"

# モデル一覧を取得
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        
        print(f"✅ 利用可能なモデル数: {len(models)}\n")
        print("=" * 80)
        
        # Imagen関連のモデルを探す
        imagen_models = []
        for model in models:
            name = model.get("name", "")
            if "imagen" in name.lower():
                imagen_models.append(model)
                print(f"\n📷 モデル名: {model.get('displayName', 'N/A')}")
                print(f"   ID: {name}")
                print(f"   サポートメソッド: {model.get('supportedGenerationMethods', [])}")
        
        if not imagen_models:
            print("\n⚠️ Imagenモデルが見つかりませんでした")
            print("\n利用可能なすべてのモデル:")
            for model in models[:10]:
                print(f"\n• {model.get('displayName', 'N/A')}")
                print(f"  ID: {model.get('name', '')}")
                print(f"  メソッド: {model.get('supportedGenerationMethods', [])}")
    else:
        print(f"❌ エラー: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 例外発生: {e}")
