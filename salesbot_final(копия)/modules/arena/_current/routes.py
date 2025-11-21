
from fastapi import APIRouter
from .engine import ArenaEngine

router = APIRouter(prefix="/arena/v4", tags=["arena"])

@router.post("/start/{sid}")
async def start(sid: str):
    eng=ArenaEngine(sid)
    eng.reset()
    return {"ok":True, "sid":sid}

@router.post("/handle/{sid}")
async def handle(sid: str, text: str):
    eng=ArenaEngine(sid)
    return eng.handle(text)

@router.get("/snapshot/{sid}")
async def snapshot(sid: str):
    eng=ArenaEngine(sid)
    return eng.snapshot()
