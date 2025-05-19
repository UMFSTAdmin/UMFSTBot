"""
Handler functions for Telegram bot events and commands.
"""
import logging
from telegram import Update, ChatMember
from telegram.ext import CallbackContext
from telegram.error import TelegramError

from storage import verification_storage
from utils import get_restricted_permissions, get_full_permissions, get_user_name, is_admin

logger = logging.getLogger(__name__)

def new_member_handler(update: Update, context: CallbackContext):
    """
    Handle new members joining the chat.
    Restrict their permissions and notify them about verification.
    """
    if not update.message or not update.message.new_chat_members:
        return
    
    chat_id = update.effective_chat.id
    
    # Process each new member
    for new_member in update.message.new_chat_members:
        # Skip if the new member is the bot itself
        if new_member.id == context.bot.id:
            logger.info(f"Bot was added to group {chat_id}")
            continue
        
        user_id = new_member.id
        
        try:
            # Restrict the new member
            context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=get_restricted_permissions()
            )
            
            # Send verification message
            user_name = get_user_name(new_member)
            welcome_message = (
                f"👋 Welcome {user_name}!\n\n"
                f"To prevent spam, you've been temporarily restricted from sending messages "
                f"in this group until an admin verifies you.\n\n"
                f"Admins can use /verify {user_id} to approve or /reject {user_id} to remove this user."
            )
            
            message = update.message.reply_text(welcome_message)
            
            # Store the pending verification
            verification_storage.add_pending_verification(
                chat_id=chat_id,
                user_id=user_id,
                username=new_member.username,
                first_name=new_member.first_name,
                last_name=new_member.last_name,
                message_id=message.message_id
            )
            
            logger.info(f"New member {user_id} restricted in chat {chat_id}, awaiting verification")
            
        except TelegramError as e:
            logger.error(f"Error restricting new member {user_id} in chat {chat_id}: {e}")

def verify_command_handler(update: Update, context: CallbackContext):
    """
    Handle /verify command from admins.
    Grant permissions to a verified user.
    """
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if command sender is an admin
    try:
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(chat_member):
            update.message.reply_text("Only admins can use this command.")
            return
    except TelegramError as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}")
        update.message.reply_text("Failed to verify admin status. Please try again later.")
        return
    
    # Get the user ID to verify
    if not context.args:
        update.message.reply_text("Please specify a user ID to verify.\nUsage: /verify USER_ID")
        return
    
    try:
        target_user_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("Invalid user ID. Please use a numeric ID.")
        return
    
    # Check if user is pending verification
    user_data = verification_storage.get_pending_verification(chat_id, target_user_id)
    if not user_data:
        update.message.reply_text("This user is not pending verification or has already been verified.")
        return
    
    try:
        # Grant permissions to the user
        context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user_id,
            permissions=get_full_permissions()
        )
        
        # Get user's name or ID for the message
        try:
            target_member = context.bot.get_chat_member(chat_id, target_user_id)
            user_name = get_user_name(target_member.user)
        except TelegramError:
            user_name = f"User {target_user_id}"
        
        # Remove from pending verification
        verification_storage.remove_pending_verification(chat_id, target_user_id)
        
        # Send verification success message
        admin_name = get_user_name(update.effective_user)
        update.message.reply_text(f"✅ {user_name} has been verified by {admin_name}. Welcome to the group!")
        
        logger.info(f"User {target_user_id} verified in chat {chat_id} by admin {user_id}")
        
    except TelegramError as e:
        logger.error(f"Error verifying user {target_user_id} in chat {chat_id}: {e}")
        update.message.reply_text(f"Failed to verify user: {e}")

