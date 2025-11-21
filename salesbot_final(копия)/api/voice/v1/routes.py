import os
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel

from core.voice_gateway.v1 import VoicePipeline

router = APIRouter(prefix="/voice/v1", tags=["voice"])

# Инициализируем общий пайплайн (ASR/TTS/LLM-обёртка)
pipeline = VoicePipeline()


# ---------- Модели ----------

class ChatMessage(BaseModel):
    role: str   # "user" | "assistant" | "system" | кастомные вроде "boss"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


# ---------- Настройки DeepSeek ----------

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_API_URL = os.getenv(
    "DEEPSEEK_API_URL",
    "https://api.deepseek.com/v1/chat/completions",
)


@router.get("/health")
async def health():
    """Проверка, что модуль и ключ вообще видны."""
    return {
        "ok": True,
        "model": DEEPSEEK_MODEL,
        "has_api_key": bool(DEEPSEEK_API_KEY),
    }


# ---------- LLM / DeepSeek ----------

@router.post("/llm/chat")
async def llm_chat(body: ChatRequest):
    """
    Прокси к DeepSeek chat-completions.
    Здесь мы НОРМАЛИЗУЕМ роли, чтобы не было ошибки:
    messages[0].role: unknown variant `boss`
    """
    if not DEEPSEEK_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DEEPSEEK_API_KEY не задан в переменных окружения",
        )

    # Нормализуем роли: всё, что не system/user/assistant/tool → user
    normalized_messages: List[dict] = []
    for m in body.messages:
        role = m.role
        if role not in ("system", "user", "assistant", "tool"):
            role = "user"
        normalized_messages.append({"role": role, "content": m.content})

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": normalized_messages,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                DEEPSEEK_API_URL,
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json=payload,
            )
    except Exception as e:
        # Ошибка сети / DNS / таймаут и т.п.
        raise HTTPException(status_code=500, detail=f"HTTP error: {e}")

    if resp.status_code >= 300:
        # Ошибка от самого DeepSeek (400, 401, 429 и т.д.)
        raise HTTPException(
            status_code=500,
            detail=f"DeepSeek error {resp.status_code}: {resp.text}",
        )

    data = resp.json()
    # Формат как у OpenAI-совместимого API
    try:
        content: Optional[str] = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected DeepSeek response: {e} | raw={data}",
        )

    return {"output": content}


# ---------- ASR (распознавание речи, stub) ----------

@router.post("/asr/transcribe")
async def asr_transcribe(file: UploadFile = File(...)):
    """
    ASR: принимаем audio/* файл и возвращаем распознанный текст.
    Сейчас использует stub из VoicePipeline.asr.
    """
    audio_bytes = await file.read()
    text = pipeline.asr.transcribe(audio_bytes, lang="ru")
    return {
        "ok": True,
        "text": text,
        "size": len(audio_bytes),
    }


# ---------- TTS (синтез речи, stub) ----------

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None


@router.post("/tts/synth")
async def tts_synth(payload: TTSRequest):
    """
    TTS: принимаем текст и отдаём WAV-байты.
    Сейчас это stub, но интерфейс уже правильный.
    """
    audio_bytes = pipeline.tts.synth(payload.text, voice=payload.voice or "neutral")
    return Response(content=audio_bytes, media_type="audio/wav")
