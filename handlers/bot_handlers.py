
import time
import asyncio
import logging
from typing import Dict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from telethon import TelegramClient, events

from config import Config
from database import Database
from parsers.gift_parser import GiftParser
from parsers.owner_parser import OwnerParser
from keyboards import Keyboards

logger = logging.getLogger("GiftParser")

class BotHandlers:
    def __init__(self, db: Database, parser: GiftParser, bot: Bot, client: TelegramClient, dp: Dispatcher):
        self.db = db
        self.parser = parser
        self.bot = bot
        self.client = client
        self.dp = dp
        self.message_queue = asyncio.Queue()
        self.is_processing = False

    def escape_html(self, text: str) -> str:
        if text is None:
            return ""
        return (text.replace('&', '&amp;')
                  .replace('<', '&lt;')
                  .replace('>', '&gt;')
                  .replace('"', '&quot;'))

    async def setup_handlers(self):
        """Setup all bot handlers"""
        # Setup command handlers
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_setmsg, Command("setmsg"))
        self.dp.message.register(self.cmd_blacklist, Command("blacklist"))
        self.dp.message.register(self.cmd_whitelist, Command("whitelist"))
        self.dp.message.register(self.cmd_show_blacklist, Command("show_blacklist"))
        self.dp.message.register(self.cmd_clear_owners, Command("clear_owners"))
        self.dp.message.register(self.cmd_clear_processed, Command("clear_processed"))
        self.dp.message.register(self.cmd_status, Command("status"))

        # Setup telethon handlers
        self.client.add_event_handler(self.telethon_new_message, events.NewMessage(chats=Config.SOURCE_CHANNELS))

    async def telethon_new_message(self, event):
        """Handle new messages from monitored channels"""
        await self.handle_gift_message(event)

    async def cmd_start(self, msg: types.Message):
        await msg.answer(
            "🤖 <b>GiftParser Bot v3.0</b>\n\n"
            "📡 <b>Функции:</b>\n"
            "• Парсинг владельца ТОЛЬКО через BeautifulSoup\n"
            "• Игнорирование @nft и черный список\n"
            "• Защита от дубликатов владельцев\n"
            "• Кастомные сообщения для мамонтов\n\n"
            "💡 <b>Команды:</b>\n"
            "/setmsg текст - установить свой текст\n"
            "/blacklist username - добавить в ЧС\n"
            "/whitelist username - удалить из ЧС\n"
            "/show_blacklist - показать ЧС\n"
            "/clear_owners - очистить владельцев\n"
            "/clear_processed - очистить всё\n"
            "/status - статус системы",
            parse_mode="HTML"
        )

    async def cmd_setmsg(self, msg: types.Message):
        text = msg.text.replace('/setmsg', '').strip()
        if not text:
            await msg.answer(
                "❌ Укажите текст после команды\n"
                f"Пример: /setmsg Привет! Хочу купить подарок\n\n"
                f"Текущий текст:\n<code>{self.escape_html(self.db.get_custom_message(msg.from_user.id))}</code>",
                parse_mode="HTML"
            )
            return
        
        self.db.set_custom_message(msg.from_user.id, text)
        await msg.answer(
            f"✅ Ваш текст установлен:\n<code>{self.escape_html(text)}</code>\n\n"
            "Теперь при нажатии 'Написать мамонту' будет использоваться этот текст",
            parse_mode="HTML"
        )

    async def cmd_blacklist(self, msg: types.Message):
        username = msg.text.replace('/blacklist', '').strip().replace('@', '')
        if not username:
            await msg.answer("❌ Укажите username\nПример: /blacklist username")
            return
        
        self.db.add_to_blacklist(username)
        await msg.answer(f"✅ @{username} добавлен в черный список")

    async def cmd_whitelist(self, msg: types.Message):
        username = msg.text.replace('/whitelist', '').strip().replace('@', '')
        if not username:
            await msg.answer("❌ Укажите username\nПример: /whitelist username")
            return
        
        self.db.remove_from_blacklist(username)
        await msg.answer(f"✅ @{username} удален из черного списка")

    async def cmd_show_blacklist(self, msg: types.Message):
        if not Config.BLACKLIST_OWNERS:
            await msg.answer("📋 Черный список пуст")
            return
        
        blacklist_text = "\n".join([f"• @{u}" for u in sorted(Config.BLACKLIST_OWNERS)])
        await msg.answer(
            f"🚫 <b>Черный список ({len(Config.BLACKLIST_OWNERS)}):</b>\n\n{blacklist_text}",
            parse_mode="HTML"
        )

    async def cmd_clear_owners(self, msg: types.Message):
        self.db.clear_owners()
        await msg.answer("✅ Список обработанных владельцев очищен")

    async def cmd_clear_processed(self, msg: types.Message):
        self.db.clear_processed()
        await msg.answer("✅ База полностью очищена")

    async def cmd_status(self, msg: types.Message):
        s = self.db.get_stats()
        await msg.answer(
            f"📊 <b>Статус системы</b>\n\n"
            f"🎁 Обработано подарков: {s['processed_gifts']}\n"
            f"📨 Обработано сообщений: {s['processed_messages']}\n"
            f"👤 Обработано владельцев: {s['processed_owners']}\n"
            f"✅ Принято заявок: {s['accepted_logs']}\n"
            f"🚫 Черный список: {s['blacklist_size']}\n"
            f"💾 Кэш владельцев: {s['cached_owners']}",
            parse_mode="HTML"
        )

    async def safe_send_message(self, gift_info: Dict, message_id: int, user_id: int = None) -> bool:
        current_time = time.time()
        time_since_last_message = current_time - self.db.last_message_time
        
        required_delay = 1 / Config.MESSAGES_PER_SECOND if Config.MESSAGES_PER_SECOND else 0
        if time_since_last_message < required_delay and required_delay > 0:
            wait_time = required_delay - time_since_last_message
            await asyncio.sleep(wait_time)
        
        gift_id = gift_info['gift_id']
        owner_username = gift_info['owner_username']
        owner_display_name = gift_info['owner_display_name']
        link = gift_info['link']

        self.db.cache_owner_info(gift_id, {
            'username': owner_username,
            'display_name': owner_display_name,
            'link': link
        })

        for attempt in range(Config.MAX_RETRIES):
            try:
                msg_text = self.format_gift_message(gift_info)
                keyboard = Keyboards.gift_keyboard(owner_username, link, gift_id, user_id, self.db)
                
                sent = await self.bot.send_message(
                    chat_id=Config.TARGET_CHAT_ID,
                    text=msg_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                
                self.db.accept_log(
                    gift_id, 
                    worker_username='-', 
                    message_id=sent.message_id, 
                    owner_username=owner_username,
                    link=link
                )
                
                self.db.last_message_time = time.time()
                logger.info(f"✅ Отправлен подарок #{gift_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки (попытка {attempt + 1}): {e}")
                await asyncio.sleep(Config.RETRY_DELAY)
        
        logger.error(f"❌ Не удалось отправить подарок #{gift_id}")
        return False

    def format_gift_message(self, g: Dict) -> str:
        gift_name = self.escape_html(g['gift_name'])
        gift_id = self.escape_html(g['gift_id'])
        price = self.escape_html(g['price'])
        owner_display_name = self.escape_html(g['owner_display_name'])
        link = self.escape_html(g['link'])
        source_channel = self.escape_html(g.get('source_channel', '-'))

        lines = [
            f"🎁 <b>{gift_name}</b>",
            f"🆔 ID: <code>#{gift_id}</code>"
        ]

        if g['price'] != '-':
            lines.append(f"💰 Ценность: {price} TON")
        
        if g['owner_display_name'] != '-':
            lines.append(f"👤 Владелец: {owner_display_name}")
        else:
            lines.append("👤 Владелец: Не указан")

        if g['link'] != '-':
            lines.append(f"🔗 {link}")

        if source_channel != '-':
            lines.append(f"📢 Канал: {source_channel}")

        return "\n".join(lines)

    async def handle_gift_message(self, event):
        try:
            message_id = event.message.id
            text = event.message.message or ""
            entities = event.message.entities or []

            source_channel = "-"
            try:
                if hasattr(event.chat, "username") and event.chat.username:
                    source_channel = event.chat.username
                elif hasattr(event.chat, "title") and event.chat.title:
                    source_channel = event.chat.title
                elif hasattr(event.chat, "id"):
                    source_channel = str(event.chat.id)
            except Exception:
                pass

            if not text.strip():
                return

            logger.info(f"🔍 Анализ сообщения {message_id}")

            gift_info = await self.parser.parse_gift_details(text, entities, source_channel=source_channel)

            if not gift_info.get('is_sale', False):
                logger.info(f"⏭ Пропуск: не продажа")
                return

            owner_username = gift_info.get('owner_username', '-')
            owner_name = gift_info.get('owner_name', '-')
            if (owner_username == '-' or not owner_username) and (owner_name == '-' or not owner_name):
                logger.info(f"⏭ Пропуск: владелец скрыт")
                return

            check_username = owner_username if owner_username and owner_username != '-' else owner_name
            if self.db.is_owner_blacklisted(check_username):
                logger.info(f"🚫 Пропуск: владелец {check_username} в черном списке")
                return

            if owner_username and owner_username != '-' and self.db.is_owner_processed(owner_username):
                logger.info(f"⏭ Пропуск: владелец {owner_username} уже обработан")
                return
            if owner_name and owner_name != '-' and self.db.is_owner_processed(owner_name):
                logger.info(f"⏭ Пропуск: владелец {owner_name} уже обработан")
                return

            if self.db.is_message_processed(message_id):
                logger.info(f"⏭ Пропуск: сообщение уже обработано")
                return

            gift_id = gift_info['gift_id']
            if gift_id != '-' and self.db.is_gift_processed(gift_id):
                logger.info(f"⏭ Пропуск: подарок #{gift_id} уже обработан")
                return

            self.db.add_processed_message(message_id)
            if gift_id != '-':
                self.db.add_processed_gift(gift_id)

            if owner_username and owner_username != '-':
                self.db.add_processed_owner(owner_username)
            elif owner_name and owner_name != '-':
                self.db.add_processed_owner(owner_name)

            await self.message_queue.put((gift_info, message_id))
            if not self.is_processing:
                self.is_processing = True
                asyncio.create_task(self.process_queue())
        except Exception as e:
            logger.error(f"Ошибка в handle_gift_message: {e}")

    async def process_queue(self):
        while not self.message_queue.empty():
            gift_info, message_id = await self.message_queue.get()
            await self.safe_send_message(gift_info, message_id)
            
            delay = 1 / Config.MESSAGES_PER_SECOND if Config.MESSAGES_PER_SECOND else 0
            if delay > 0:
                await asyncio.sleep(delay)
            
            self.message_queue.task_done()
        
        self.is_processing = False