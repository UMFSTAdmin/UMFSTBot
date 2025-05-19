"""
Configuration settings for the Telegram bot application.
"""
import os

# Telegram Bot API token from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "placeholder_token_for_development")
if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "placeholder_token_for_development":
    print("Warning: Using placeholder token. Set TELEGRAM_TOKEN environment variable for production.")

# Webhook settings
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
if not WEBHOOK_URL and os.environ.get("ENVIRONMENT") == "production":
    print("Warning: No WEBHOOK_URL environment variable set for production environment.")

# Local development settings
USE_POLLING = os.environ.get("USE_POLLING", "True").lower() in ("true", "1", "t")

# Flask settings
SECRET_KEY = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
