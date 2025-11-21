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
    
    Теперь доступ через главное меню (кнопки), команды убраны для обычных пользователей.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    # Callback handlers для inline кнопок
    @dp.callback_query(lambda c: c.data == "up_reset")
    async def _callback_up_reset(callback: types.CallbackQuery):
        """Начать с новым сценарием"""
        from .engine import UpsellEngine
        
        user_id = str(callback.from_user.id)
        upsell = UpsellEngine(user_id)
        upsell._reset()
        
        state = upsell.snapshot()
        
        packages_ru = {
            "basic": "🎵 Basic",
            "premium": "🎬 Premium",
            "gold": "⭐ Gold"
        }
        
        package_name = packages_ru.get(state['package'], state['package'])
        
        await callback.message.edit_text(
            f"🔄 <b>Новый сценарий!</b>\n\n"
            f"📦 Пакет для допродажи: {package_name}\n\n"
            f"Клиент уже заказал 1 песню. Предложи апгрейд!",
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "up_status")
    async def _callback_up_status(callback: types.CallbackQuery):
        """Посмотреть статистику"""
        from .engine import UpsellEngine
        
        user_id = str(callback.from_user.id)
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
        
        await callback.message.edit_text(status_text, parse_mode="HTML")
        await callback.answer()