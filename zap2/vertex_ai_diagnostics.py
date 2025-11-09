"""Vertex AI接続とモデルアクセスの診断スクリプト"""

import os
from google.oauth2 import service_account

# 設定
PROJECT_ID = 'makeshorts-477014'
LOCATION = 'us-central1'  # us-east1から変更
SERVICE_ACCOUNT_FILE = 'makeshorts-477014-fb3e71c2c530.json'

def test_vertex_ai_access():
    """Vertex AIへのアクセスとモデルの利用可能性をテスト"""
    
    print(f"=== Vertex AI 診断開始 ===\n")
    print(f"プロジェクトID: {PROJECT_ID}")
    print(f"リージョン: {LOCATION}")
    print(f"サービスアカウントファイル: {SERVICE_ACCOUNT_FILE}\n")
    
    # 1. サービスアカウントファイルの存在確認
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ エラー: サービスアカウントファイルが見つかりません: {SERVICE_ACCOUNT_FILE}")
        print(f"現在のディレクトリ: {os.getcwd()}")
        print(f"ディレクトリ内のJSONファイル:")
        for f in os.listdir('.'):
            if f.endswith('.json'):
                print(f"  - {f}")
        return
    print(f"✅ サービスアカウントファイル存在確認")
    
    # 2. 認証情報の読み込み
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        print(f"✅ 認証情報の読み込み成功")
        print(f"   サービスアカウント: {credentials.service_account_email}\n")
    except Exception as e:
        print(f"❌ 認証情報の読み込み失敗: {e}")
        return
    
    # 3. Vertex AI初期化とモデルテスト
    print("=== モデルアクセステスト ===\n")
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
        print(f"✅ Vertex AI初期化成功\n")
    except Exception as e:
        print(f"❌ Vertex AI初期化失敗: {e}\n")
        return
    
    models_to_test = [
        'gemini-1.5-flash-002',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-1.0-pro',
        'gemini-pro',
    ]
    
    for model_name in models_to_test:
        try:
            model = GenerativeModel(model_name)
            
            response = model.generate_content(
                "Say 'test' in one word.",
                generation_config={"temperature": 0.1, "max_output_tokens": 10}
            )
            
            print(f"✅ {model_name}: アクセス可能")
            print(f"   レスポンス: {response.text.strip()}")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                print(f"❌ {model_name}: 404 Not Found")
            elif "403" in error_msg or "permission" in error_msg.lower():
                print(f"❌ {model_name}: 403 Permission Denied")
            else:
                print(f"❌ {model_name}: エラー")
                print(f"   詳細: {error_msg[:200]}")
        print()
    
    print("\n=== 診断完了 ===")


if __name__ == "__main__":
    test_vertex_ai_access()
