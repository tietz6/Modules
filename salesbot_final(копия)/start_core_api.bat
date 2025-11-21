@echo off
setlocal

REM --- переходим в папку с проектом ---
cd /d "%~dp0"

REM --- активируем виртуальное окружение ---
call venv\Scripts\activate

REM === КЛЮЧИ И НАСТРОЙКИ ===

REM DeepSeek
set DEEPSEEK_API_KEY=sk-4de54b0041b44cf193b22cf21f028be7
set DEEPSEEK_MODEL=deepseek-chat
REM Можно не задавать, у нас в коде есть значение по умолчанию,
REM но если хочешь явно:
REM set DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

REM Голос (ASR)
set VOICE_API_KEY=10da831f2d514801a47c79b8e3e68ebb

REM Телеграм-бот для пушей
REM === ТЕЛЕГРАМ ДЛЯ PUSH ===
set TELEGRAM_BOT_TOKEN=8029409301:AAGpKsSxQ_rdQJm_5kR6hk_E5JgOoQLNAgI
set TG_BOT_TOKEN=8029409301:AAGpKsSxQ_rdQJm_5kR6hk_E5JgOoQLNAgI
set TELEGRAM_PUSH_MOCK_MODE=false

REM === ЗАПУСК API ===
start "SALESBOT_API" python -m uvicorn startup:app --host 0.0.0.0 --port 8080 --reload
python main.py

REM === Запускаем Telegram-бота в отдельном окне ===
start "SALESBOT_BOT" python simple_telegram_bot.py

pause
endlocal