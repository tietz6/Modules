
core/voice_gateway/v1 — голосовой шлюз и LLM-пайплайн
-----------------------------------------------------
Что даёт:
  - Унифицированный интерфейс: ASR, TTS, LLM
  - Встроенный клиент LLM с graceful fallback
  - Конфиг через ENV: DEEPSEEK_API_URL, DEEPSEEK_API_KEY, HTTP_TIMEOUT, HTTP_RETRIES
  - Зависимости: integrations.patch_v4.http_client (если есть), иначе pure requests
  - Встроенные стабы для офлайн-режима

Использование:
  from core.voice_gateway.v1 import VoicePipeline
  vp = VoicePipeline()
  answer = vp.llm.chat([{"role":"user","content":"Привет"}])
  # answer → str
