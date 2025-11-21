
from fastapi import APIRouter
from .engine import MasterPath

router = APIRouter(prefix="/master_path/v3", tags=["master_path"])

@router.post("/start/{sid}")
async def start(sid: str):
    mp = MasterPath(sid)
    mp.reset()
    return {"ok": True, "sid": sid}

@router.post("/handle/{sid}")
async def handle(sid: str, text: str):
    mp = MasterPath(sid)
    return mp.handle(text)

@router.get("/snapshot/{sid}")
async def snapshot(sid: str):
    mp = MasterPath(sid)
    return mp.snapshot()

@router.post("/reset/{sid}")
async def reset(sid: str):
    mp = MasterPath(sid)
    return mp.reset()
