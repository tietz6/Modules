"""
FastAPI routes for Sleeping Dragon module
Handles inactive client re-engagement training
"""

from fastapi import APIRouter, Request
from .engine import SleepingDragonEngine

router = APIRouter(prefix="/sleeping_dragon/v1", tags=["sleeping_dragon"])


@router.post("/start")
async def start_telegram(req: Request):
    """
    Telegram bot integration endpoint - accepts chat_id
    Starts a new sleeping dragon training session
    """
    data = await req.json()
    chat_id = data.get("chat_id")
    probe = data.get("probe", False)
    
    # Quick response for probe requests (discovery)
    if probe:
        return {"ok": True, "available": True}
    
    if not chat_id:
        return {"error": "chat_id required"}
    
    # Use chat_id as user ID for telegram users
    user_id = str(chat_id)
    engine = SleepingDragonEngine(user_id)
    result = engine.reset()
    
    # Get initial state to show user
    state = engine.snapshot()
    
    scenarios_ru = {
        "after_texts": "Клиент получил тексты песни, но не ответил",
        "after_demo": "Клиент прослушал демо, но замолчал",
        "before_payment": "Клиент обсуждал оплату, но пропал",
        "after_discussion": "Клиент обсуждал акцию 3+1, но не вернулся",
        "after_genre": "Клиент выбирал жанр, но пропал",
        "no_response": "Клиент вообще не ответил на первое сообщение"
    }
    
    behaviors_ru = {
        "busy": "Занятой, но доброжелательный",
        "cold": "Холодный, не интересуется",
        "doubtful": "Сомневается в качестве",
        "price_sensitive": "Чувствителен к цене",
        "emotional": "Эмоциональный, нерешительный",
        "interested": "Заинтересован, но забыл"
    }
    
    scenario_desc = scenarios_ru.get(state['scenario'], state['scenario'])
    behavior_desc = behaviors_ru.get(state['behavior'], state['behavior'])
    
    return {
        "ok": True,
        "user_id": user_id,
        "reply": (
            f"🐉 <b>Спящий Дракон</b> - Модуль активирован!\n\n"
            f"📍 <b>Ситуация:</b>\n{scenario_desc}\n\n"
            f"👤 <b>Тип клиента:</b> {behavior_desc}\n\n"
            f"🌊 <b>Текущая волна:</b> {state['wave']} из 3\n\n"
            f"💬 Напиши своё сообщение для возвращения клиента.\n"
            f"Я дам тебе обратную связь после каждой волны!"
        ),
        "state": state
    }


@router.post("/start/{user_id}")
async def start_session(user_id: str):
    """
    Legacy endpoint - creates new sleeping dragon session
    """
    engine = SleepingDragonEngine(user_id)
    engine.reset()
    state = engine.snapshot()
    return {"ok": True, "user_id": user_id, "state": state}


@router.post("/turn")
async def process_turn(req: Request):
    """
    Process a turn in the sleeping dragon training
    User sends a message, we provide client response and feedback
    """
    data = await req.json()
    user_id = data.get("user_id") or data.get("chat_id")
    message = data.get("message") or data.get("text")
    
    if not user_id or not message:
        return {"error": "user_id and message required"}
    
    user_id = str(user_id)
    engine = SleepingDragonEngine(user_id)
    result = engine.process_message(message)
    
    return {
        "ok": True,
        "reply": result.get("reply", ""),
        "feedback": result.get("feedback", ""),
        "state": engine.snapshot()
    }


@router.get("/state/{user_id}")
async def get_state(user_id: str):
    """Get current state of user's sleeping dragon session"""
    engine = SleepingDragonEngine(user_id)
    state = engine.snapshot()
    return {"ok": True, "state": state}


@router.post("/reset/{user_id}")
async def reset_session(user_id: str):
    """Reset user's sleeping dragon session to start fresh"""
    engine = SleepingDragonEngine(user_id)
    result = engine.reset()
    return {"ok": True, "result": result, "state": engine.snapshot()}
