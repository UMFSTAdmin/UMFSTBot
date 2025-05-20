import logging
import os
import sys
import time
import asyncio
from aiohttp import web
from telegram import Update, ChatMemberUpdated, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
)

# Get telegram token from environment variables for security
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7582664657  # Telegram ID of @UMFST_Admin

# Store pending users for verification
pending_users = {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

async def handle_chat_member_update(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    new_user = update.chat_member.new_chat_member.user
    chat_id = update.chat_member.chat.id

    if new_user and not new_user.is_bot:
        # Restrict the new user
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=new_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        # Store for later verification
        pending_users[new_user.username] = new_user.id

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Hi @{new_user.username}, please verify by sending your student ID to the admin."
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"New member @{new_user.username} joined. Use /verify @{new_user.username} or /reject @{new_user.username}."
        )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /verify @username")
        return

    username = context.args[0].lstrip('@')
    user_id = pending_users.get(username)

    if not user_id:
        await update.message.reply_text("❗ User not found or not pending verification.")
        return

    chat_id = update.effective_chat.id

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
    del pending_users[username]  # Remove from pending list

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /reject @username")
        return

    username = context.args[0].lstrip('@')
    user_id = pending_users.get(username)

    if not user_id:
        await update.message.reply_text("❗ User not found or not pending verification.")
        return

    chat_id = update.effective_chat.id

    # Ban the user from the group
    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    await update.message.reply_text(f"@{username} has been removed from the group.")
    del pending_users[username]  # Remove from pending list

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the UMFST Student Bot!\n\n"
        "Use /verify, /rules, or /resources to get started.\n"
        "Admins can manage new members through /verify and /reject."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Available Commands:\n"
        "/start - Introduction message\n"
        "/verify @username - Admins verify a user\n"
        "/reject @username - Admins reject a user\n"
        "/rules - Community rules\n"
        "/resources - Useful links"
    )

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 UMFST Community Rules:\n"
        "1. Be respectful.\n"
        "2. No spam or self-promotion.\n"
        "3. Use English or Romanian only.\n"
        "4. Verify before participating.\n"
        "5. Follow admin instructions."
    )

async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 UMFST Student Resources:\n"
        "🖥️ Student Portal: https://student.umfst.ro\n"
        "📅 Class Schedule: https://orar.umfst.ro\n"
        "📄 Academic Calendar: https://www.umfst.ro/academic-calendar\n"
        "🌐 UMFST Website: https://www.umfst.ro"
    )

async def handle(request):
    return web.Response(text="Bot is running")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 5000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    # Set up the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register all command handlers
    app.add_handler(ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("resources", resources_command))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CommandHandler("reject", reject))

    # Run web server and bot concurrently
    await asyncio.gather(start_webserver(), app.run_polling())

if __name__ == "__main__":
    asyncio.run(main())