def reject_command_handler(update: Update, context: CallbackContext):
    """
    Handle /reject command from admins.
    Remove a user from the group.
    """
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if command sender is an admin
    try:
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(chat_member):
            update.message.reply_text("Only admins can use this command.")
            return
    except TelegramError as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}")
        update.message.reply_text("Failed to verify admin status. Please try again later.")
        return
    
    # Get the user ID to reject
    if not context.args:
        update.message.reply_text("Please specify a user ID to reject.\nUsage: /reject USER_ID")
        return
    
    try:
        target_user_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("Invalid user ID. Please use a numeric ID.")
        return
    
    # Check if user is pending verification
    user_data = verification_storage.get_pending_verification(chat_id, target_user_id)
    if not user_data:
        update.message.reply_text("This user is not pending verification or has already been verified.")
        return
    
    try:
        # Get user's name or ID for the message
        try:
            target_member = context.bot.get_chat_member(chat_id, target_user_id)
            user_name = get_user_name(target_member.user)
        except TelegramError:
            user_name = f"User {target_user_id}"
        
        # Ban the user
        context.bot.ban_chat_member(chat_id=chat_id, user_id=target_user_id)
        
        # Immediately unban to convert it to a "kick" (not a permanent ban)
        context.bot.unban_chat_member(chat_id=chat_id, user_id=target_user_id)
        
        # Remove from pending verification
        verification_storage.remove_pending_verification(chat_id, target_user_id)
        
        # Send rejection message
        admin_name = get_user_name(update.effective_user)
        update.message.reply_text(f"❌ {user_name} has been rejected and removed from the group by {admin_name}.")
        
        logger.info(f"User {target_user_id} rejected in chat {chat_id} by admin {user_id}")
        
    except TelegramError as e:
        logger.error(f"Error rejecting user {target_user_id} in chat {chat_id}: {e}")
        update.message.reply_text(f"Failed to reject user: {e}")

def list_pending_command_handler(update: Update, context: CallbackContext):
    """
    Handle /listpending command from admins.
    List all users awaiting verification.
    """
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if command sender is an admin
    try:
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        if not is_admin(chat_member):
            update.message.reply_text("Only admins can use this command.")
            return
    except TelegramError as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}")
        update.message.reply_text("Failed to verify admin status. Please try again later.")
        return
    
    # Get all pending users
    pending_users = verification_storage.get_all_pending_users(chat_id)
    
    if not pending_users:
        update.message.reply_text("No users are currently awaiting verification.")
        return
    
    # Build message with list of pending users
    message = "Users awaiting verification:\n\n"
    
    for user_id, user_data in pending_users.items():
        username = user_data.get("username", "")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")
        
        user_display = ""
        if username:
            user_display += f"@{username} "
        if first_name or last_name:
            name_parts = []
            if first_name:
                name_parts.append(first_name)
            if last_name:
                name_parts.append(last_name)
            user_display += f"({' '.join(name_parts)})"
        
        if not user_display:
            user_display = f"User {user_id}"
        
        message += f"• {user_display} - ID: {user_id}\n"
        message += f"  Commands: /verify {user_id} | /reject {user_id}\n\n"
    
    update.message.reply_text(message)

def help_command_handler(update: Update, context: CallbackContext):
    """
    Handle /help command to provide information about the bot.
    """
    help_text = (
        "🤖 *Verification Bot Help* 🤖\n\n"
        "*For Admins:*\n"
        "/verify USER_ID - Approve a user and grant chat permissions\n"
        "/reject USER_ID - Remove a user from the group\n"
        "/listpending - Show all users awaiting verification\n"
        "/help - Show this help message\n\n"
        "*How it works:*\n"
        "1. When new users join, they are restricted from sending messages\n"
        "2. An admin must verify them using the /verify command\n"
        "3. Once verified, users can participate in the chat\n"
        "4. Alternatively, admins can reject users with /reject"
    )
    
    update.message.reply_text(help_text, parse_mode="Markdown")

def error_handler(update: object, context: CallbackContext) -> None:
    """
    Handle errors in the dispatcher.
    Log them for debugging.
    """
    logger.error(f"Exception while handling an update: {context.error}")
