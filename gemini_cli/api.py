import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
import json


class GeminiAPI:
    def __init__(self):
        """Vertex AI の Gemini モデルを初期化"""
        credentials_path = os.getenv("GCP_SERVICE_ACCOUNT_FILE", "credentials/makeshorts-477014-a05545136d6a.json")
        project_id = os.getenv("GCP_PROJECT_ID", "makeshorts-477014")
        location = os.getenv("GCP_LOCATION", "us-central1")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # ← 新モデルに対応

        creds = service_account.Credentials.from_service_account_file(credentials_path)
        vertexai.init(project=project_id, location=location, credentials=creds)

        # 最新モデルを利用
        self.model = GenerativeModel(model_name)

    def generate_text(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Geminiからテキストを生成"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            return response.text.strip()
        except Exception as e:
            print(f"[GeminiAPI Error]: {e}")
            return "⚠️ Gemini応答エラー：Vertex AIへの接続またはAPIの権限を確認してください。"

    def generate_json(self, prompt: str) -> dict:
        """GeminiからJSON形式の応答を生成"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[GeminiAPI JSON Error]: {e}")
            return {"error": str(e)}
