"""
Telegram bot implementation for user verification in groups.
Sets up the bot with handlers and webhook server.
"""
import logging
import os
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

from config import TELEGRAM_TOKEN, WEBHOOK_URL, USE_POLLING, SECRET_KEY
from handlers import (
    new_member_handler,
    verify_command_handler,
    reject_command_handler,
    list_pending_command_handler,
    help_command_handler,
    error_handler
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Create bot instance and updater
updater = None
dispatcher = None

def setup_bot():
    global updater, dispatcher
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "placeholder_token_for_development":
        logger.warning("No valid Telegram token provided. Bot functionality will be limited.")
        return False
    
    try:
        # Create the Updater
        updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Register handlers
        dispatcher.add_handler(CommandHandler("verify", verify_command_handler))
        dispatcher.add_handler(CommandHandler("reject", reject_command_handler))
        dispatcher.add_handler(CommandHandler("listpending", list_pending_command_handler))
        dispatcher.add_handler(CommandHandler("help", help_command_handler))
        dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member_handler))
        
        # Register error handler
        dispatcher.add_error_handler(error_handler)
        
        # Start bot based on configuration
        if USE_POLLING:
            # For local development using polling
            logger.info("Bot started in polling mode")
            updater.start_polling()
        elif WEBHOOK_URL:
            webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
            logger.info(f"Setting webhook to {webhook_url}")
            updater.start_webhook(
                listen="0.0.0.0",
                port=5000,
                url_path=TELEGRAM_TOKEN,
                webhook_url=webhook_url if WEBHOOK_URL else None
            )
        else:
            logger.warning("No webhook URL set and polling disabled. Bot won't receive updates.")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing bot: {e}")
        return False

# Set up the bot
bot_initialized = setup_bot()

# Webhook setup
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    """
    Handle incoming webhook requests from Telegram.
    """
    if not bot_initialized or not dispatcher:
        logger.error("Webhook received but bot not initialized")
        return "Bot not initialized", 500
    
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), updater.bot)
            dispatcher.process_update(update)
            return "OK"
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return "Error processing update", 500
    
    return "Method not allowed", 405

@app.route('/')
def index():
    """
    Simple status page to verify the bot is running.
    """
    status = {
        "status": "running",
        "bot_initialized": bot_initialized,
        "mode": "polling" if USE_POLLING else "webhook"
    }
    
    # For HTML response
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Verification Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body data-bs-theme="dark">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>Telegram Verification Bot Status</h3>
                        </div>
                        <div class="card-body">
                            <p><strong>Status:</strong> Running</p>
                            <p><strong>Bot Initialized:</strong> {bot_initialized}</p>
                            <p><strong>Mode:</strong> {"Polling" if USE_POLLING else "Webhook"}</p>
                            <p class="mt-4">
                                This bot restricts new members in Telegram groups until an admin verifies them.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_response
