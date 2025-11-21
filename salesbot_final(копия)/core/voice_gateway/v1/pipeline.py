import os
import time
from typing import List, Dict, Optional

# Попробуем взять HTTP-клиент из integrations.patch_v4 / patch_v3
_HTTP_CLIENT = None
try:
    from integrations.patch_v4.http_client import http_post  # type: ignore
    _HTTP_CLIENT = ("v4", http_post)
except Exception:
    try:
        from integrations.patch_v3.http_client import http_post  # type: ignore
        _HTTP_CLIENT = ("v3", http_post)
    except Exception:
        _HTTP_CLIENT = None

# Фоллбек на requests (если есть)
try:
    import requests  # type: ignore
except Exception:
    requests = None  # type: ignore


def _read_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


# ---- Нормализация ролей для DeepSeek ----

_ALLOWED_ROLES = {"system", "user", "assistant", "tool"}


def _normalize_messages_for_deepseek(
    messages: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    DeepSeek принимает только роли: system / user / assistant / tool.
    Любые кастомные роли ("boss", "coach", "client_emotional" и т.п.)
    аккуратно приводим к безопасным значениям.
    """
    normalized: List[Dict[str, str]] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role not in _ALLOWED_ROLES:
            low = str(role).lower()
            if "system" in low or "meta" in low:
                safe_role = "system"
            else:
                safe_role = "user"
        else:
            safe_role = role

        normalized.append(
            {
                "role": safe_role,
                "content": content,
            }
        )

    return normalized


class _LLMClient:
    """
    Обёртка над DeepSeek (или совместимым сервисом).

    Ожидаемый API (по сути как OpenAI /chat/completions):
      POST {api_url}
      headers:
        Authorization: Bearer <key>
        Content-Type: application/json
      body:
        {
          "model": "...",
          "messages": [{ "role": "user", "content": "..." }, ...]
        }
      response:
        либо { "output": "..." }
        либо { "choices": [ { "message": { "content": "..." } } ] }
    """

    def __init__(self) -> None:
        self.api_url = _read_env(
            "DEEPSEEK_API_URL",
            "https://api.deepseek.com/v1/chat/completions",
        )
        self.api_key = _read_env("DEEPSEEK_API_KEY", None)
        self.timeout = float(_read_env("HTTP_TIMEOUT", "15"))
        self.retries = int(_read_env("HTTP_RETRIES", "2"))
        self.model = _read_env("DEEPSEEK_MODEL", "deepseek-chat")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Если ключа нет или вообще нет HTTP-клиента — локальный коуч-ответ
        if not self.api_key or (_HTTP_CLIENT is None and requests is None):
            return self._local_echo(messages)

        safe_messages = _normalize_messages_for_deepseek(messages)

        payload: Dict[str, object] = {
            "model": self.model,
            "messages": safe_messages,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_err: Optional[str] = None

        for _ in range(max(1, self.retries)):
            try:
                # Вариант через integrations.patch_*
                if _HTTP_CLIENT is not None:
                    _, http_post = _HTTP_CLIENT
                    resp = http_post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout,
                    )
                    data = resp if isinstance(resp, dict) else {}
                else:
                    # Вариант через requests
                    assert requests is not None  # для type checker
                    r = requests.post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout,
                    )
                    data = r.json()

                if isinstance(data, dict):
                    # Вариант { "output": "..." }
                    if "output" in data and isinstance(data["output"], str):
                        return data["output"]

                    # Вариант OpenAI-стиля с choices
                    if "choices" in data and data["choices"]:
                        ch = data["choices"][0]
                        msg = (ch.get("message") or {}).get("content")
                        if isinstance(msg, str):
                            return msg

                last_err = f"unexpected response: {str(data)[:200]}"
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
                time.sleep(0.25)

        # Если всё упало — аккуратно деградируем
        return self._local_echo(messages, error=last_err)

    def _local_echo(
        self,
        messages: List[Dict[str, str]],
        error: Optional[str] = None,
    ) -> str:
        """
        Локальный коуч, когда нет сети / ключа / API.
        Даёт мягкий совет по последнему сообщению.
        """
        text = ""
        for m in reversed(messages):
            if m.get("role") in ("user", "assistant"):
                text = m.get("content", "")
                break

        prefix = "Совет коуча: "
        base = (
            "задавай уточняющие вопросы, показывай ценность и веди к следующему шагу."
        )

        if not text:
            if error:
                return prefix + base + f" (локальный режим, причина: {error[:80]})"
            return prefix + base

        low = text.lower()
        tips = []

        if any(w in low for w in ["цена", "дорого", "сколько"]):
            tips.append(
                "переведи разговор к ценности результата и разложи стоимость на шаги/части."
            )
        if "?" not in text:
            tips.append(
                "добавь 1–2 уточняющих вопроса, чтобы лучше понять человека."
            )
        if len(text) < 16:
            tips.append(
                "расширь ответ ещё 1–2 фразами, чтобы создать больше доверия."
            )

        if not tips:
            tips.append(base)

        if error:
            tips.append("(локальный режим LLM, причина: " + error[:80] + ")")

        return prefix + " ".join(tips)


class _ASRStub:
    def transcribe(self, audio_bytes: bytes, lang: str = "ru") -> str:
        return "[asr-stub] распознавание недоступно в офлайн-режиме"


class _TTSStub:
    def synth(self, text: str, voice: str = "neutral") -> bytes:
        return b"[tts-stub]"


class VoicePipeline:
    """
    Основной фасад голосового шлюза.
    Содержит:
      - llm: чат-API (DeepSeek + фоллбек)
      - asr: распознавание (стаб)
      - tts: синтез (стаб)
    """

    def __init__(self) -> None:
        self.llm = _LLMClient()
        self.asr = _ASRStub()
        self.tts = _TTSStub()