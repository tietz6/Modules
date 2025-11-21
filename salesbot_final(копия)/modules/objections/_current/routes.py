
from fastapi import APIRouter
from .engine import ObjectionEngine

router = APIRouter(prefix="/objections/v3", tags=["objections"])

@router.post("/start/{sid}")
async def start(sid: str):
    eng=ObjectionEngine(sid)
    eng.reset()
    return {"ok":True, "sid":sid}

@router.post("/handle/{sid}")
async def handle(sid: str, text: str):
    eng=ObjectionEngine(sid)
    return eng.handle(text)

@router.get("/snapshot/{sid}")
async def snapshot(sid: str):
    eng=ObjectionEngine(sid)
    return eng.snapshot()
