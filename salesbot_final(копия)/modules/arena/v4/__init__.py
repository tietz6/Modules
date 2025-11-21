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
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    @dp.message(Command("arena", "арена"))
    async def _cmd_arena(message: types.Message):
        """
        Команда /arena - тренировка с AI-клиентом
        20 типов клиентов, 5 эмоций, 3 уровня сложности
        """
        from .engine import ArenaEngine
        
        user_id = str(message.from_user.id)
        
        # Set active session in router
        try:
            from telegram_message_router import set_active_session
            set_active_session(user_id, 'arena')
        except:
            pass
        
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
        
        help_text = (
            "⚔️ <b>Арена</b> - Тренировка с AI-клиентом\n\n"
            f"👤 Тип клиента: <b>{ctype_name}</b>\n"
            f"{emotion_name}\n"
            f"🎚 Сложность: <b>{state['difficulty']}</b>\n\n"
            "💬 Начни диалог с клиентом!\n"
            "Я буду отвечать как настоящий клиент через DeepSeek AI.\n\n"
            "Команды:\n"
            "/arena_reset - новый клиент\n"
            "/arena_status - статистика"
        )
        
        await message.reply(help_text, parse_mode="HTML")
    
    @dp.message(Command("arena_reset"))
    async def _cmd_arena_reset(message: types.Message):
        """Начать с новым клиентом"""
        from .engine import ArenaEngine
        
        user_id = str(message.from_user.id)
        arena = ArenaEngine(user_id)
        arena.reset()
        
        # Clear active session
        try:
            from telegram_message_router import clear_active_session
            clear_active_session(user_id)
        except:
            pass
        
        await message.reply("🔄 Новый клиент сгенерирован!\n\nИспользуй /arena чтобы начать.")
    
    @dp.message(Command("arena_status"))
    async def _cmd_arena_status(message: types.Message):
        """Посмотреть статистику"""
        from .engine import ArenaEngine
        
        user_id = str(message.from_user.id)
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
        
        await message.reply(status_text, parse_mode="HTML")
