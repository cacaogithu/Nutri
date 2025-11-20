import os

# Testing mode - if enabled, uses mock Z-API instead of real API
TESTING_MODE = os.environ.get("TESTING_MODE", "false").lower() == "true"

# Allowed phone number for access control (only this number can interact)
ALLOWED_PHONE_NUMBER = os.environ.get("ALLOWED_PHONE_NUMBER", "+14079897162")

# Z-API credentials
Z_API_INSTANCE = os.environ.get("Z_API_INSTANCE", "3E84D96FA64D02171F6692EB59F3FBA2")
Z_API_TOKEN = os.environ.get("Z_API_TOKEN", "34D8B9D16CCB6070EF5D38CB")

# Only validate credentials if not in testing mode
if not TESTING_MODE:
    if not Z_API_INSTANCE or not Z_API_TOKEN:
        raise ValueError(
            "Z-API credentials not configured. Please set Z_API_INSTANCE and Z_API_TOKEN environment variables."
        )

Z_API_BASE_URL = f"https://api.z-api.io/instances/{Z_API_INSTANCE}/token/{Z_API_TOKEN}"

SUBSCRIPTION_PRICE = 47.00

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

# Buffer configuration
BUFFER_WINDOW_SECONDS = int(os.environ.get("BUFFER_WINDOW_SECONDS", "15"))
BUFFER_CHECK_INTERVAL_SECONDS = int(os.environ.get("BUFFER_CHECK_INTERVAL_SECONDS", "3"))
BUFFER_LOCK_TIMEOUT_SECONDS = int(os.environ.get("BUFFER_LOCK_TIMEOUT_SECONDS", "60"))
