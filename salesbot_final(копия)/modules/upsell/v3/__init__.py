try:
    from aiogram import types
    from aiogram.filters import Command
    from aiogram import Dispatcher
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False
    types = None
    Dispatcher = None
    Command = None

def register_telegram(dp, registry):
    """
    Регистрируем телеграм-хэндлеры для модуля upsell (допродажи).
    Вызывается автозагрузчиком telegram/autoload.py.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    @dp.message(Command("upsell", "допродажи"))
    async def _cmd_upsell(message: types.Message):
        """
        Команда /upsell - тренировка допродаж
        3 режима клиента, 3 пакета услуг
        """
        from .engine import UpsellEngine, PACKAGES
        
        user_id = str(message.from_user.id)
        
        # Set active session in router
        try:
            from telegram_message_router import set_active_session
            set_active_session(user_id, 'upsell')
        except:
            pass
        
        upsell = UpsellEngine(user_id)
        state = upsell.snapshot()
        
        modes_ru = {
            "soft": "😊 Мягкий",
            "normal": "😐 Обычный",
            "aggressive": "😠 Жесткий"
        }
        
        packages_ru = {
            "basic": "🎵 Basic - Песня + обработка",
            "premium": "🎬 Premium - Песня + видео открытка",
            "gold": "⭐ Gold - Песня + премиум история + видео"
        }
        
        mode_name = modes_ru.get(state['mode'], state['mode'])
        package_name = packages_ru.get(state['package'], state['package'])
        
        help_text = (
            "🏆 <b>Допродажи</b> - Вкус Победы\n\n"
            f"👤 Клиент: {mode_name}\n"
            f"📦 Пакет для допродажи: {package_name}\n\n"
            "💬 Клиент уже заказал базовую песню.\n"
            "Твоя задача - предложить апгрейд!\n\n"
            "Я буду отвечать как клиент через DeepSeek AI.\n\n"
            "Команды:\n"
            "/upsell_reset - новый сценарий\n"
            "/upsell_status - статистика"
        )
        
        await message.reply(help_text, parse_mode="HTML")
    
    @dp.message(Command("upsell_reset"))
    async def _cmd_upsell_reset(message: types.Message):
        """Начать с новым сценарием"""
        from .engine import UpsellEngine
        
        user_id = str(message.from_user.id)
        upsell = UpsellEngine(user_id)
        upsell._reset()
        
        # Clear active session
        try:
            from telegram_message_router import clear_active_session
            clear_active_session(user_id)
        except:
            pass
        
        await message.reply("🔄 Новый сценарий допродажи сгенерирован!\n\nИспользуй /upsell чтобы начать.")
    
    @dp.message(Command("upsell_status"))
    async def _cmd_upsell_status(message: types.Message):
        """Посмотреть статистику"""
        from .engine import UpsellEngine
        
        user_id = str(message.from_user.id)
        upsell = UpsellEngine(user_id)
        state = upsell.snapshot()
        
        modes_ru = {
            "soft": "😊 Мягкий",
            "normal": "😐 Обычный",
            "aggressive": "😠 Жесткий"
        }
        
        packages_ru = {
            "basic": "🎵 Basic",
            "premium": "🎬 Premium",
            "gold": "⭐ Gold"
        }
        
        mode_name = modes_ru.get(state['mode'], state['mode'])
        package_name = packages_ru.get(state['package'], state['package'])
        history_count = len(state.get('history', []))
        
        status_text = (
            f"📊 <b>Статус тренировки</b>\n\n"
            f"👤 Клиент: {mode_name}\n"
            f"📦 Пакет: {package_name}\n"
            f"💬 Реплик: {history_count}\n\n"
            "Продолжай работу с допродажей!"
        )
        
        await message.reply(status_text, parse_mode="HTML")