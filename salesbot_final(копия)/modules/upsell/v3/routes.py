from fastapi import APIRouter, Request
from .engine import UpsellEngine
router = APIRouter(prefix="/upsell/v3", tags=["upsell"])
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
    eng = UpsellEngine(sid)
    eng.reset()
    
    # Get initial state to show user
    state = eng.snapshot()
    
    return {
        "ok": True,
        "sid": sid,
        "reply": f"💰 Тренажёр допродаж запущен!\n\n"
                 f"Режим: {state['mode']}\n"
                 f"Пакет: {state['package']}\n\n"
                 f"Попробуй предложить клиенту дополнительные услуги!"
    }
@router.post("/start/{sid}")
async def start(sid:str):
    eng = UpsellEngine(sid)
    eng.reset()
    return {"ok": True, "sid": sid}