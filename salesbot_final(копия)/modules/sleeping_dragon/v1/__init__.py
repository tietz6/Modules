"""
Модуль Спящий Дракон - Telegram интеграция
"""

from .engine import SleepingDragonEngine
__all__ = ['SleepingDragonEngine']

# Telegram integration
try:
    from aiogram import types
    from aiogram.filters import Command
    from aiogram import Dispatcher
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False
    types = None
    Dispatcher = None
    Command = None
    InlineKeyboardMarkup = None
    InlineKeyboardButton = None


def register_telegram(dp, registry):
    """
    Регистрируем телеграм-хэндлеры для модуля sleeping_dragon.
    Работа с неактивными клиентами - 3 волны сообщений.
    Вызывается автозагрузчиком telegram/autoload.py.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    # Хранилище активных сессий: user_id -> engine
    active_sessions = {}
    
    def get_or_create_engine(user_id: str):
        """Получить или создать движок для пользователя"""
        if user_id not in active_sessions:
            active_sessions[user_id] = SleepingDragonEngine(user_id)
        return active_sessions[user_id]
    
    @dp.callback_query(lambda c: c.data == "sd_reset")
    async def _callback_sd_reset(callback: types.CallbackQuery):
        """Создать новую ситуацию"""
        user_id = str(callback.from_user.id)
        engine = get_or_create_engine(user_id)
        result = engine.reset()
        
        await callback.message.edit_text(
            f"🔄 <b>Новая ситуация:</b>\n\n"
            f"{result.get('scenario', 'Клиент неактивен')}\n\n"
            f"Начинай первую волну сообщений!",
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "sd_status")
    async def _callback_sd_status(callback: types.CallbackQuery):
        """Показать статистику"""
        user_id = str(callback.from_user.id)
        engine = get_or_create_engine(user_id)
        state = engine.snapshot()
        
        scenarios_ru = {
            "after_texts": "После текстов",
            "after_demo": "После демо",
            "before_payment": "До оплаты",
            "after_discussion": "После акции",
            "after_genre": "После жанра",
            "no_response": "Нет ответа"
        }
        
        behaviors_ru = {
            "busy": "Занятой",
            "cold": "Холодный",
            "doubtful": "Сомневающийся",
            "price_sensitive": "Ценовой",
            "emotional": "Эмоциональный",
            "interested": "Заинтересованный"
        }
        
        scenario_name = scenarios_ru.get(state['scenario'], state['scenario'])
        behavior_name = behaviors_ru.get(state['behavior'], state['behavior'])
        
        status_text = (
            f"📊 <b>Статус тренировки</b>\n\n"
            f"📍 Ситуация: {scenario_name}\n"
            f"👤 Тип клиента: {behavior_name}\n"
            f"🌊 Волна: {state['wave']} из 3\n"
            f"💬 Сообщений: {len(state.get('history', []))}\n\n"
            f"Продолжай работать с клиентом!"
        )
        
        await callback.message.edit_text(status_text, parse_mode="HTML")
        await callback.answer()
    
    # Обработка обычных текстовых сообщений внутри модуля
    # Это будет работать через роутер сообщений, если он настроен
    # Пока что создаём отдельный хендлер для команд внутри модуля
    
    @dp.message(Command("sleeping_dragon", "спящий_дракон"))
    async def _cmd_sleeping_dragon(message: types.Message):
        """
        Команда для работы с модулем Спящий Дракон.
        Обычно пользователь входит через кнопку, но команда тоже работает.
        """
        user_id = str(message.from_user.id)
        engine = get_or_create_engine(user_id)
        state = engine.snapshot()
        
        scenarios_ru = {
            "after_texts": "Клиент получил тексты песни, но не ответил",
            "after_demo": "Клиент прослушал демо, но замолчал",
            "before_payment": "Клиент обсуждал оплату, но пропал",
            "after_discussion": "Клиент обсуждал акцию 3+1, но не вернулся",
            "after_genre": "Клиент выбирал жанр, но пропал",
            "no_response": "Клиент вообще не ответил на первое сообщение"
        }
        
        behaviors_ru = {
            "busy": "Занятой, но доброжелательный",
            "cold": "Холодный, не интересуется",
            "doubtful": "Сомневается в качестве",
            "price_sensitive": "Чувствителен к цене",
            "emotional": "Эмоциональный, нерешительный",
            "interested": "Заинтересован, но забыл"
        }
        
        scenario_desc = scenarios_ru.get(state['scenario'], state['scenario'])
        behavior_desc = behaviors_ru.get(state['behavior'], state['behavior'])
        
        help_text = (
            "🐉 <b>Спящий Дракон</b>\n\n"
            f"📍 <b>Ситуация:</b>\n{scenario_desc}\n\n"
            f"👤 <b>Тип клиента:</b> {behavior_desc}\n\n"
            f"🌊 <b>Текущая волна:</b> {state['wave']} из 3\n\n"
            "💬 Напиши своё сообщение клиенту.\n"
            "Я сыграю роль клиента и дам тебе обратную связь!\n\n"
            "📝 <b>Помни о волнах:</b>\n"
            "1️⃣ Тёплое напоминание + эмпатия\n"
            "2️⃣ Ценность + эмоция/бонус\n"
            "3️⃣ Уважение + открытая дверь"
        )
        
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Новая ситуация", callback_data="sd_reset")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="sd_status")]
        ])
        
        await message.reply(help_text, reply_markup=inline_kb, parse_mode="HTML")
