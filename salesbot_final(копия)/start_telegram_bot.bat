@echo off
setlocal

REM === Путь к проекту ===
cd /d C:\Users\mukta\Desktop\Бот\salesbot_final(копия)

REM === Активация venv ===
call venv\Scripts\activate

REM === ТЕЛЕГРАМ ТОКЕНЫ ===
set TG_BOT_TOKEN=8029409301:AAGpKsSxQ_rdQJm_5kR6hk_E5JgOoQLNAgI
set TELEGRAM_BOT_TOKEN=8029409301:AAGpKsSxQ_rdQJm_5kR6hk_E5JgOoQLNAgI

echo ---
echo TG_BOT_TOKEN=%TG_BOT_TOKEN%
echo TELEGRAM_BOT_TOKEN=%TELEGRAM_BOT_TOKEN%
echo ---

REM === Запускаем бота ===
python telegram_bot.py

endlocal