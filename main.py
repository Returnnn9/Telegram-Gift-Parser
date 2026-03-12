import asyncio
import logging
from aiogram import Bot, Dispatcher
from telethon import TelegramClient

from config import Config
from database import Database
from parsers.gift_parser import GiftParser
from handlers.bot_handlers import BotHandlers
from handlers.callback_handlers import setup_callbacks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GiftParser")

async def main():
    """Main application entry point"""
    logger.info("🚀 Запуск GiftParser Bot v3.0 с BeautifulSoup...")
    
    
    db = Database()
    parser = GiftParser()
    bot = Bot(Config.BOT_TOKEN)
    dp = Dispatcher()
    client = TelegramClient('gift_session', Config.API_ID, Config.API_HASH)
    handlers = BotHandlers(db, parser, bot, client, dp)
    
  
    await handlers.setup_handlers()
    setup_callbacks(dp, bot, db)
    
    
    await client.start(phone=Config.PHONE)
    logger.info("✅ Telethon подключен")
    
   
    asyncio.create_task(dp.start_polling(bot))
    logger.info("✅ Aiogram запущен")
    
    logger.info("🎉 Бот полностью готов к работе!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")