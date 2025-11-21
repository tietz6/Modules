
api/voice/v1 — публичные эндпоинты голосового шлюза
---------------------------------------------------
Эндпоинты:
  GET  /voice/v1/health
  POST /voice/v1/llm/chat        {messages:[{role,content}]}
  POST /voice/v1/asr/transcribe  (multipart/form-data: file)
  POST /voice/v1/tts/synth       {text, voice?} → audio/pcm (stub)

Зависимости:
  core.voice_gateway.v1 (VoicePipeline)
