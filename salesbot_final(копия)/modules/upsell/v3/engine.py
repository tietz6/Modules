
import json, random
from dataclasses import dataclass, asdict
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

MODES = ["soft","normal","aggressive"]
PACKAGES = {
    "basic": "Песня + обработка",
    "premium": "Песня + видео открытка",
    "gold": "Песня + премиум история + видео"
}

@dataclass
class USState:
    mode: str
    package: str
    history: list

    def to_dict(self):
        return asdict(self)

class UpsellEngine:
    def __init__(self, sid:str):
        self.sid=f"us:{sid}"
        self.store=StateStore("salesbot.db")
        raw=self.store.get(self.sid)
        if raw:
            try:
                d=json.loads(raw)
                self.state=USState(**d)
            except:
                self._reset()
        else:
            self._reset()
        try:
            self.llm=VoicePipeline().llm
        except:
            self.llm=None

    def _reset(self):
        mode=random.choice(MODES)
        pkg=random.choice(list(PACKAGES.keys()))
        self.state=USState(mode=mode, package=pkg, history=[])
        self._save()

    def _save(self):
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))

    def snapshot(self):
        return self.state.to_dict()

    def handle(self, text:str)->dict:
        self.state.history.append({"role":"user","content":text})
        pkg_desc=PACKAGES[self.state.package]
        mode=self.state.mode

        suggestion=None
        if self.llm:
            try:
                msg=[
                  {"role":"system","content":f"Ты клиент. Сценарий допродажи: {mode}. Пакет предлагается: {pkg_desc}."},
                  {"role":"user","content":text}
                ]
                suggestion=self.llm.chat(msg)
            except:
                suggestion=None

        score=0
        if any(w in text.lower() for w in ["получите","давайте","предлагаю","выгода"]):
            score+=1
        if len(text)>25:
            score+=1

        self._save()

        return {
            "mode":mode,
            "package":self.state.package,
            "client_reply":suggestion,
            "score":score
        }

    def reset(self):
        self._reset()
        return {"ok":True}
