"""
Запуск Telegram-бота как отдельного процесса.
- Требуется установить переменную окружения TELEGRAM_TOKEN.
- Используем aiogram v2 (Dispatcher + executor.start_polling).
"""
import os
import sys

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("ERROR: set TELEGRAM_TOKEN environment variable")
    sys.exit(1)

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# Подключаем автозагрузчик модулей для telegram
from telegram.autoload import autoload_telegram_handlers
from api.core.registry import ModuleRegistry

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    registry = ModuleRegistry()

    # Автозагрузка телеграм-хэндлеров из пакета modules
    autoload_telegram_handlers(dp, registry, package_name="modules")

    print("[run_bot] Starting polling...")
    executor.start_polling(dp, skip_updates=True)
    print("[run_bot] Stopped polling.")

if __name__ == "__main__":
    main()