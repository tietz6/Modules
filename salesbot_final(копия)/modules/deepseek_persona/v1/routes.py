
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .service import load_persona, persona_chat, apply_persona

router = APIRouter(prefix="/deepseek_persona/v1", tags=["deepseek_persona"])

@router.get("/persona")
async def persona():
    return load_persona()

@router.post("/chat")
async def persona_chat_api(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "")
    role = data.get("role", "coach")
    return {"reply": persona_chat(prompt, role)}

@router.post("/stylize")
async def stylize_api(req: Request):
    data = await req.json()
    text = data.get("text", "")
    role = data.get("role", "coach")
    return {"styled": apply_persona(role, text)}
