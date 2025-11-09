import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="config/.env")
print("PROJECT_ID =", os.getenv("GCP_PROJECT_ID"))
print("SERVICE_ACCOUNT_FILE =", os.getenv("GCP_SERVICE_ACCOUNT_FILE"))
print("Gemini API Key =", os.getenv("GEMINI_API_KEY")[:10] + "...")