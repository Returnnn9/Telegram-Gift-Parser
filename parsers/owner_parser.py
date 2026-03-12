
import re
import logging
import aiohttp
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from telethon import TelegramClient

logger = logging.getLogger("GiftParser")

class OwnerParser:
    client: Optional[TelegramClient] = None

    @classmethod
    def set_client(cls, client: TelegramClient):
        cls.client = client

    @classmethod
    async def extract_owner_info(cls, text: str, entities: List = None, gift_link: str = None) -> Dict[str, str]:
        owner_info = {'username': '', 'name': '', 'display_name': ''}
        logger.info("🔍 (OwnerParser) Начало парсинга владельца через BeautifulSoup")
        
        entities = entities or []

       
        try:
            owner_name = cls._extract_owner_name(text)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при извлечении имени владельца: {e}")
            owner_name = ''
        if owner_name:
            owner_info['name'] = owner_name
            logger.info(f"✅ Имя владельца найдено: {owner_name}")

       
        if gift_link and gift_link != '-':
            try:
                username_from_gift = await cls._extract_username_from_gift_link(gift_link)
                if username_from_gift and username_from_gift.lower() != '@nft':
                    owner_info['username'] = username_from_gift
                    logger.info(f"✅ Username найден через парсинг ссылки: {username_from_gift}")
                    
                    
                    if cls.client:
                        try:
                            clean_username = owner_info['username'].lstrip('@')
                            entity = await cls.client.get_entity(clean_username)
                            first = getattr(entity, 'first_name', '') or ''
                            last = getattr(entity, 'last_name', '') or ''
                            full = (first + ' ' + last).strip()
                            if full:
                                owner_info['name'] = full
                                logger.info(f"✅ Имя получено из entity по username: {full}")
                        except Exception as e:
                            logger.debug(f"🔎 Не удалось получить имя по username '{owner_info['username']}': {e}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка парсинга ссылки на подарок: {e}")

        
        if owner_info['name'] and owner_info['username']:
            owner_info['display_name'] = f"{owner_info['name']} {owner_info['username']}"
        elif owner_info['name']:
            owner_info['display_name'] = owner_info['name']
        elif owner_info['username']:
            owner_info['display_name'] = owner_info['username']
        else:
            owner_info['display_name'] = ''

       
        for k in ('username', 'name', 'display_name'):
            if not owner_info[k]:
                owner_info[k] = '-'

        logger.info(f"📊 (OwnerParser) Результат: {owner_info}")
        return owner_info

    @classmethod
    async def _extract_username_from_gift_link(cls, gift_link: str) -> str:
        """Парсинг username из ссылки на подарок с помощью BeautifulSoup"""
        try:
            logger.info(f"🌐 Парсинг ссылки на подарок: {gift_link}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(gift_link, timeout=15, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        logger.info(f"🔍 Анализ HTML страницы подарка")
                        
                       
                        owner_elements = soup.find_all('i', class_=re.compile(r'tgme_.*_owner_photo'))
                        for owner_element in owner_elements:
                            parent_link = owner_element.find_parent('a', href=True)
                            if parent_link:
                                href = parent_link.get('href', '')
                                logger.info(f"🔗 Найдена ссылка владельца: {href}")
                                if 't.me/' in href:
                                    match = re.search(r't\.me/([a-zA-Z0-9_]{3,32})', href)
                                    if match:
                                        username = f"@{match.group(1)}"
                                        if username.lower() != '@nft':
                                            logger.info(f"✅ Username найден через owner_photo: {username}")
                                            return username
                        
                      
                        links = soup.find_all('a', href=True)
                        telegram_links = []
                        for link in links:
                            href = link.get('href', '')
                            if 't.me/' in href:
                                telegram_links.append(href)
                                match = re.search(r't\.me/([a-zA-Z0-9_]{3,32})', href)
                                if match:
                                    username = f"@{match.group(1)}"
                                    if username.lower() != '@nft':
                                        logger.info(f"✅ Username найден через поиск ссылок: {username}")
                                        return username
                        
                        if telegram_links:
                            logger.info(f"🔗 Найдены telegram ссылки: {telegram_links}")
                        
                      
                        text_content = soup.get_text()
                        matches = re.findall(r'@([a-zA-Z0-9_]{3,32})', text_content)
                        if matches:
                            for match in matches:
                                username = f"@{match}"
                                if username.lower() != '@nft':
                                    logger.info(f"✅ Username найден в тексте страницы: {username}")
                                    return username
                        
                        
                        meta_tags = soup.find_all('meta')
                        for meta in meta_tags:
                            property_attr = meta.get('property') or meta.get('name')
                            content = meta.get('content', '')
                            
                            if property_attr in ['og:title', 'twitter:title', 'title']:
                                matches = re.findall(r'@([a-zA-Z0-9_]{3,32})', content)
                                if matches:
                                    for match in matches:
                                        username = f"@{match}"
                                        if username.lower() != '@nft':
                                            logger.info(f"✅ Username найден в meta-тегах: {username}")
                                            return username
                            
                            if 't.me/' in content:
                                match = re.search(r't\.me/([a-zA-Z0-9_]{3,32})', content)
                                if match:
                                    username = f"@{match.group(1)}"
                                    if username.lower() != '@nft':
                                        logger.info(f"✅ Username найден в meta-ссылке: {username}")
                                        return username
                        
                        logger.info("❌ Username не найден при парсинге ссылки")
                    else:
                        logger.warning(f"⚠️ Ошибка HTTP {response.status} при парсинге ссылки")
                        
        except asyncio.TimeoutError:
            logger.warning("⏰ Таймаут при парсинге ссылки на подарок")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при парсинге ссылки на подарок: {e}")
        
        return ''

    @staticmethod
    def _extract_owner_name(text: str) -> str:
        """Извлекаем только имя владельца, игнорируя @nft и другие username"""
        patterns = [
            r'(?:Владелец|Продавец|Продаёт|Продает|Owner|Seller|Продаю|Продаю:)[\s:—\-]*([^\n\r@]*)',
            r'(?:Владелец|Owner)[^\S\r\n]*[\n\r][^\S\r\n]*([^\n\r@]+)',
            r'(?:Владелец|Owner)[^\S\r\n]*[:\-][^\S\r\n]*([^\n\r@]+)',
        ]
        
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if m:
                raw = m.group(1).strip()
                if re.fullmatch(r'[-—\s]+', raw) or re.search(r'скрыт|hidden|—|@nft', raw, re.IGNORECASE):
                    continue
                cleaned = re.sub(r'@[a-zA-Z0-9_]{3,32}', '', raw)
                cleaned = re.sub(r'^[^A-Za-z0-9А-Яа-я]+|[^A-Za-z0-9А-Яа-я]+$', '', cleaned)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if len(cleaned) >= 1 and cleaned.lower() != 'nft':
                    return cleaned
        
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for i, line in enumerate(lines):
            if re.search(r'Владелец|Owner|Продавец|Seller', line, re.IGNORECASE):
                if i + 1 < len(lines):
                    candidate = re.sub(r'@[A-Za-z0-9_]+', '', lines[i + 1])
                    candidate = re.sub(r'^[^A-Za-z0-9А-Яа-ja]+|[^A-Za-z0-9А-Яа-ja]+$', '', candidate).strip()
                    if candidate and not re.fullmatch(r'[-—]+', candidate) and candidate.lower() != 'nft':
                        return candidate
        return ''