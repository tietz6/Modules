
import json, random
from dataclasses import dataclass, asdict
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

ERROR_TYPES = [
    "too_fast","too_slow","no_greeting","weak_offer","no_questions","pressure",
    "over_talking","low_energy","no_empathy","bad_structure","weak_closing",
    "lack_confidence","irrelevant","monotone","no_value","unclear","scattered",
    "too_direct","too_friendly","too_robotic","interrupting","missing_info",
    "no_repetition","no_confirmation","bad_price_explain","no_storytelling",
    "dry_voice","fearful","aggressive","uncertain","volume_issue","rushing",
    "silence","awkward","contradiction","hesitation","too_many_words","chaotic"
]

LEVELS = ["low","medium","high"]

@dataclass
class DragonState:
    history: list
    last_error: dict
    meta: dict
    def to_dict(self): return asdict(self)

class DragonEngine:
    def __init__(self, sid:str):
        self.sid=f"dragon:{sid}"
        self.store=StateStore("salesbot.db")
        raw=self.store.get(self.sid)
        if raw:
            try:
                d=json.loads(raw)
                self.state=DragonState(**d)
            except:
                self._reset()
        else:
            self._reset()
        try: self.llm=VoicePipeline().llm
        except: self.llm=None

    def _reset(self):
        self.state = DragonState(history=[], last_error={}, meta={"round":0})
        self._save()

    def _save(self):
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))

    def snapshot(self):
        return self.state.to_dict()

    def handle(self, text:str)->dict:
        self.state.history.append({"role":"user","content":text})
        self.state.meta["round"] += 1

        # choose random error type (LLM improves quality)
        etype=random.choice(ERROR_TYPES)
        level=random.choice(LEVELS)

        advice=None
        if self.llm:
            try:
                msg=[
                  {"role":"system","content":"Ты супер‑коуч. Анализируй ошибки менеджера максимально честно."},
                  {"role":"user","content":f"Фраза менеджера: {text}. Ошибка: {etype}. Уровень: {level}."}
                ]
                advice=self.llm.chat(msg)
            except:
                advice=None

        self.state.last_error={"type":etype,"level":level,"advice":advice}
        self._save()

        return {
            "error_type": etype,
            "level": level,
            "advice": advice,
            "round": self.state.meta["round"]
        }

    def reset(self):
        self._reset()
        return {"ok":True}
