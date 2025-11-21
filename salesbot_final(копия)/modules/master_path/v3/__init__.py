from .engine import MasterPath
__all__=['MasterPath']

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
    Регистрируем телеграм-хэндлеры для модуля master_path.
    Путь Мастера - полный цикл продажи от приветствия до закрытия.
    Вызывается автозагрузчиком telegram/autoload.py.
    
    Теперь доступ через главное меню (кнопки), команды убраны для обычных пользователей.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    # Добавляем только callback handlers для inline кнопок
    @dp.callback_query(lambda c: c.data == "mp_reset")
    async def _callback_mp_reset(callback: types.CallbackQuery):
        """Начать тренировку заново"""
        from .engine import MasterPath
        
        user_id = str(callback.from_user.id)
        mp = MasterPath(user_id)
        mp._reset()
        
        await callback.message.edit_text(
            "🔄 <b>Тренировка сброшена</b>\n\n"
            "Начинаем с начала! Этап: Приветствие\n\n"
            "💬 Напиши свой вариант приветствия клиента.",
            parse_mode="HTML"
        )
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "mp_status")
    async def _callback_mp_status(callback: types.CallbackQuery):
        """Посмотреть текущий прогресс"""
        from .engine import MasterPath
        
        user_id = str(callback.from_user.id)
        mp = MasterPath(user_id)
        state = mp.snapshot()
        
        stages_ru = {
            "greeting": "Приветствие",
            "qualification": "Квалификация",
            "support": "Поддержка",
            "offer": "Предложение",
            "demo": "Демо",
            "final": "Закрытие",
            "done": "Завершено"
        }
        
        stage_name = stages_ru.get(state['stage'], state['stage'])
        history_count = len(state.get('history', []))
        
        status_text = (
            f"📊 <b>Статус тренировки</b>\n\n"
            f"📍 Этап: <b>{stage_name}</b>\n"
            f"💬 Реплик отправлено: {history_count}\n\n"
            "Продолжай тренировку, отправляя свои варианты реплик!"
        )
        
        await callback.message.edit_text(status_text, parse_mode="HTML")
        await callback.answer()
