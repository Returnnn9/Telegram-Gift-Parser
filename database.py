import asyncio
import time
import logging
from typing import Optional, Dict, List, Set
from config import Config

logger = logging.getLogger("GiftParser")

class Database:
    def __init__(self):
        self.processed_gifts = set()
        self.accepted_logs = {}
        self.last_message_time = 0
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        self.delayed_gifts = {}
        self.owner_cache = {}
        self.processed_messages = set()
        self.processed_owners: Set[str] = set()
        self.custom_messages: Dict[int, str] = {}

    def add_processed_gift(self, gift_id: str):
        self.processed_gifts.add(gift_id)

    def is_gift_processed(self, gift_id: str) -> bool:
        return gift_id in self.processed_gifts

    def add_processed_message(self, message_id: int):
        self.processed_messages.add(message_id)

    def is_message_processed(self, message_id: int) -> bool:
        return message_id in self.processed_messages

    def add_processed_owner(self, owner_username: str):
        clean_username = owner_username.replace('@', '').lower()
        self.processed_owners.add(clean_username)
        logger.info(f"➕ Добавлен владелец в обработанные: {clean_username}")

    def is_owner_processed(self, owner_username: str) -> bool:
        clean_username = owner_username.replace('@', '').lower()
        return clean_username in self.processed_owners

    def is_owner_blacklisted(self, owner_username: str) -> bool:
        clean_username = owner_username.replace('@', '').lower()
        return clean_username in {u.lower() for u in Config.BLACKLIST_OWNERS}

    def set_custom_message(self, user_id: int, message: str):
        self.custom_messages[user_id] = message

    def get_custom_message(self, user_id: int) -> str:
        return self.custom_messages.get(user_id, Config.MESSAGE_TEMPLATE)

    def accept_log(self, gift_id: str, worker_username: str, message_id: int | None = None, 
                   owner_username: str = '-', link: str = '-'):
        self.accepted_logs[gift_id] = {
            'worker': worker_username, 
            'message_id': message_id,
            'owner_username': owner_username,
            'link': link
        }

    def get_log_worker(self, gift_id: str):
        return self.accepted_logs.get(gift_id)

    def cache_owner_info(self, gift_id: str, owner_info: Dict):
        self.owner_cache[gift_id] = owner_info

    def get_cached_owner_info(self, gift_id: str) -> Optional[Dict]:
        return self.owner_cache.get(gift_id)

    def clear_processed(self):
        self.processed_gifts.clear()
        self.processed_messages.clear()
        self.processed_owners.clear()
        logger.info("✅ База очищена")

    def clear_owners(self):
        self.processed_owners.clear()
        logger.info("✅ Список обработанных владельцев очищен")

    def add_to_blacklist(self, username: str):
        clean_username = username.replace('@', '').lower()
        Config.BLACKLIST_OWNERS.add(clean_username)
        logger.info(f"🚫 Добавлен в черный список: {clean_username}")

    def remove_from_blacklist(self, username: str):
        clean_username = username.replace('@', '').lower()
        Config.BLACKLIST_OWNERS.discard(clean_username)
        logger.info(f"✅ Удален из черного списка: {clean_username}")

    def get_stats(self):
        return {
            'processed_gifts': len(self.processed_gifts),
            'processed_messages': len(self.processed_messages),
            'accepted_logs': len(self.accepted_logs),
            'delayed_gifts': len(self.delayed_gifts),
            'cached_owners': len(self.owner_cache),
            'processed_owners': len(self.processed_owners),
            'blacklist_size': len(Config.BLACKLIST_OWNERS)
        }