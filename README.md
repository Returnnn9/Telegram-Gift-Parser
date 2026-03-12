# 🎁 Telegram Gift Parser v3.0

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange.svg?style=for-the-badge&logo=telegram)](https://docs.aiogram.dev/)
[![Telethon](https://img.shields.io/badge/Telethon-Client-blue.svg?style=for-the-badge)](https://docs.telethon.dev/)

[🇷🇺 Русский](#-описание-проекта) | [🇺🇸 English](#-project-overview)

---

## 🇷🇺 Описание проекта

**Telegram Gift Parser** — это бот для парсинга подарков и в Telegram. Бот в реальном времени мониторит указанные каналы, ловит сообщения о продаже и мгновенно извлекает всю подноготную: от ID подарка до скрытых данных владельца.

### ✨ Ключевые фишки
- 🕵️‍♂️ **Deep Parsing**: Извлечение данных владельца через BeautifulSoup, даже если они запрятаны.
- ⚡ **Hybrid Engine**: Сочетание мощи **Telethon** (для мониторинга) и гибкости **Aiogram** (для управления).
- 🛡️ **Система фильтрации**: Встроенный черный список и автоматическое игнорирование `@nft`.
- 🧠 **Умная база**: Защита от дубликатов и кэширование данных в SQLite.
- 💬 **Персонализация**: Настройка кастомных сообщений для "мамонтов" (потенциальных продавцов).

### 🛠 Стек технологий
- **Core:** Python 3.10+
- **Bot logic:** Aiogram 3
- **Scraping:** Telethon + BeautifulSoup4
- **Database:** SQLite3
- **Logging:** Advanced logging system

---

## 🇺🇸 Project Overview

**Telegram Gift Parser** is a state-of-the-art tool designed for Telegram gift hunters. The bot monitors designated channels in real-time, intercepts sale announcements, and instantly extracts all relevant details: from gift IDs to hidden owner information.

### ✨ Key Features
- 🕵️‍♂️ **Deep Parsing**: Extracts owner details using BeautifulSoup, bypassing standard limitations.
- ⚡ **Hybrid Engine**: Combines the power of **Telethon** (for monitoring) with the flexibility of **Aiogram** (for management).
- 🛡️ **Filtering System**: Integrated blacklist and automatic `@nft` exclusion.
- 🧠 **Smart Database**: Duplicate protection and data caching using SQLite.
- 💬 **Personalization**: Custom messaging setup for potential sellers ("mammoths").

### 🛠 Tech Stack
- **Core:** Python 3.10+
- **Bot logic:** Aiogram 3
- **Scraping:** Telethon + BeautifulSoup4
- **Database:** SQLite3
- **Logging:** Advanced logging system

---

## 🚀 Быстрый старт / Quick Start

1. **Клонируйте репозиторий / Clone the repo:**
   ```bash
   git clone https://github.com/Returnnn9/Telegram-Gift-Parser.git
   cd Telegram-Gift-Parser
   ```

2. **Установите зависимости / Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте `config.py` / Configure `config.py`:**
   Заполните ваши `API_ID`, `API_HASH` и `BOT_TOKEN`.

4. **Запустите / Run:**
   ```bash
   python main.py
   ```

---

## 🎮 Команды / Commands

- `/start` — Панель управления / Control panel
- `/setmsg` — Установить текст сообщения / Set custom message
- `/blacklist` — Добавить в ЧС / Add to blacklist
- `/status` — Статистика системы / System stats

---

<p align="center">
  <i>Developed with ❤️ for the Telegram Community</i>
</p>
