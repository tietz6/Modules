from fastapi import APIRouter, Request
from .engine import MasterPath
router = APIRouter(prefix="/master_path/v3", tags=["master_path"])
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
    mp = MasterPath(sid)
    mp.reset()
    
    # Get initial state to show user
    state = mp.snapshot()
    
    return {
        "ok": True,
        "sid": sid,
        "reply": f"🎓 Мастер-путь запущен!\n\n"
                 f"Текущий этап: {state['stage']}\n\n"
                 f"Я буду сопровождать тебя через все этапы диалога с клиентом.\n"
                 f"Начинай с приветствия!"
    }
@router.post("/start/{sid}")
async def start(sid: str):
    mp = MasterPath(sid)
    mp.reset()
    return {"ok": True, "sid": sid}