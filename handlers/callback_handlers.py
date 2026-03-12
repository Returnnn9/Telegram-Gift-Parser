import time
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery

from keyboards import Keyboards

logger = logging.getLogger("GiftParser")

def setup_callbacks(dp: Dispatcher, bot: Bot, db):
    """Setup callback handlers"""
    
    @dp.callback_query(F.data.startswith("accept:"))
    async def on_accept(query: CallbackQuery):
        gift_id = query.data.split(":")[1]
        worker = query.from_user.username or f"id{query.from_user.id}"
        log = db.get_log_worker(gift_id)
        
        if not log:
            await query.answer("❌ Заявка не найдена", show_alert=True)
            return

        msg_id = log["message_id"]
        owner_username = log.get("owner_username", "-")
        link = log.get("link", "-")
        
        cached_owner = db.get_cached_owner_info(gift_id)
        if cached_owner:
            owner_username = cached_owner.get('username', owner_username)
            link = cached_owner.get('link', link)
        
        original_text = query.message.text or ""
        lines = original_text.split('\n')
        cleaned_lines = [line for line in lines if not line.startswith('✅ В работе:')]
        cleaned_text = '\n'.join(cleaned_lines)
        
        acceptance_info = f"\n\n✅ <b>Подарок принят</b>\n"
        acceptance_info += f"📊 Информация о принятии:\n"
        acceptance_info += f"├ Принял: @{worker}\n"
        acceptance_info += f"├ User ID: {query.from_user.id}\n"
        acceptance_info += f"└ Время принятия: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        new_text = f"{cleaned_text}{acceptance_info}"
        
        new_keyboard = Keyboards.accepted_keyboard(owner_username, link, query.from_user.id, db)
        
        try:
            await bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=msg_id,
                text=new_text,
                reply_markup=new_keyboard,
                parse_mode="HTML"
            )
            
            db.accept_log(
                gift_id, 
                worker_username=worker, 
                message_id=msg_id,
                owner_username=owner_username,
                link=link
            )
            
            await query.answer(f"✅ Вы взяли в работу #{gift_id}")
            logger.info(f"✅ Подарок #{gift_id} принят воркером @{worker}")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении сообщения: {e}")
            await query.answer("❌ Не удалось обновить сообщение", show_alert=True)