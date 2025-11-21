from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os

from .service import config, subscribers, update_subscribers, send_push, LOG


router = APIRouter(
    prefix="/telegram_push/v1",
    tags=["telegram_push"],
)

# ---------- Pydantic-модели для Swagger ----------

class SubscribeBody(BaseModel):
    manager_id: str
    chat_id: str | int
    channels: list[str] | None = None


class SendBody(BaseModel):
    manager_id: str
    channel: str = "training"
    template: str = "training.reminder"
    payload: dict | None = None


class TrainingReminderBody(BaseModel):
    manager_id: str
    when: str | None = "сегодня"
    mode: str | None = "Arena"


class PercentUpBody(BaseModel):
    manager_id: str
    percent: float | int


class ToNextBody(BaseModel):
    manager_id: str
    remain: float | int = 0
    next_percent: str | None = "—"


class DealWonBody(BaseModel):
    manager_id: str
    id: str
    amount: float | int = 0
    income: float | int = 0


class DealLostBody(BaseModel):
    manager_id: str
    id: str


# ---------- Служебные ручки ----------

@router.get("/health")
async def health():
    cfg = config() or {}
    return {
        "ok": True,
        "mock_mode": bool(cfg.get("mock_mode", False)),
    }


@router.get("/dev/me")
async def dev_me():
    cfg = config() or {}
    token = (
        cfg.get("TELEGRAM_BOT_TOKEN")
        or cfg.get("token")
        or os.getenv("TG_BOT_TOKEN")
    )

    return {
        "ok": True,
        "mock_mode": bool(cfg.get("mock_mode", False)),
        "token_present": bool(token),
    }


@router.get("/subscribers")
async def get_subs():
    return subscribers()


# ---------- Подписка и ручная отправка ----------

@router.post("/subscribe")
async def subscribe(body: SubscribeBody):
    manager_id = body.manager_id
    chat_id = str(body.chat_id)
    channels = body.channels or ["training", "kpi", "cases", "deals"]

    if not manager_id or not chat_id:
        return JSONResponse(
            {"error": "manager_id and chat_id required"},
            status_code=400,
        )

    m = subscribers()
    m[manager_id] = {
        "chat_id": chat_id,
        "channels": channels,
    }
    update_subscribers(m)
    return {"ok": True, "manager_id": manager_id}


@router.post("/send")
async def send(body: SendBody):
    return send_push(
        body.manager_id,
        body.channel,
        body.template,
        body.payload or {},
    )


@router.get("/log")
async def log():
    try:
        lines = (
            open(LOG, "r", encoding="utf-8")
            .read()
            .strip()
            .splitlines()[-200:]
        )
        return {
            "ok": True,
            "items": [json.loads(x) for x in lines if x.strip()],
        }
    except Exception:
        return {"ok": True, "items": []}


# ---------- События (event-хуки) ----------

@router.post("/events/training_reminder")
async def ev_training(body: TrainingReminderBody):
    return send_push(
        body.manager_id,
        "training",
        "training.reminder",
        {
            "when": body.when or "сегодня",
            "mode": body.mode or "Arena",
        },
    )


@router.post("/events/percent_up")
async def ev_percent_up(body: PercentUpBody):
    return send_push(
        body.manager_id,
        "kpi",
        "kpi.percent_up",
        {"percent": body.percent},
    )


@router.post("/events/to_next")
async def ev_to_next(body: ToNextBody):
    return send_push(
        body.manager_id,
        "kpi",
        "kpi.to_next",
        {
            "remain": body.remain,
            "next_percent": body.next_percent or "—",
        },
    )


@router.post("/events/deal_won")
async def ev_deal_won(body: DealWonBody):
    return send_push(
        body.manager_id,
        "deals",
        "deals.won",
        {
            "id": body.id,
            "amount": body.amount,
            "income": body.income,
        },
    )


@router.post("/events/deal_lost")
async def ev_deal_lost(body: DealLostBody):
    return send_push(
        body.manager_id,
        "deals",
        "deals.lost",
        {
            "id": body.id,
            "manager_id": body.manager_id,
        },
    )