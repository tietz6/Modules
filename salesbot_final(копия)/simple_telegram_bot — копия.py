import time
import requests

# 🔥 Твой токен бота
TOKEN = "8029409301:AAGpKsSxQ_rdQJm_5kR6hk_E5JgOoQLNAgI"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# 🔗 Адрес твоего локального API (salesbot)
API_BASE = "http://127.0.0.1:8080"


def send_message(chat_id: int, text: str) -> None:
    """Отправка сообщения в Telegram."""
    try:
        resp = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        data = resp.json()
        if not data.get("ok"):
            print("Ошибка sendMessage:", data)
    except Exception as e:
        print("Исключение в send_message:", e)


def get_updates(offset: int | None = None) -> dict:
    """Получение апдейтов от Telegram."""
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset

    resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
    return resp.json()


def ask_llm(user_text: str) -> str:
    """
    Вопрос к твоему локальному LLM (DeepSeek через /voice/v1/llm/chat).
    """
    try:
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты тёплый, но очень структурный наставник по продажам "
                        "для проекта «На Счастье». Говори живо, по-человечески, "
                        "без сухого офисного стиля. Помогаешь менеджеру продавать "
                        "песни и доппродукты мягко, без давления."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ]
        }
        resp = requests.post(
            f"{API_BASE}/voice/v1/llm/chat",
            json=payload,
            timeout=20,
        )
        data = resp.json()
        # В PART_37 описан ответ вида {"output": "..."}
        answer = data.get("output") or str(data)
        return answer
    except Exception as e:
        print("Ошибка при запросе к LLM:", e)
        return "Сейчас я немного недоступен, попробуйте ещё раз чуть позже 🫂"


def main() -> None:
    print("✅ simple_telegram_bot + LLM запущен. Жду сообщения…")
    last_update_id = None

    while True:
        try:
            data = get_updates(offset=(last_update_id + 1) if last_update_id else None)

            if not data.get("ok"):
                print("Ответ Telegram не ok:", data)
                time.sleep(3)
                continue

            for upd in data.get("result", []):
                last_update_id = upd["update_id"]
                msg = upd.get("message") or {}
                chat = msg.get("chat") or {}
                chat_id = chat.get("id")
                text = msg.get("text") or ""

                if not chat_id or not text:
                    continue

                print(f"[{chat_id}] {text}")

                # Команда /start — отдельный сценарий
                if text == "/start":
                    send_message(
                        chat_id,
                        "Привет, Босс 🌸\n\n"
                        "Я твой ИИ-наставник по продажам проекта «На Счастье».\n"
                        "Можешь писать сюда сценарии, возражения клиентов, "
                        "свои ответы — я помогу переформулировать мягко и по делу.",
                    )
                    continue

                # Всё остальное — уходит в DeepSeek через твой API
                reply = ask_llm(text)
                send_message(chat_id, reply)

        except KeyboardInterrupt:
            print("🛑 Остановка по Ctrl+C")
            break
        except Exception as e:
            print("Ошибка в основном цикле:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()