import logging
import os
import sys
import time
import signal
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ChatMemberHandler, ContextTypes

# Get telegram token from environment variables for security
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

logging.basicConfig(level=logging.INFO)

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

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lift the ban for a user so they can rejoin the group"""
    # Only allow admins to use this command
    if update.effective_user.id != ADMIN_ID:
        return
        
    # Check if a username was provided
    if not context.args:
        await update.message.reply_text("Usage: /unban @username")
        return
        
    username = context.args[0].lstrip('@')
    chat_id = update.effective_chat.id
    
    try:
        # Try to find the user by username
        # This is a bit tricky since banned users are not in the group anymore
        # Let's ask the admin for confirmation
        confirmation = await update.message.reply_text(
            f"Looking for user @{username} to unban... "
            f"Please also provide the user ID if you know it using /unban_id [user_id]"
        )
        
        # Let's try to find any ban information by username
        banned_users = await context.bot.get_chat_banned_members(chat_id)
        
        for banned_user in banned_users:
            if banned_user.user.username == username:
                # Found the user, now unban them
                user_id = banned_user.user.id
                await context.bot.unban_chat_member(
                    chat_id=chat_id, 
                    user_id=user_id,
                    only_if_banned=True
                )
                await update.message.reply_text(f"✅ @{username} has been unbanned and can rejoin the group.")
                return
                
        # If we reach here, we couldn't find the user in the banned list
        await update.message.reply_text(
            f"❗ Could not find @{username} in the banned users list. "
            f"You may need to unban by user ID with /unban_id [user_id]"
        )
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def unban_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user by their ID number"""
    # Only allow admins to use this command
    if update.effective_user.id != ADMIN_ID:
        return
        
    # Check if a user ID was provided
    if not context.args:
        await update.message.reply_text("Usage: /unban_id [user_id]")
        return
    
    try:
        # Get the user ID from args
        user_id = int(context.args[0])
        chat_id = update.effective_chat.id
        
        # Unban the user by ID
        await context.bot.unban_chat_member(
            chat_id=chat_id, 
            user_id=user_id,
            only_if_banned=True
        )
        
        await update.message.reply_text(f"✅ User with ID {user_id} has been unbanned and can rejoin the group.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric ID.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
	try:
		app = ApplicationBuilder().token(BOT_TOKEN).build()

		app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
		app.add_handler(CommandHandler("verify", verify))
		app.add_handler(CommandHandler("reject", reject))
		app.add_handler(CommandHandler("unban", unban))
		app.add_handler(CommandHandler("unban_id", unban_id))

		logger.info("Bot is starting...")
		app.run_polling()
	except Exception as e:
		logger.error(f"Bot failed to start: {e}")
    
if __name__ == "__main__":
    main()