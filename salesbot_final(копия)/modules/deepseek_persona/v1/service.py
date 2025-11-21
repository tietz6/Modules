
import os, json, random
from typing import Dict, Any
from core.voice_gateway.v1 import VoicePipeline

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "data", "persona.json")

def load_persona()->Dict[str, Any]:
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_persona(role: str, text: str)->str:
    persona = load_persona()
    blocks = persona.get("templates", {})
    tone = persona.get("tone", {})
    prefix = ""
    if role == "coach":
        prefix = random.choice(blocks.get("coach_opening", ["Смотри:"]))
    elif role == "client_emotional":
        prefix = random.choice(blocks.get("client_emotional", ["Мне важно…"]))
    elif role == "client_rational":
        prefix = random.choice(blocks.get("client_rational", ["Мне нужно…"]))
    return f"{prefix} {text}"

def persona_chat(prompt: str, role: str="coach")->str:
    persona = load_persona()
    vp = VoicePipeline()
    sys = (
        "Ты говоришь от имени бренда «На Счастье»: тёплый, уверенный стиль, "
        "эмоции, искренность, уважение. Следуй правилам:\n" +
        "\n".join(persona.get("rules", []))
    )
    msg = [
        {"role": "system", "content": sys},
        {"role": "user", "content": prompt}
    ]
    try:
        base = vp.llm.chat(msg)
        return apply_persona(role, base)
    except Exception:
        return apply_persona(role, prompt)
