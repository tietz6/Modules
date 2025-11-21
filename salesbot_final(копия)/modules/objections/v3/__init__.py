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
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    @dp.message(Command("objections", "возражения"))
    async def _cmd_objections(message: types.Message):
        """
        Команда /objections - тренировка работы с возражениями
        10 типов возражений, 4 типа персон клиента
        """
        from .engine import ObjectionEngine
        
        user_id = str(message.from_user.id)
        
        # Set active session in router
        try:
            from telegram_message_router import set_active_session
            set_active_session(user_id, 'objections')
        except:
            pass
        
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
        
        help_text = (
            "🛡️ <b>Возражения</b> - Щит и Меч продажника\n\n"
            f"⚠️ Тип возражения: <b>{obj_type}</b>\n"
            f"👤 Персона клиента: {persona}\n\n"
            "💬 Клиент высказал возражение.\n"
            "Твоя задача - работать с возражением!\n\n"
            "Я буду отвечать как клиент через DeepSeek AI.\n\n"
            "Команды:\n"
            "/obj_reset - новое возражение\n"
            "/obj_status - статистика"
        )
        
        await message.reply(help_text, parse_mode="HTML")
    
    @dp.message(Command("obj_reset"))
    async def _cmd_obj_reset(message: types.Message):
        """Начать с новым возражением"""
        from .engine import ObjectionEngine
        
        user_id = str(message.from_user.id)
        obj = ObjectionEngine(user_id)
        obj._reset()
        
        # Clear active session
        try:
            from telegram_message_router import clear_active_session
            clear_active_session(user_id)
        except:
            pass
        
        await message.reply("🔄 Новое возражение сгенерировано!\n\nИспользуй /objections чтобы начать.")
    
    @dp.message(Command("obj_status"))
    async def _cmd_obj_status(message: types.Message):
        """Посмотреть статистику"""
        from .engine import ObjectionEngine
        
        user_id = str(message.from_user.id)
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
        
        await message.reply(status_text, parse_mode="HTML")
