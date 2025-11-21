
import time
from .personas import PERSONAS
from core.voice_gateway.v1 import VoicePipeline

class ArenaEngine:
    def __init__(self, mode: str="soft"):
        self.mode = mode if mode in PERSONAS else "soft"
        self.pipeline = VoicePipeline()
        self.history = []

    def start(self):
        persona = PERSONAS[self.mode]
        self.history.append({
            "role":"system",
            "content": f"Ты клиент. Стиль: {persona['style']}. {persona['prompt']}"
        })
        return {"ok":True,"mode":self.mode}

    def ask(self, text: str):
        self.history.append({"role":"user","content":text})
        try:
            reply = self.pipeline.llm.chat(self.history)
        except Exception as e:
            reply = "Извините, сейчас не могу ответить."

        self.history.append({"role":"assistant","content":reply})

        metrics = self._score(text, reply)
        return {"ok":True,"reply":reply,"metrics":metrics}

    def _score(self, user_text, reply):
        # naive scoring model
        tempo = 1 if len(user_text) < 120 else 0
        empathy = 1 if any(x in reply.lower() for x in ["понимаю","сочувствую","давайте вместе"]) else 0
        clarity = 1 if len(reply.split())>3 else 0
        return {"tempo":tempo,"empathy":empathy,"clarity":clarity}

    def reset(self):
        self.history=[]
        return {"ok":True}
