from fastapi import APIRouter, Request
from .engine import ObjectionEngine
router = APIRouter(prefix="/objections/v3", tags=["objections"])
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
    eng = ObjectionEngine(sid)
    eng.reset()
    
    # Get initial state to show user
    state = eng.snapshot()
    
    return {
        "ok": True,
        "sid": sid,
        "reply": f"💬 Тренажёр возражений запущен!\n\n"
                 f"Персона клиента: {state['persona']}\n"
                 f"Тип возражения: {state['objection_type']}\n\n"
                 f"Я буду играть роль клиента с возражениями. Попробуй их обработать!"
    }
@router.post("/start/{sid}")
async def start(sid: str):
    eng = ObjectionEngine(sid)
    eng.reset()
    return {"ok": True, "sid": sid}