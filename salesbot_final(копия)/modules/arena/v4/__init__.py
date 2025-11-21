from .engine import ArenaEngine
__all__=['ArenaEngine']

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
    Регистрируем телеграм-хэндлеры для модуля arena (практика с AI-клиентами).
    Вызывается автозагрузчиком telegram/autoload.py.
    
    Теперь доступ через главное меню (кнопки), команды убраны для обычных пользователей.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    # Добавляем только callback handlers для inline кнопок
    @dp.callback_query(lambda c: c.data == "arena_reset")
    async def _callback_arena_reset(callback: types.CallbackQuery):
        """Начать с новым клиентом"""
        from .engine import ArenaEngine
        
        user_id = str(callback.from_user.id)
        arena = ArenaEngine(user_id)
        arena.reset()
        
        state = arena.snapshot()
        
        client_types_ru = {
            "silent": "Молчаливый", "talkative": "Разговорчивый", "rude": "Грубый",
            "polite": "Вежливый", "busy": "Занятой", "rich": "Богатый",
            "poor": "Экономный", "jokester": "Шутник", "logic": "Логик",
            "emotional": "Эмоциональный", "skeptic": "Скептик", "warm": "Теплый",
            "cold": "Холодный", "doubtful": "Сомневающийся", "dominant": "Доминантный",
            "passive": "Пассивный", "detail": "Детальный", "fast": "Быстрый",
            "slow": "Медлительный", "expert": "Эксперт"
        }
        
        ctype_name = client_types_ru.get(state['ctype'], state['ctype'])
        
        await callback.message.edit_text(
            f"🔄 <b>Новый клиент сгенерирован!</b>\n\n"
            f"👤 Тип: {ctype_name}\n\n"
            f"Начинай диалог!",
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "arena_status")
    async def _callback_arena_status(callback: types.CallbackQuery):
        """Посмотреть статистику"""
        from .engine import ArenaEngine
        
        user_id = str(callback.from_user.id)
        arena = ArenaEngine(user_id)
        state = arena.snapshot()
        
        client_types_ru = {
            "silent": "Молчаливый", "talkative": "Разговорчивый", "rude": "Грубый",
            "polite": "Вежливый", "busy": "Занятой", "rich": "Богатый",
            "poor": "Экономный", "jokester": "Шутник", "logic": "Логик",
            "emotional": "Эмоциональный", "skeptic": "Скептик", "warm": "Теплый",
            "cold": "Холодный", "doubtful": "Сомневающийся", "dominant": "Доминантный",
            "passive": "Пассивный", "detail": "Детальный", "fast": "Быстрый",
            "slow": "Медлительный", "expert": "Эксперт"
        }
        
        emotions_ru = {
            "calm": "😌 Спокоен",
            "neutral": "😐 Нейтрален",
            "annoyed": "😠 Раздражен",
            "angry": "😡 Зол",
            "excited": "😄 Взволнован"
        }
        
        ctype_name = client_types_ru.get(state['ctype'], state['ctype'])
        emotion_name = emotions_ru.get(state['emotion'], state['emotion'])
        round_num = state.get('meta', {}).get('round', 0)
        
        status_text = (
            f"📊 <b>Статус Арены</b>\n\n"
            f"👤 Клиент: <b>{ctype_name}</b>\n"
            f"{emotion_name}\n"
            f"🎚 Сложность: <b>{state['difficulty']}</b>\n"
            f"🔄 Раунд: {round_num}\n\n"
            "Продолжай диалог, отправляя сообщения!"
        )
        
        await callback.message.edit_text(status_text, parse_mode="HTML")
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "arena_finish")
    async def _callback_arena_finish(callback: types.CallbackQuery):
        """Завершить сессию и получить оценку"""
        await callback.message.edit_text(
            "🎯 <b>Сессия завершена!</b>\n\n"
            "Оценка производится... (функция в разработке)\n\n"
            "Скоро здесь будет подробный разбор по параметрам:\n"
            "• Empathy (эмпатия)\n"
            "• CTA (призыв к действию)\n"
            "• Timing (тайминг)\n"
            "• Clarity (ясность)\n"
            "• Value (ценность)\n"
            "• Upsell (допродажи)",
            parse_mode="HTML"
        )
        await callback.answer()
