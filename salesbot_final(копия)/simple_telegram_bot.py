# improved simple_telegram_bot.py — auto-discover backend modules and probe start endpoints
# Replace your existing file with this one.
import os
import time
import requests
import json
import re
from typing import Dict, Tuple, List

# ============ SETTINGS ============
BACKEND_URL = (os.getenv("BACKEND_URL") or "http://127.0.0.1:8080").rstrip("/")
# token names supported by your bat files; add more if your bat uses another name
TOKEN = (
    os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TG_BOT_TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
    or os.getenv("TOKEN")
)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # optional

if not TOKEN:
    print("❌ Нет TELEGRAM токена в переменных окружения. Проверьте start_core_api.bat")
    time.sleep(60)
    raise SystemExit(1)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Session memory: chat_id -> {"mode": "dialog"/None, "sid": str|None}
SESSIONS: Dict[int, dict] = {}

# Logging
def log(*args):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{ts}] [BOT]", *args)

# Telegram helpers
def send_message(chat_id: int, text: str):
    """Send text to Telegram (safe)."""
    try:
        resp = requests.post(
            BASE_URL + "/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
        if not resp.ok:
            log("Ошибка sendMessage:", resp.status_code, resp.text)
    except Exception as e:
        log("Ошибка отправки в Telegram:", e)

def get_session(chat_id: int):
    if chat_id not in SESSIONS:
        SESSIONS[chat_id] = {"mode": None, "sid": None}
    return SESSIONS[chat_id]

# ===================== Legacy trainer endpoints - REMOVED =====================
# trainer_dialog_engine has been removed from the project
# Use master_path module instead via /master_path command

# ===================== MODULE DISCOVERY & PROBING =====================

# Candidate endpoint patterns (tried in order)
PROBE_PATTERNS = [
    "/{module}/{version}/start",
    "/{module}/{version}/start_session",
    "/{module}/{version}/run",
    "/{module}/{version}/init",
    "/{module}/start",
]

def fetch_routes_summary() -> Dict:
    """
    Query backend endpoint that router_autoload provides:
    /api/public/v1/routes_summary -> {"attached": [...], "errors":[...]}
    This tells us which route modules were attached to backend.
    """
    url = BACKEND_URL + "/api/public/v1/routes_summary"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log("Не удалось запросить routes_summary:", e)
        return {}

def parse_attached_module_name(import_path: str) -> Tuple[str, str]:
    """
    Given import-like string 'modules.master_path.v3.routes' return ('master_path','v3')
    If can't parse, return ('', '')
    """
    parts = import_path.split(".")
    # find pattern modules.<name>.vX.
    if len(parts) >= 3 and parts[0] == "modules":
        name = parts[1]
        # try to find version part 'v\d'
        version = ""
        for p in parts[2:5]:
            if re.match(r"^v\d+$", p):
                version = p
                break
        return name, version
    return "", ""

def probe_module_endpoint(module: str, version: str) -> str:
    """
    Try to find a working endpoint for module/version by POSTing empty chat_id.
    Returns endpoint path (starting with /) or empty string.
    """
    for pattern in PROBE_PATTERNS:
        candidate = pattern.format(module=module, version=version)
        url = BACKEND_URL + candidate
        try:
            # POST a lightweight probe; backend should respond quickly
            r = requests.post(url, json={"probe": True, "chat_id": 0}, timeout=5)
            # Accept any 2xx as success
            if 200 <= r.status_code < 300:
                log("Probe OK:", candidate, "status", r.status_code)
                return candidate
            else:
                # If backend returns 404/405, try next
                log("Probe candidate", candidate, "->", r.status_code)
        except Exception as e:
            log("Probe candidate", candidate, "failed:", e)
            # continue trying
    return ""

def build_module_commands_from_backend() -> Dict[str, Tuple[str, str]]:
    """
    Query backend to discover attached modules and probe for working start endpoints.
    Returns mapping: "/module" -> (endpoint_path, description)
    """
    commands = {}
    rs = fetch_routes_summary()
    attached = rs.get("attached") or []
    if not attached:
        log("routes_summary returned no attached modules; fallback to fs-scan")
        return commands

    log("routes_summary attached modules count:", len(attached))
    for imp in attached:
        module, version = parse_attached_module_name(imp)
        if not module:
            continue
        # attempt to probe with version first
        endpoint = ""
        if version:
            endpoint = probe_module_endpoint(module, version)
        # if probe with version failed, also try without version
        if not endpoint:
            endpoint = probe_module_endpoint(module, "")
        if endpoint:
            cmd = f"/{module}"
            desc = f"{module} ({version or 'no-version'})"
            commands[cmd] = (endpoint, desc)
        else:
            log("No start endpoint found for", module, version)
    return commands

# Fallback: local fs scanning (previous behaviour)
def find_modules_commands_fs() -> Dict[str, Tuple[str, str]]:
    candidates = []
    here = os.path.abspath(os.path.dirname(__file__))
    candidates.append(os.path.join(here, "modules"))
    candidates.append(os.path.join(here, "..", "modules"))
    candidates.append(os.path.join(here, "..", "..", "modules"))
    candidates.append(os.path.join(os.getcwd(), "modules"))
    modules_dir = None
    for p in candidates:
        if os.path.isdir(p):
            modules_dir = os.path.abspath(p)
            break
    commands = {}
    if not modules_dir:
        log("FS-scan: modules folder not found in candidates", candidates)
        return commands
    log("FS-scan modules folder:", modules_dir)
    try:
        for name in sorted(os.listdir(modules_dir)):
            item = os.path.join(modules_dir, name)
            if not os.path.isdir(item):
                continue
            if name.startswith(".") or name in ("__pycache__", "tests"):
                continue
            versions = []
            for sub in os.listdir(item):
                m = re.match(r"^v(\d+)", sub)
                if m and os.path.isdir(os.path.join(item, sub)):
                    versions.append((int(m.group(1)), sub))
            if versions:
                versions.sort(reverse=True)
                version = versions[0][1]
                endpoint = f"/{name}/{version}/start"
                command = f"/{name}"
                description = f"{name} ({version})"
                commands[command] = (endpoint, description)
            else:
                endpoint = f"/{name}/start"
                command = f"/{name}"
                description = f"{name} (no version)"
                commands[command] = (endpoint, description)
    except Exception as e:
        log("Ошибка при FS сканировании modules:", e)
    return commands

# Build MODULE_COMMANDS using backend discovery first, then fs fallback
MODULE_COMMANDS = build_module_commands_from_backend()
if not MODULE_COMMANDS:
    MODULE_COMMANDS = find_modules_commands_fs()
log("Discovered module commands:", MODULE_COMMANDS)

# Legacy trainer commands removed - no longer used

# ===================== COMMAND HANDLERS =====================

def handle_start_command(chat_id: int, session: dict):
    session["mode"] = None
    session["sid"] = None
    text = (
        "Привет 🌿 Я — Tietz, твой ИИ-наставник.\n"
        "Готов провести тебя по модулям обучения.\n"
        "Выбери, с чего начнём.\n\n"
        "Доступные команды:\n"
        "/master_path — Я новичок (полный путь обучения)\n"
        "/modules — Я уже с базой (выбрать модуль)\n"
    )
    send_message(chat_id, text)

def handle_train_command(chat_id: int, session: dict):
    """Handle /train command - delegates to master_path module"""
    # /train now just redirects to master_path
    handle_module_command(chat_id, session, "/master_path")

# Legacy dialog handlers removed - use module-based approach instead

# ===================== GENERIC MODULE CALL =====================

def handle_module_command(chat_id: int, session: dict, cmd: str):
    endpoint_desc = MODULE_COMMANDS.get(cmd)
    if not endpoint_desc:
        send_message(chat_id, "Модульная команда не найдена или не подключена.")
        return
    endpoint, desc = endpoint_desc
    url = BACKEND_URL + endpoint
    log("CALL MODULE", cmd, url)
    try:
        resp = requests.post(url, json={"chat_id": chat_id}, timeout=15)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {"result": resp.text}
        msg = data.get("reply") or data.get("result") or str(data)
        if isinstance(msg, (dict, list)):
            msg = json.dumps(msg, ensure_ascii=False, indent=2)
        send_message(chat_id, msg)
    except Exception as e:
        log("Ошибка вызова модуля", cmd, e)
        send_message(chat_id, f"Ошибка запуска модуля {cmd}: {e}")

# ===================== UPDATES PROCESSING =====================

LAST_ACTIVITY_TS = time.time()

def handle_update(update: dict):
    global LAST_ACTIVITY_TS
    message = update.get("message") or {}
    if not message:
        return
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return
    text = (message.get("text") or "").strip()
    if not text:
        return
    user = message.get("from") or {}
    username = user.get("username") or f"{user.get('first_name','')} {user.get('last_name','')}".strip()
    log("UPDATE from", chat_id, "user:", username, "text:", text[:200])
    LAST_ACTIVITY_TS = time.time()
    session = get_session(chat_id)

    # commands
    if text == "/start":
        handle_start_command(chat_id, session); return
    if text == "/train":
        handle_train_command(chat_id, session); return
    if text == "/modules":
        lines = ["Доступные модули:"]
        for k, (_ep, desc) in MODULE_COMMANDS.items():
            lines.append(f"{k} — {desc}")
        send_message(chat_id, "\n".join(lines)); return

    first_word = text.split()[0]
    if first_word in MODULE_COMMANDS:
        handle_module_command(chat_id, session, first_word); return

    # No active session mode anymore - just guide user
    send_message(chat_id, "Напиши /modules чтобы увидеть модули или /train для обучения.")

# ===================== MAIN LOOP =====================

def main():
    log("✅ simple_telegram_bot started. BACKEND_URL:", BACKEND_URL)
    log("Telegram token present. Discovered module commands:", MODULE_COMMANDS)
    offset = None
    last_heartbeat = time.time()
    while True:
        try:
            resp = requests.get(BASE_URL + "/getUpdates", params={"timeout": 50, "offset": offset}, timeout=70)
            data = resp.json()
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                handle_update(upd)
        except Exception as e:
            log("Ошибка в основном цикле:", e)
            time.sleep(3)
        now = time.time()
        if now - last_heartbeat > 60:
            active_chats = len(SESSIONS)
            log(f"heartbeat: active_chats={active_chats}, last_activity_ago={int(now-LAST_ACTIVITY_TS)}s")
            last_heartbeat = now

if __name__ == "__main__":
    main()