from fastapi import APIRouter, Request
from typing import Any, Dict

import os
import requests

from core.voice_gateway.v1 import VoicePipeline

router = APIRouter(
    prefix="/telegram_bot/v1",
    tags=["telegram_bot"]
)


def _get_token() -> str:
    """
    Берём токен бота из окружения.
    Ты уже задаёшь его в .bat:
      set TELEGRAM_BOT_TOKEN=...
      set TG_BOT_TOKEN=...
    """
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN")
        or os.environ.get("TG_BOT_TOKEN")
    )
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN / TG_BOT_TOKEN не заданы в окружении")
    return token


def _send_message(chat_id: int, text: str) -> Dict[str, Any]:
    """
    Отправка сообщения в Telegram.
    """
    token = _get_token()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    r = requests.post(url, json=payload, timeout=10)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return {"ok": r.ok, "status": r.status_code, "data": data}


@router.get("/health")
async def health():
    """
    Быстрый чек, что модуль подключен.
    """
    return {"ok": True}


@router.post("/webhook")
async def telegram_webhook(update: Dict[str, Any]):
    """
    Основной вход от Telegram (webhook).
    """
    message = update.get("message") or update.get("edited_message")
    if not message:
        # ничего не делаем, чтобы Telegram был доволен
        return {"ok": True, "skipped": True}

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if not chat_id:
        return {"ok": False, "error": "no_chat_id"}

    # --- Логика ответов ---

    # 1) Старт
    if text.startswith("/start"):
        reply_text = (
            "Добрый день! 🥰\n\n"
            "Я бот проекта «На Счастье». Мы создаём персональные песни по вашей истории: "
            "про любовь, семью, детей, важные моменты 💛\n\n"
            "Напишите, пожалуйста, кому вы хотите подарить песню — и я помогу собрать историю 🌿"
        )

    # 2) Любой другой текст — отправляем в DeepSeek через VoicePipeline
    else:
        vp = VoicePipeline()
        system_prompt = (
            "Ты тёплый, живой ассистент проекта «На Счастье».\n"
            "Отвечай коротко, по-человечески, без канцелярита, в тоне заботливого менеджера,\n"
            "который помогает человеку создать персональную песню по его истории.\n"
            "Задавай уточняющие вопросы по истории, эмоциям, поводу, но не дави на оплату."
        )
        try:
            reply_text = vp.llm.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ]
            )
        except Exception:
            # Если вдруг DeepSeek/VoicePipeline упал — не молчим.
            reply_text = (
                "Я с вами, просто немного перегружены по ИИ 🌿\n"
                "Напишите, пожалуйста: кому хотите подарить песню и к какому событию?"
            )

    # --- Отправляем ответ пользователю ---
    try:
        send_result = _send_message(chat_id, reply_text)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return {"ok": True, "sent": send_result}
