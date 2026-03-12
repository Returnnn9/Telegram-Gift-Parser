from typing import Optional
from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import Config

class Keyboards:
    @staticmethod
    def create_message_url(username: str, message: str = None) -> Optional[str]:
        if not username or username == '-':
            return None
        clean_username = username.replace('@', '')
        base_url = f"https://t.me/{clean_username}"
        if message:
            encoded_message = quote(message)
            return f"{base_url}?text={encoded_message}"
        return base_url

    @staticmethod
    def gift_keyboard(owner_username: str, link: str, gift_id: str, user_id: int = None, db = None) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        message_text = Config.MESSAGE_TEMPLATE
        if db and user_id:
            message_text = db.get_custom_message(user_id)
        message_url = Keyboards.create_message_url(owner_username, message_text)
        if message_url:
            kb.button(text="✉️ Написать мамонту", url=message_url)
        if link != '-':
            kb.button(text="🎁 Посмотреть подарок", url=link)
        if gift_id != '-':
            kb.button(text="✅ Принять", callback_data=f"accept:{gift_id}")
        kb.adjust(1)
        return kb.as_markup()

    @staticmethod
    def accepted_keyboard(owner_username: str, link: str, user_id: int = None, db = None) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        message_text = Config.MESSAGE_TEMPLATE
        if db and user_id:
            message_text = db.get_custom_message(user_id)
        message_url = Keyboards.create_message_url(owner_username, message_text)
        if message_url:
            kb.button(text="✉️ Написать мамонту", url=message_url)
        kb.adjust(1)
        return kb.as_markup()