import logging
import os
import sys
import asyncio
from aiohttp import web
from telegram import Update, ChatPermissions, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
)

# Get telegram token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7582664657  # Telegram ID of @UMFST_Admin

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

# --- HANDLERS ---

async def handle_chat_member_update(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
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

    try:
        async for member in context.bot.get_chat_members(chat_id):
            if member.user.username == username:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=member.user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
                await context.bot.send_message(
                    chat_id=member.user.id,
                    text="✅ You've been verified! Welcome to the UMFST student community."
                )
                return
    except Exception as e:
        logger.error(f"Verification error: {e}")
    await update.message.reply_text("User not found in group.")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /reject @username")
        return
    username = context.args[0].lstrip('@')
    chat_id = update.effective_chat.id

    try:
        async for member in context.bot.get_chat_members(chat_id):
            if member.user.username == username:
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=member.user.id)
                await update.message.reply_text(f"@{username} has been removed from the group.")
                return
    except Exception as e:
        logger.error(f"Rejection error: {e}")
    await update.message.reply_text("User not found in group.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban @username")
        return
    username = context.args[0].lstrip('@')
    chat_id = update.effective_chat.id

    try:
        banned_users = await context.bot.get_chat_administrators(chat_id)
        for banned in banned_users:
            if banned.user.username == username:
                await context.bot.unban_chat_member(chat_id=chat_id, user_id=banned.user.id, only_if_banned=True)
                await update.message.reply_text(f"✅ @{username} has been unbanned.")
                return
        await update.message.reply_text(f"❗ Could not find @{username} in the banned list.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def unban_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban_id [user_id]")
        return
    try:
        user_id = int(context.args[0])
        chat_id = update.effective_chat.id
        await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id, only_if_banned=True)
        await update.message.reply_text(f"✅ User with ID {user_id} has been unbanned.")
    except ValueError:
        await update.message.reply_text("Invalid ID.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Simple command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the UMFST Student Bot!\n\n"
        "Use /verify, /rules, or /resources to get started.\n"
        "Admins can manage new members through /verify and /reject."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Commands:\n"
        "/start - Welcome message\n"
        "/verify @username - Admins verify a user\n"
        "/reject @username - Admins reject a user\n"
        "/unban @username - Unban user by username\n"
        "/unban_id [user_id] - Unban by ID\n"
        "/rules - Community rules\n"
        "/resources - Useful links"
    )

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Rules:\n"
        "1. Be respectful.\n"
        "2. No spam.\n"
        "3. Use English or Romanian.\n"
        "4. Verify before chatting.\n"
        "5. Follow admin instructions."
    )

async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Resources:\n"
        "🖥️ Portal: https://student.umfst.ro\n"
        "📅 Schedule: https://orar.umfst.ro\n"
        "📄 Calendar: https://www.umfst.ro/academic-calendar\n"
        "🌐 Website: https://www.umfst.ro"
    )

# --- Web Server for Render ---
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

# --- Main Entrypoint ---
async def main_async():
    await start_webserver()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("resources", resources_command))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("unban_id", unban_id))

    await app.run_polling()

if __name__ == "__main__":
    import threading

    # Start webserver for Render health check
    def run_webserver():
        asyncio.run(start_webserver())

    threading.Thread(target=run_webserver).start()

    # Start Telegram bot (uses its own asyncio loop)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("resources", resources_command))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("unban_id", unban_id))

    app.run_polling()  # <--- let this manage the async loop
