import os

Z_API_INSTANCE = os.environ.get("Z_API_INSTANCE", "")
Z_API_TOKEN = os.environ.get("Z_API_TOKEN", "")

if not Z_API_INSTANCE or not Z_API_TOKEN:
    raise ValueError(
        "Z-API credentials not configured. Please set Z_API_INSTANCE and Z_API_TOKEN environment variables."
    )

Z_API_BASE_URL = f"https://api.z-api.io/instances/{Z_API_INSTANCE}/token/{Z_API_TOKEN}"

SUBSCRIPTION_PRICE = 47.00

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
