"""
Utility functions for the Telegram verification bot.
"""
import logging
from telegram import ChatPermissions

logger = logging.getLogger(__name__)

def get_restricted_permissions():
    """
    Returns ChatPermissions with all permissions set to False
    to restrict a user from sending messages.
    """
    return ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_manage_topics=False
    )

def get_full_permissions():
    """
    Returns ChatPermissions with basic permissions set to True
    after a user has been verified.
    """
    return ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True
    )

def get_user_name(user):
    """
    Generates a user's display name based on available information.
    """
    if user.username:
        return f"@{user.username}"
    
    name_parts = []
    if user.first_name:
        name_parts.append(user.first_name)
    if user.last_name:
        name_parts.append(user.last_name)
    
    full_name = " ".join(name_parts)
    
    if full_name:
        return full_name
    
    return f"User {user.id}"

def is_admin(chat_member):
    """
    Check if a chat member has admin privileges.
    """
    if not chat_member:
        return False
    
    return chat_member.status in ("administrator", "creator")
