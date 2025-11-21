
from fastapi import APIRouter
from .engine import DragonEngine

router = APIRouter(prefix="/sleeping_dragon/v4", tags=["sleeping_dragon"])

@router.post("/start/{sid}")
async def start(sid:str):
    eng=DragonEngine(sid)
    eng.reset()
    return {"ok":True,"sid":sid}

@router.post("/handle/{sid}")
async def handle(sid:str, text:str):
    eng=DragonEngine(sid)
    return eng.handle(text)

@router.get("/snapshot/{sid}")
async def snapshot(sid:str):
    eng=DragonEngine(sid)
    return eng.snapshot()
