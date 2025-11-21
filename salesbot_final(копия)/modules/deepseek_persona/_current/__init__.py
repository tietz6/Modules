from .routes import router
__all__=['router']

# Telegram integration
try:
    from aiogram import types
    from aiogram.dispatcher import Dispatcher
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False
    types = None
    Dispatcher = None

def register_telegram(dp, registry):
    """
    Регистрируем телеграм-хэндлеры для модуля deepseek_persona.
    Вызывается автозагрузчиком telegram/autoload.py.
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    @dp.message_handler(commands=["coach"])
    async def _cmd_coach(message: types.Message):
        """
        Команда /coach <текст> - получить совет коуча
        Пример: /coach Как ответить клиенту на возражение о цене?
        """
        from .service import persona_chat
        
        # Получаем текст после команды
        text = message.get_args()
        if not text:
            await message.reply(
                "📝 Используй команду так:\n"
                "/coach <твой вопрос>\n\n"
                "Пример: /coach Как ответить клиенту на возражение о цене?"
            )
            return
        
        try:
            # Генерируем ответ коуча
            reply = persona_chat(text, role="coach")
            await message.reply(f"🎓 Совет коуча:\n\n{reply}")
        except Exception as e:
            await message.reply(f"❌ Ошибка: {str(e)}")
    
    @dp.message_handler(commands=["stylize"])
    async def _cmd_stylize(message: types.Message):
        """
        Команда /stylize <текст> - стилизовать текст под бренд "На Счастье"
        Пример: /stylize Здравствуйте, я могу вам помочь
        """
        from .service import apply_persona
        
        # Получаем текст после команды
        text = message.get_args()
        if not text:
            await message.reply(
                "✨ Используй команду так:\n"
                "/stylize <твой текст>\n\n"
                "Пример: /stylize Здравствуйте, я могу вам помочь"
            )
            return
        
        try:
            # Стилизуем текст
            styled = apply_persona("coach", text)
            await message.reply(f"✨ Стилизованный текст:\n\n{styled}")
        except Exception as e:
            await message.reply(f"❌ Ошибка: {str(e)}")
    
    @dp.message_handler(commands=["persona_info"])
    async def _cmd_persona_info(message: types.Message):
        """
        Команда /persona_info - получить информацию о персоне бренда
        """
        from .service import load_persona
        
        try:
            persona = load_persona()
            
            # Формируем красивое сообщение
            rules = persona.get("rules", [])
            rules_text = "\n".join([f"• {rule}" for rule in rules[:5]])  # Первые 5 правил
            
            info_text = (
                "🌟 Персона бренда «На Счастье»\n\n"
                f"📋 Правила общения:\n{rules_text}\n\n"
                "💬 Доступные команды:\n"
                "• /coach <вопрос> - получить совет коуча\n"
                "• /stylize <текст> - стилизовать текст\n"
                "• /persona_info - эта справка"
            )
            
            await message.reply(info_text)
        except Exception as e:
            await message.reply(f"❌ Ошибка: {str(e)}")
