"""
In-memory storage for the Telegram verification bot.
Manages pending user verifications.
"""
from typing import Dict, Set
import threading
import logging

logger = logging.getLogger(__name__)

class MemberVerificationStorage:
    """
    Simple in-memory storage for pending member verifications.
    
    Stores users who need verification with the format:
    {
        chat_id: {
            user_id: {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "message_id": message_id
            }
        }
    }
    """
    def __init__(self):
        self._pending_verifications: Dict[int, Dict[int, Dict]] = {}
        self._lock = threading.RLock()
        logger.debug("Initialized member verification storage")
    
    def add_pending_verification(self, chat_id: int, user_id: int, username: str = None, 
                                first_name: str = None, last_name: str = None, message_id: int = None):
        """Add a user to the pending verification list."""
        with self._lock:
            if chat_id not in self._pending_verifications:
                self._pending_verifications[chat_id] = {}
            
            self._pending_verifications[chat_id][user_id] = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "message_id": message_id
            }
            
            logger.debug(f"Added pending verification for user {user_id} in chat {chat_id}")
    
    def remove_pending_verification(self, chat_id: int, user_id: int):
        """Remove a user from the pending verification list."""
        with self._lock:
            if chat_id in self._pending_verifications and user_id in self._pending_verifications[chat_id]:
                user_data = self._pending_verifications[chat_id].pop(user_id)
                logger.debug(f"Removed pending verification for user {user_id} in chat {chat_id}")
                return user_data
            return None
    
    def get_pending_verification(self, chat_id: int, user_id: int):
        """Get pending verification data for a user."""
        with self._lock:
            if chat_id in self._pending_verifications and user_id in self._pending_verifications[chat_id]:
                return self._pending_verifications[chat_id][user_id]
            return None
    
    def is_pending_verification(self, chat_id: int, user_id: int) -> bool:
        """Check if a user is pending verification."""
        with self._lock:
            return chat_id in self._pending_verifications and user_id in self._pending_verifications[chat_id]
    
    def get_all_pending_users(self, chat_id: int) -> Dict[int, Dict]:
        """Get all pending users for a specific chat."""
        with self._lock:
            if chat_id in self._pending_verifications:
                return self._pending_verifications[chat_id].copy()
            return {}

# Global storage instance
verification_storage = MemberVerificationStorage()
