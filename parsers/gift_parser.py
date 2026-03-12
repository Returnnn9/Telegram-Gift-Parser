import re
import logging
from typing import Dict, List, Optional
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
from parsers.owner_parser import OwnerParser

logger = logging.getLogger("GiftParser")

class GiftParser:
    @staticmethod
    def is_sale_message(text: str) -> bool:
        sale_indicators = [
            r'продаж', r'sale', r'купл', r'purchas', r'buy', r'прода', r'продаётся', r'продается',
            r'ценность', r'price', r'стоимость', r'цена', r'gift sold', r'gift for sale', r'for sale'
        ]
        auction_indicators = [
            r'аукцион', r'auction', r'ставк', r'bid', r'trade'
        ]
        has_sale = any(re.search(ind, text, re.IGNORECASE) for ind in sale_indicators)
        has_auction = any(re.search(ind, text, re.IGNORECASE) for ind in auction_indicators)
        return has_sale and not has_auction

    @staticmethod
    def extract_gift_id(text: str) -> str:
        patterns = [
            r'#(\d+)',
            r'№\s*(\d+)',
            r'ID[:\s]*(\d+)',
            r'EVIEye-(\d+)',
            r'(\d{4,})'
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1)
        return '-'

    @staticmethod
    def extract_gift_name(text: str) -> str:
        explicit_patterns = [
            r'Telegram[^\n]*#\d+',
            r'[A-Za-z][^#\n]{2,50}#\d+',
        ]
        for p in explicit_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                name = m.group(0).strip()
                name = re.sub(r'#\d+', '', name).strip()
                if name:
                    return name
        lines = text.strip().split('\n')
        for line in lines[:4]:
            clean_line = re.sub(r'[#№@].*', '', line).strip()
            if (clean_line and 
                not any(clean_line.lower().startswith(k) for k in 
                       ['коллекционный', 'владелец', 'owner', 'модель', 'фон', 
                        'узор', 'количество', 'ценность', 'новый подарок', 'ссылка',
                        'функция', 'указания', 'показать подарок', 'gift sold', 'id:']) and
                2 < len(clean_line) < 100):
                return clean_line
        return 'Unknown Gift'

    @staticmethod
    def extract_price(text: str) -> str:
        patterns = [
            r'Ценность[^\d-]*([-]?\s*[\d\s,.]+)',
            r'Price[^\d-]*([-]?\s*[\d\s,.]+)',
            r'~?([-]?\s*[\d\s,.]+)\s*(?:RUB|TON|USD|₮|⬩)',
            r'([-]?\s*[\d\s,.]+\s*(?:TON|₮|⬩))'
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                price = m.group(1).replace(',', '.').replace(' ', '')
                num = re.search(r'([-]?\d+\.?\d*)', price)
                if num:
                    return num.group(1)
        return '-'

    @staticmethod
    def extract_link(text: str, entities: List = None) -> str:
        entities = entities or []
        if entities:
            for entity in entities:
                try:
                    if isinstance(entity, MessageEntityTextUrl):
                        url = getattr(entity, 'url', None)
                        if url and 't.me/' in url:
                            return url
                    elif isinstance(entity, MessageEntityUrl):
                        if hasattr(entity, 'offset') and hasattr(entity, 'length'):
                            url_text = text[entity.offset:entity.offset+entity.length]
                            if 't.me/' in url_text:
                                return url_text
                except Exception:
                    continue
        link_patterns = [
            r'https?://t\.me/[\w\-/]+',
            r'Ссылка:\s*(https?://[^\s]+)',
            r'🔗\s*(https?://[^\s]+)',
            r'ПОДАРОК\s*(https?://[^\s]+)',
            r'http[^\s]+t\.me[^\s]+'
        ]
        for p in link_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0)
        return '-'

    @staticmethod
    async def parse_gift_details(text: str, entities: List = None, source_channel: str = None) -> Dict:
        entities = entities or []
        gift_id = GiftParser.extract_gift_id(text)
        gift_name = GiftParser.extract_gift_name(text)
        link = GiftParser.extract_link(text, entities)
        
        owner_info = await OwnerParser.extract_owner_info(text, entities, link)
        price = GiftParser.extract_price(text)
        
        result = {
            'gift_id': gift_id,
            'gift_name': gift_name,
            'owner_name': owner_info['name'],
            'owner_username': owner_info['username'],
            'owner_display_name': owner_info['display_name'],
            'price': price,
            'link': link,
            'raw_text': text,
            'is_sale': GiftParser.is_sale_message(text),
            'source_channel': source_channel or '-',
        }
        
        logger.info(f"🎁 Парсинг: {gift_name} (ID: {gift_id}), Владелец: {owner_info['display_name']}")
        return result