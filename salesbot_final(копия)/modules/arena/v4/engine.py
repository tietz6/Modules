
import json, random
from dataclasses import dataclass, asdict
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

EMOTIONS = ["calm","neutral","annoyed","angry","excited"]
CLIENT_TYPES = [
  "silent","talkative","rude","polite","busy","rich","poor","jokester","logic","emotional",
  "skeptic","warm","cold","doubtful","dominant","passive","detail","fast","slow","expert"
]

DIFFICULTY = ["L1","L2","L3"]

@dataclass
class ArenaState:
    ctype: str
    emotion: str
    difficulty: str
    history: list
    meta: dict
    def to_dict(self): return asdict(self)

class ArenaEngine:
    def __init__(self, sid: str):
        self.sid=f"arena:{sid}"
        self.store=StateStore("salesbot.db")
        raw=self.store.get(self.sid)
        if raw:
            try:
                d=json.loads(raw)
                self.state=ArenaState(**d)
            except:
                self._reset()
        else:
            self._reset()

        try: self.llm=VoicePipeline().llm
        except: self.llm=None

    def _reset(self):
        self.state = ArenaState(
            ctype=random.choice(CLIENT_TYPES),
            emotion=random.choice(EMOTIONS),
            difficulty=random.choice(DIFFICULTY),
            history=[],
            meta={"round":0}
        )
        self._save()

    def _save(self):
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))

    def snapshot(self):
        return self.state.to_dict()

    def handle(self, text: str)->dict:
        self.state.history.append({"role":"user","content":text})
        self.state.meta["round"] += 1

        persona_desc=f"Тип: {self.state.ctype}. Эмоция: {self.state.emotion}. Сложность: {self.state.difficulty}."
        suggestion=None
        if self.llm:
            try:
                msg=[
                  {"role":"system","content":f"Ты клиент. {persona_desc} Реагируй естественно."},
                  {"role":"user","content":text}
                ]
                suggestion=self.llm.chat(msg)
            except:
                suggestion=None

        # emotion shift
        if any(w in text.lower() for w in ["извиняюсь","понимаю","давайте","готов"]):
            self.state.emotion="calm"
        elif "?" in text:
            self.state.emotion="neutral"
        else:
            if self.state.difficulty=="L3":
                self.state.emotion=random.choice(["annoyed","angry","neutral"])

        # scoring
        score=0
        if len(text)>20: score+=1
        if any(w in text.lower() for w in ["согласен","понимаю","давайте"]): score+=1

        self._save()

        return {
            "ctype":self.state.ctype,
            "emotion":self.state.emotion,
            "difficulty":self.state.difficulty,
            "client_reply":suggestion,
            "score":score
        }

    def reset(self):
        self._reset()
        return {"ok":True}
