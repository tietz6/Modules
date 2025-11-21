
from dataclasses import dataclass, asdict
from typing import Dict, Any
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

STAGES = ["greeting","qualification","support","offer","demo","final","done"]

@dataclass
class MPState:
    stage: str
    history: list
    metadata: dict

    def to_dict(self):
        return asdict(self)

class MasterPath:
    def __init__(self, session_id: str):
        self.sid = f"mp:{session_id}"
        self.store = StateStore("salesbot.db")
        raw = self.store.get(self.sid)
        if raw:
            try:
                import json
                d = json.loads(raw)
                self.state = MPState(stage=d.get("stage","greeting"),
                                     history=d.get("history",[]),
                                     metadata=d.get("metadata",{}))
            except Exception:
                self._reset()
        else:
            self._reset()
        try:
            self.llm = VoicePipeline().llm
        except Exception:
            self.llm = None

    def _reset(self):
        self.state = MPState(stage="greeting", history=[], metadata={})
        self._save()

    def _save(self):
        import json
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))

    def snapshot(self)->dict:
        return self.state.to_dict()

    def advance(self)->str:
        idx = STAGES.index(self.state.stage)
        if idx < len(STAGES)-1:
            self.state.stage = STAGES[idx+1]
            self._save()
        return self.state.stage

    def handle(self, text: str)->dict:
        self.state.history.append({"role":"user","content":text})
        suggestion = None
        if self.llm:
            try:
                msg = [
                    {"role":"system","content":f"Ты коуч. Текущий этап: {self.state.stage}."},
                    {"role":"user","content": text}
                ]
                suggestion = self.llm.chat(msg)
            except Exception:
                suggestion = None

        reply = {
            "stage": self.state.stage,
            "coach_suggestion": suggestion
        }

        score = 0
        if self.state.stage == "greeting" and any(w in text.lower() for w in ["привет","здравствуйте","добрый"]):
            score += 1
        if self.state.stage == "qualification" and "?" in text:
            score += 1
        reply["score"] = score

        self.advance()
        self._save()
        return reply

    def reset(self):
        self._reset()
        return {"ok": True}
