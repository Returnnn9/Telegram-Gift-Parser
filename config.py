from typing import Set

class Config:
    
    API_ID = 
    API_HASH = 
    PHONE = 
    BOT_TOKEN = ''

   
    TARGET_CHAT_ID = ''
    SOURCE_CHANNELS = ['GiftNotification', 'mrktnotification', 'portals_notifications']

   
    MESSAGE_TEMPLATE = "Здравствуйте! Интересует ваш подарок."
    
    
    BLACKLIST_OWNERS: Set[str] = {'nft'}
    
    
    DELAY_MINUTES = 0
    DELAY_ENABLED = False
    MESSAGES_PER_SECOND = 0.3
    MAX_RETRIES = 3
    RETRY_DELAY = 5