"""Example template for local-only API configuration."""

# Copy this file to `private_settings.py` and fill in your real credentials.
# `private_settings.py` is ignored by Git so secrets stay local.
API_CONFIG = {
    # OpenAI-compatible text generation endpoint credentials
    "openai_api_key": "sk-your-api-key",
    "openai_base_url": "https://api.openai.com/v1",
    "openai_model": "gpt-4.1",

    # Optional: override default temperature or other request parameters
    # "openai_temperature": 0.2,
}
