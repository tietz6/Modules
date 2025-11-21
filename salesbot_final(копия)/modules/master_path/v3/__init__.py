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
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    @dp.message(Command("master_path", "путь_мастера"))
    async def _cmd_master_path(message: types.Message):
        """
        Команда /master_path - начать тренировку "Путь Мастера"
        Полный цикл продажи: приветствие → квалификация → поддержка → предложение → демо → закрытие
        """
        from .engine import MasterPath
        
        user_id = str(message.from_user.id)
        
        # Set active session in router
        try:
            from telegram_message_router import set_active_session
            set_active_session(user_id, 'master_path')
        except:
            pass
        
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
        
        help_text = (
            "🎯 <b>Путь Мастера</b> - Полный цикл продажи\n\n"
            f"📍 Текущий этап: <b>{stage_name}</b>\n\n"
            "📝 Этапы:\n"
            "1️⃣ Приветствие\n"
            "2️⃣ Квалификация клиента\n"
            "3️⃣ Поддержка/эмпатия\n"
            "4️⃣ Предложение\n"
            "5️⃣ Демо (образцы)\n"
            "6️⃣ Закрытие сделки\n\n"
            "💬 Напиши свой вариант реплики для этого этапа.\n"
            "Я дам тебе обратную связь от ИИ-коуча!\n\n"
            "Команды:\n"
            "/mp_next - перейти к следующему этапу\n"
            "/mp_reset - начать заново\n"
            "/mp_status - посмотреть прогресс"
        )
        
        await message.reply(help_text, parse_mode="HTML")
    
    @dp.message(Command("mp_next"))
    async def _cmd_mp_next(message: types.Message):
        """Перейти к следующему этапу"""
        from .engine import MasterPath
        
        user_id = str(message.from_user.id)
        mp = MasterPath(user_id)
        new_stage = mp.advance()
        
        stages_ru = {
            "greeting": "Приветствие",
            "qualification": "Квалификация",
            "support": "Поддержка",
            "offer": "Предложение",
            "demo": "Демо",
            "final": "Закрытие",
            "done": "Завершено"
        }
        
        stage_name = stages_ru.get(new_stage, new_stage)
        
        await message.reply(f"✅ Переход на этап: <b>{stage_name}</b>", parse_mode="HTML")
    
    @dp.message(Command("mp_reset"))
    async def _cmd_mp_reset(message: types.Message):
        """Начать тренировку заново"""
        from .engine import MasterPath
        
        user_id = str(message.from_user.id)
        mp = MasterPath(user_id)
        mp._reset()
        
        # Clear active session
        try:
            from telegram_message_router import clear_active_session
            clear_active_session(user_id)
        except:
            pass
        
        await message.reply("🔄 Тренировка сброшена. Начинаем с начала!\n\nИспользуй /master_path чтобы начать.")
    
    @dp.message(Command("mp_status"))
    async def _cmd_mp_status(message: types.Message):
        """Посмотреть текущий прогресс"""
        from .engine import MasterPath
        
        user_id = str(message.from_user.id)
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
        
        await message.reply(status_text, parse_mode="HTML")
