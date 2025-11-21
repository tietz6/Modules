
import os, json, time
from typing import Dict, Any, List, Optional

BASE = os.path.dirname(__file__)
CFG = os.path.join(BASE, "data", "config.json")
SUB = os.path.join(BASE, "data", "subscribers.json")
FMT = os.path.join(BASE, "data", "push_formats.json")
LOG = os.path.join(BASE, "data", "send_log.jsonl")

def _load(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.endswith(".jsonl"):
                return []
            return json.load(f)
    except Exception:
        return default

def _save(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def config()->Dict[str, Any]:
    return _load(CFG, {"enabled": False, "mock_mode": True, "bot_token_env": "TELEGRAM_BOT_TOKEN"})

def subscribers()->Dict[str, Any]:
    return _load(SUB, {})

def update_subscribers(m: Dict[str, Any]):
    _save(SUB, m)

def _render(template: str, payload: Dict[str, Any])->str:
    out = template
    for k,v in (payload or {}).items():
        out = out.replace("{{ "+k+" }}", str(v))
    return out

def _append_log(entry: Dict[str, Any]):
    # append as JSONL
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False)+"\n")

def send_push(manager_id: str, channel: str, template_key: str, payload: Dict[str, Any])->Dict[str, Any]:
    cfg = config()
    subs = subscribers()
    fmt = _load(FMT, {})
    sub = subs.get(manager_id)
    if not sub:
        return {"ok": False, "error": "not_subscribed"}
    if channel not in sub.get("channels", []):
        return {"ok": False, "error": "channel_not_allowed"}
    tpl = fmt.get(template_key, "{{ text }}")
    text = _render(tpl, payload)

    entry = {
        "ts": int(time.time()),
        "manager_id": manager_id,
        "chat_id": sub.get("chat_id"),
        "channel": channel,
        "template": template_key,
        "text": text
    }

    if cfg.get("mock_mode", True):
        _append_log(entry)
        return {"ok": True, "mock": True, "entry": entry}

    # Real send (disabled in mock-only mode). Example kept for adapter:
    try:
        import requests
        token = os.environ.get(cfg.get("bot_token_env","TELEGRAM_BOT_TOKEN"))
        if not token:
            return {"ok": False, "error": "no_token_env"}
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": sub.get("chat_id"), "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=data, timeout=10)
        _append_log({**entry, "status": r.status_code})
        return {"ok": r.ok, "status": r.status_code}
    except Exception as e:
        _append_log({**entry, "error": str(e)})
        return {"ok": False, "error": str(e)}
