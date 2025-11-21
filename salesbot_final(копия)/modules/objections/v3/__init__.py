from .engine import ObjectionEngine
__all__=['ObjectionEngine']

# Telegram integration
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
    Регистрируем телеграм-хэндлеры для модуля objections (работа с возражениями).
    Вызывается автозагрузчиком telegram/autoload.py.
    
    Теперь доступ через главное меню (кнопки), команды убраны для обычных пользователей.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    # Callback handlers для inline кнопок
    @dp.callback_query(lambda c: c.data == "obj_reset")
    async def _callback_obj_reset(callback: types.CallbackQuery):
        """Начать с новым возражением"""
        from .engine import ObjectionEngine
        
        user_id = str(callback.from_user.id)
        obj = ObjectionEngine(user_id)
        obj._reset()
        
        state = obj.snapshot()
        
        objection_types_ru = {
            "price": "💰 Цена",
            "trust": "🤝 Недоверие",
            "hurry": "⏰ Спешка",
            "think": "🤔 Подумать",
            "ask_spouse": "👥 Спросить супруга",
            "scam_fear": "⚠️ Страх обмана",
            "too_expensive": "💸 Слишком дорого",
            "not_needed": "🚫 Не нужно",
            "later": "📅 Позже",
            "competitor": "🏪 Конкурент"
        }
        
        obj_type = objection_types_ru.get(state['objection_type'], state['objection_type'])
        
        await callback.message.edit_text(
            f"🔄 <b>Новое возражение!</b>\n\n"
            f"⚠️ Тип: {obj_type}\n\n"
            f"Начинай работу с возражением!",
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "obj_status")
    async def _callback_obj_status(callback: types.CallbackQuery):
        """Посмотреть статистику"""
        from .engine import ObjectionEngine
        
        user_id = str(callback.from_user.id)
        obj = ObjectionEngine(user_id)
        state = obj.snapshot()
        
        objection_types_ru = {
            "price": "💰 Цена",
            "trust": "🤝 Недоверие",
            "hurry": "⏰ Спешка",
            "think": "🤔 Подумать",
            "ask_spouse": "👥 Спросить супруга",
            "scam_fear": "⚠️ Страх обмана",
            "too_expensive": "💸 Слишком дорого",
            "not_needed": "🚫 Не нужно",
            "later": "📅 Позже",
            "competitor": "🏪 Конкурент"
        }
        
        personas_ru = {
            "stranger": "😶 Холодный",
            "calm": "😌 Спокойный",
            "aggressive": "😠 Агрессивный",
            "funny": "😄 С юмором"
        }
        
        obj_type = objection_types_ru.get(state['objection_type'], state['objection_type'])
        persona = personas_ru.get(state['persona'], state['persona'])
        history_count = len(state.get('history', []))
        
        status_text = (
            f"📊 <b>Статус тренировки</b>\n\n"
            f"⚠️ Возражение: <b>{obj_type}</b>\n"
            f"👤 Персона: {persona}\n"
            f"💬 Реплик: {history_count}\n\n"
            "Продолжай работу с возражением!"
        )
        
        await callback.message.edit_text(status_text, parse_mode="HTML")
        await callback.answer()
