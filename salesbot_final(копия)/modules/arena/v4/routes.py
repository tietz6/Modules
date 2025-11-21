from fastapi import APIRouter, Request
from .engine import ArenaEngine
router = APIRouter(prefix="/arena/v4", tags=["arena"])
@router.post("/start")
async def start_telegram(req: Request):
    """Telegram bot integration endpoint - accepts chat_id"""
    data = await req.json()
    chat_id = data.get("chat_id")
    probe = data.get("probe", False)
    
    # Quick response for probe requests (discovery)
    if probe:
        return {"ok": True, "available": True}
    
    if not chat_id:
        return {"error": "chat_id required"}
    
    # Use chat_id as session ID for telegram users
    sid = str(chat_id)
    eng = ArenaEngine(sid)
    eng.reset()
    
    # Get initial state to show user
    state = eng.snapshot()
    
    return {
        "ok": True,
        "sid": sid,
        "reply": f"🎯 Арена запущена!\n\n"
                 f"Тип клиента: {state['ctype']}\n"
                 f"Эмоция: {state['emotion']}\n"
                 f"Сложность: {state['difficulty']}\n\n"
                 f"Начинайте диалог - я буду реагировать как клиент."
    }
@router.post("/start/{sid}")
async def start(sid: str):
    eng = ArenaEngine(sid)
    eng.reset()
    return {"ok": True, "sid": sid}