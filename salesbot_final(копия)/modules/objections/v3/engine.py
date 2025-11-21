
import random, json
from dataclasses import dataclass, asdict
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

OBJECTION_TYPES = [
    "price","trust","hurry","think","ask_spouse","scam_fear",
    "too_expensive","not_needed","later","competitor"
]

PERSONAS = {
    "stranger":"Говори коротко. Клиент холодный.",
    "calm":"Спокойный клиент, открыт к диалогу.",
    "aggressive":"Грубый стиль, давит.",
    "funny":"С юмором отвечает."
}

@dataclass
class OBJState:
    persona: str
    objection_type: str
    history: list

    def to_dict(self):
        return asdict(self)

class ObjectionEngine:
    def __init__(self, sid: str):
        self.sid=f"obj:{sid}"
        self.store=StateStore("salesbot.db")
        raw=self.store.get(self.sid)
        if raw:
            try:
                d=json.loads(raw)
                self.state=OBJState(**d)
            except:
                self._reset()
        else:
            self._reset()
        try:
            self.llm=VoicePipeline().llm
        except:
            self.llm=None

    def _reset(self):
        persona=random.choice(list(PERSONAS.keys()))
        otype=random.choice(OBJECTION_TYPES)
        self.state=OBJState(persona=persona, objection_type=otype, history=[])
        self._save()

    def _save(self):
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))

    def snapshot(self):
        return self.state.to_dict()

    def handle(self, text: str)->dict:
        self.state.history.append({"role":"user","content":text})
        persona_desc=PERSONAS[self.state.persona]
        ot=self.state.objection_type

        suggestion=None
        if self.llm:
            try:
                msg=[
                  {"role":"system","content":f"Ты клиент. Тип возражения: {ot}. {persona_desc}"},
                  {"role":"user","content":text}
                ]
                suggestion=self.llm.chat(msg)
            except:
                suggestion=None

        # simple scoring
        score=0
        if any(w in text.lower() for w in ["понимаю","согласен","давайте","могу"]):
            score+=1
        if len(text)>20:
            score+=1

        self._save()

        return {
            "persona": self.state.persona,
            "objection_type": ot,
            "client_reply": suggestion,
            "score": score
        }

    def reset(self):
        self._reset()
        return {"ok":True}
