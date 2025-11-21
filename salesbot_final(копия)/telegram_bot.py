import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from api.core.registry import ModuleRegistry
from telegram.autoload import autoload_telegram_handlers

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN required")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
registry = ModuleRegistry()

# Автозагрузка модулей
autoload_telegram_handlers(dp, registry, package_name="modules")

def run():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    run()