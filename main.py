import logging
import os
from flask import Flask, render_template, request, jsonify
from threading import Thread
import asyncio

# Telegram imports
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ChatMemberHandler, ContextTypes

# Get telegram token from environment variables for security
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = 7582664657  # Telegram ID of @UMFST_Admin

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Bot application
bot_app = None
loop = None
bot_thread = None

# Set up logging
logging.basicConfig(level=logging.INFO)

# =============== TELEGRAM BOT FUNCTIONS ===============

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_user = update.chat_member.new_chat_member.user
    if new_user and not new_user.is_bot:
        chat_id = update.chat_member.chat.id
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=new_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Hi @{new_user.username}, please verify you're a UMFST student by sending your student ID or enrollment proof to the admin."
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"New member @{new_user.username} is awaiting verification. Use /verify @{new_user.username} or /reject @{new_user.username}."
        )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /verify @username")
        return
    username = context.args[0].lstrip('@')
    chat_id = update.effective_chat.id
    chat_members = await context.bot.get_chat_administrators(chat_id)
    for member in chat_members:
        if member.user.username == username:
            user_id = member.user.id
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ You've been verified! Welcome to the UMFST student community."
            )
            return
    await update.message.reply_text("User not found in group.")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /reject @username")
        return
    username = context.args[0].lstrip('@')
    chat_id = update.effective_chat.id
    chat_members = await context.bot.get_chat_administrators(chat_id)
    for member in chat_members:
        if member.user.username == username:
            user_id = member.user.id
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await update.message.reply_text(f"@{username} has been removed from the group.")
            return
    await update.message.reply_text("User not found in group.")

# =============== FLASK WEB APP ROUTES ===============

@app.route('/')
def index():
    """Status page showing bot information"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UMFST Campus Verification Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body data-bs-theme="dark">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>UMFST Campus Verification Bot</h3>
                        </div>
                        <div class="card-body">
                            <p><strong>Status:</strong> Running</p>
                            <p><strong>Bot Mode:</strong> Polling</p>
                            <p class="mt-4">
                                This bot restricts new members in UMFST campus Telegram groups until they're verified
                                by providing their student ID or enrollment proof to an admin.
                            </p>
                            <div class="mt-4">
                                <h5>Features:</h5>
                                <ul>
                                    <li>Automatically restricts new members when they join</li>
                                    <li>Notifies admin about new members requiring verification</li>
                                    <li>Admin can verify or reject members with simple commands</li>
                                    <li>Helps maintain a secure community of actual students</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

# Function to run the async bot
async def run_bot():
    global bot_app
    
    if not BOT_TOKEN:
        logging.error("No Telegram token provided. Bot will not start.")
        return

    # Create and configure the application
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    bot_app.add_handler(CommandHandler("verify", verify))
    bot_app.add_handler(CommandHandler("reject", reject))
    
    # Start the bot
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    logging.info("Bot started successfully in polling mode")
    
    # Keep the bot running
    try:
        await bot_app.updater.stop_on_signal()
    finally:
        await bot_app.stop()
        await bot_app.shutdown()

# Function to start the bot in a separate thread
def start_bot_thread():
    global loop, bot_thread
    
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    
    # Define the thread target function
    def bot_thread_func():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    
    # Start the bot in a separate thread
    bot_thread = Thread(target=bot_thread_func)
    bot_thread.daemon = True
    bot_thread.start()
    logging.info("Bot thread started")

# Start the bot when this module is imported
start_bot_thread()

# Helper function for rendering templates as strings (since we don't have template files)
def render_template_string(template_string):
    return template_string

# Main function to run the Flask app directly
if __name__ == "__main__":
    # Only start the bot thread if it hasn't been started yet
    if bot_thread is None or not bot_thread.is_alive():
        start_bot_thread()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
