
from fastapi import APIRouter
from .engine import UpsellEngine

router = APIRouter(prefix="/upsell/v3", tags=["upsell"])

@router.post("/start/{sid}")
async def start(sid:str):
    eng=UpsellEngine(sid)
    eng.reset()
    return {"ok":True, "sid":sid}

@router.post("/handle/{sid}")
async def handle(sid:str, text:str):
    eng=UpsellEngine(sid)
    return eng.handle(text)

@router.get("/snapshot/{sid}")
async def snapshot(sid:str):
    eng=UpsellEngine(sid)
    return eng.snapshot()
